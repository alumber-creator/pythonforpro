---
title: "Контекстные менеджеры: with и управление ресурсами"
order: 4
tags:
  - контекстные-менеджеры
  - with
  - ресурсы
  - RAII
prerequisites: "Функции, классы"
objective: "Освоить контекстные менеджеры для безопасного управления ресурсами"
---

# Контекстные менеджеры: `with` и управление ресурсами

## 🎯 Цель урока

Научиться использовать `with` для гарантированного освобождения ресурсов, создавать собственные контекстные менеджеры и освоить модуль `contextlib` для продвинутых сценариев.

## 📋 Предпосылки

Вы умеете определять классы и функции в Python, работали с файлами через `open()` и понимаете важность закрытия ресурсов.

---

## Введение

Управление ресурсами — одна из немногих областей, где ошибка может стоить очень дорого: утечка файловых дескрипторов, незакрытые соединения с базой данных, блокировки, которые никогда не снимаются. Python решает эту проблему элегантно: контекстные менеджеры и оператор `with` гарантируют, что ресурс будет освобождён, даже если внутри блока произошло исключение.

В отличие от C++ с его RAII (Resource Acquisition Is Initialization), где освобождение привязано к времени жизни объекта, Python делает управление ресурсами явным и читаемым. В отличие от Java `try-with-resources`, Python-контекстные менеджеры более гибкие и компонуемые.

---

## Основная часть

### 1. Оператор `with` — основы

Самый известный пример — работа с файлами:

**❌ Без `with` (ненадёжно):**

```python
f = open("data.txt")
try:
    content = f.read()
finally:
    f.close()  # Закроется ли файл, если open() упал ДО try?
```

**✅ С `with` (надёжно и лаконично):**

```python
with open("data.txt") as f:
    content = f.read()
# Здесь файл УЖЕ закрыт, даже если read() вызвал исключение
```

Что происходит под капотом:

```python
# with open("data.txt") as f:
#     content = f.read()
#
# Эквивалентно:
manager = open("data.txt")
f = manager.__enter__()
try:
    content = f.read()
finally:
    manager.__exit__(exc_type, exc_val, exc_tb)
```

Ключевое: `__exit__` вызывается ВСЕГДА — и при нормальном завершении, и при исключении. Он получает информацию об исключении (`None, None, None` если исключения не было).

### 2. Встроенные контекстные менеджеры

Python предоставляет множество контекстных менеджеров в стандартной библиотеке:

#### Файлы

```python
with open("data.txt") as f:
    content = f.read()

# Открытие нескольких файлов
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read().upper())
```

#### Блокировки потоков

```python
import threading

lock = threading.Lock()

# ❌ Риск: исключение между acquire и release
lock.acquire()
try:
    # критическая секция
    pass
finally:
    lock.release()

# ✅ Идиоматично
with lock:
    # критическая секция — блокировка гарантированно снимется
    pass
```

#### Временные изменения

```python
import decimal

# Временно меняем контекст вычислений decimal
with decimal.localcontext() as ctx:
    ctx.prec = 50  # 50 знаков после запятой
    result = decimal.Decimal(1) / decimal.Decimal(7)
# Здесь точность восстановлена
```

#### Транзакции базы данных

```python
import sqlite3

conn = sqlite3.connect("app.db")
with conn:  # Автоматический commit или rollback
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
# Если исключение — rollback, иначе commit
```

### 3. Создание собственных контекстных менеджеров

#### Способ 1: Класс с `__enter__` и `__exit__`

```python
class ManagedFile:
    """Контекстный менеджер для файла с автоматическим закрытием."""

    def __init__(self, filename: str, mode: str = "r"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # Возвращаем False — не подавляем исключения
        return False


with ManagedFile("data.txt") as f:
    content = f.read()
```

#### Способ 2: `contextlib.contextmanager` — декоратор

Более элегантный способ — использовать генератор с одним `yield`:

```python
from contextlib import contextmanager


@contextmanager
def managed_file(filename: str, mode: str = "r"):
    """То же самое, но в 4 строки вместо 15."""
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()


with managed_file("data.txt") as f:
    content = f.read()
```

Всё, что до `yield` — это `__enter__`. Всё, что после `yield` — это `__exit__`. Если внутри `with` произошло исключение, оно пробрасывается в точку `yield`, и блок `finally` гарантированно выполняется.

#### Пример: таймер выполнения

```python
import time
from contextlib import contextmanager


@contextmanager
def timer(description: str = "Код"):
    """Замеряет время выполнения блока кода."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{description} выполнился за {elapsed:.3f} секунд")


with timer("Вычисление факториала"):
    result = 1
    for i in range(1, 100_000):
        result *= i
# Выведет: Вычисление факториала выполнился за X.XXX секунд
```

#### Пример: временная смена директории

```python
import os
from contextlib import contextmanager


@contextmanager
def change_dir(path: str):
    """Временно меняет рабочую директорию."""
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


print(os.getcwd())  # /home/user
with change_dir("/tmp"):
    print(os.getcwd())  # /tmp
    # ... работаем во временной директории ...
print(os.getcwd())  # /home/user — восстановлено
```

### 4. Модуль `contextlib` — инструменты для профессионалов

#### `closing` — для объектов с `.close()` но без `__enter__`

```python
from contextlib import closing
from urllib.request import urlopen

# urlopen возвращает объект с .close(), но без поддержки with
with closing(urlopen("https://python.org")) as page:
    content = page.read()
```

#### `suppress` — игнорирование указанных исключений

```python
from contextlib import suppress

# ❌ Громоздко
try:
    os.remove("temp.txt")
except FileNotFoundError:
    pass

# ✅ Элегантно
with suppress(FileNotFoundError):
    os.remove("temp.txt")
```

#### `redirect_stdout` — перехват вывода

```python
import io
from contextlib import redirect_stdout

f = io.StringIO()
with redirect_stdout(f):
    print("Hello, world!")
    print("Это ушло в буфер, а не на экран")

output = f.getvalue()
print(output)  # Hello, world!\nЭто ушло в буфер, а не на экран\n
```

#### `ExitStack` — динамическое управление контекстными менеджерами

`ExitStack` позволяет управлять набором контекстных менеджеров, которые создаются динамически во время выполнения:

```python
from contextlib import ExitStack


def process_files(filenames: list[str]):
    """Открывает несколько файлов, количество которых известно только в runtime."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in filenames]
        # Все файлы будут закрыты при выходе из with, даже если
        # открытие одного из них упало с исключением
        for f in files:
            print(f.read())
```

`ExitStack` также полезен для управления ресурсами в `__init__`:

```python
class ResourceManager:
    def __init__(self, paths: list[str]):
        self._stack = ExitStack()
        self._files = []
        for path in paths:
            self._files.append(self._stack.enter_context(open(path)))

    def close(self):
        self._stack.close()

    # Или сделать сам класс контекстным менеджером:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._stack.close()
```

### 5. Обработка исключений в `__exit__`

`__exit__` может подавить исключение, вернув `True`:

```python
class SuppressKeyError:
    """Контекстный менеджер, подавляющий KeyError."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is KeyError:
            print(f"Подавлен KeyError: {exc_val}")
            return True  # Подавляем исключение
        return False  # Пробрасываем другие исключения


data = {"a": 1}
with SuppressKeyError():
    print(data["a"])  # 1
    print(data["b"])  # KeyError подавлен
print("Продолжаем выполнение!")
```

### 6. Вложенные и составные контекстные менеджеры

```python
# Несколько менеджеров в одном with
with (
    open("input.txt") as infile,
    open("output.txt", "w") as outfile,
    threading.Lock() as lock,
):
    with lock:
        outfile.write(infile.read().upper())
```

Синтаксис с круглыми скобками и запятыми доступен с Python 3.10. Для более старых версий:

```python
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    ...
```

### 7. Асинхронные контекстные менеджеры

С Python 3.5+ доступны асинхронные контекстные менеджеры для работы с `async`/`await`:

```python
import asyncio


class AsyncConnection:
    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def connect(self):
        await asyncio.sleep(0.1)  # Имитация подключения
        print("Подключено")

    async def disconnect(self):
        await asyncio.sleep(0.1)  # Имитация отключения
        print("Отключено")


async def main():
    async with AsyncConnection() as conn:
        print("Работаем с соединением")
    # Здесь соединение гарантированно закрыто
```

### 8. Сравнение с другими языками

#### Java try-with-resources

Java 7+ предлагает try-with-resources для объектов, реализующих `AutoCloseable`:

```java
// Java — try-with-resources
try (BufferedReader br = new BufferedReader(new FileReader("data.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        System.out.println(line);
    }
} // Автоматический close()
```

```python
# Python — более лаконичный синтаксис
with open("data.txt") as f:
    for line in f:
        print(line, end="")
```

Отличия Python:
- Не требует реализации интерфейса — достаточно duck typing (`__enter__`/`__exit__`)
- `with` — это утверждение, а не блок с объявлением переменных
- `contextlib` даёт декларативные способы создания менеджеров (в Java нужен отдельный класс)

#### C++ RAII

C++ привязывает освобождение ресурса к деструктору:

```cpp
// C++ — RAII: деструктор автоматически вызывается при выходе из области видимости
{
    std::ifstream file("data.txt");
    std::string line;
    while (std::getline(file, line)) {
        std::cout << line << std::endl;
    }
} // Деструктор file закрывает файл
```

```python
# Python — явный with подчёркивает намерение
with open("data.txt") as f:
    for line in f:
        print(line, end="")
```

Философское различие:
- C++: ресурс привязан к времени жизни объекта (неявно)
- Python: ресурс явно привязан к блоку `with` (читатель видит, где ресурс «жив»)

Python-подход более читаем: вы сразу видите границы использования ресурса, не гадая о деструкторах.

#### C# using

C# `using` очень похож на Python `with`:

```csharp
// C# using
using (var file = new StreamReader("data.txt"))
{
    string content = file.ReadToEnd();
}
```

```python
# Python with — концептуально то же самое
with open("data.txt") as f:
    content = f.read()
```

И Python, и C# делают управление ресурсами явным и читаемым. Python выигрывает в гибкости благодаря `contextlib`.

#### JavaScript

JavaScript не имеет прямого аналога. Используется `try/finally` или `using` (Stage 3, TC39 proposal):

```javascript
// JavaScript — try/finally (ручное управление)
const f = fs.openSync("data.txt", "r");
try {
    const content = fs.readFileSync(f);
} finally {
    fs.closeSync(f);
}
```

```python
# Python — with всё делает автоматически
with open("data.txt") as f:
    content = f.read()
```

---

## Практическое задание

### Задание 1: Контекстный менеджер для бенчмаркинга

Напишите контекстный менеджер `Benchmark`, который:
- Замеряет время выполнения блока кода
- Собирает статистику (количество вызовов, общее время, среднее, минимум, максимум)
- Имеет метод `report()` для вывода статистики

```python
class Benchmark:
    """Контекстный менеджер для сбора статистики выполнения."""

    def __init__(self, name: str = "Код"):
        self.name = name
        self._total_time = 0.0
        self._calls = 0
        self._min_time = float("inf")
        self._max_time = 0.0

    def __enter__(self):
        # Ваш код
        pass

    def __exit__(self, *args):
        # Ваш код
        pass

    def report(self):
        """Выводит статистику выполнения."""
        # Ваш код
        pass


# Использование:
bench = Benchmark("Моя операция")
for _ in range(5):
    with bench:
        # Какая-то работа
        sum(range(1_000_000))
bench.report()
```

### Задание 2: Временная переменная окружения

Напишите контекстный менеджер `temp_env` (используя `@contextmanager`), который временно устанавливает переменную окружения и восстанавливает её исходное значение (или удаляет, если её не было).

```python
from contextlib import contextmanager
import os


@contextmanager
def temp_env(key: str, value: str):
    """Временно устанавливает переменную окружения."""
    # Ваш код
    pass


# Использование:
with temp_env("MY_VAR", "hello"):
    print(os.environ.get("MY_VAR"))  # hello
print(os.environ.get("MY_VAR"))  # None (или исходное значение)
```

### Задание 3: Транзакционный контекст

Реализуйте контекстный менеджер `Transaction` для работы со списком как с транзакционной структурой данных:
- При входе сохраняет копию списка
- При выходе без исключения — сохраняет изменения
- При выходе с исключением — откатывает список к исходному состоянию

```python
class Transaction:
    """Транзакционный контекст для списка."""

    def __init__(self, target: list):
        self.target = target
        self._backup = None

    def __enter__(self):
        # Ваш код
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ваш код
        pass


# Использование:
data = [1, 2, 3]
print(data)  # [1, 2, 3]

try:
    with Transaction(data):
        data.append(4)
        data[0] = 99
        raise ValueError("Что-то пошло не так")
except ValueError:
    pass

print(data)  # [1, 2, 3] — изменения откатились
```

---

## Дополнительные материалы

### Документация

- [PEP 343 — The "with" Statement](https://peps.python.org/pep-0343/)
- [contextlib documentation](https://docs.python.org/3/library/contextlib.html)
- [Python Reference: The with statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 15 (контекстные менеджеры).
- **«Effective Python»**, Бретт Слаткин — совет 43: «Рассмотрите contextlib и with для повторно используемых try/finally».

### Статьи

- [Real Python: Context Managers and Python's with Statement](https://realpython.com/python-with-statement/)
- [Python Patterns: Context Managers](https://python-patterns.guide/)

### Видео

- **«Context Managers: The Amazing, the Awful, and the Ugly»**, Реймонд Хеттингер — доклад о продвинутых техниках.