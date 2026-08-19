---
title: "Генераторы и итераторы: ленивые вычисления в Python"
order: 3
tags:
  - генераторы
  - итераторы
  - yield
  - ленивые-вычисления
prerequisites: "Функции, comprehensions"
objective: "Освоить создание и использование генераторов для эффективной работы с последовательностями"
---

# Генераторы и итераторы: ленивые вычисления в Python

## 🎯 Цель урока

Освоить протокол итераторов, функции-генераторы с `yield`, генераторные выражения и модуль `itertools` для создания эффективных, ленивых конвейеров обработки данных.

## 📋 Предпосылки

Вы понимаете работу циклов `for`, знаете, что такое итерация по спискам и словарям. Знакомы с comprehensions (урок 2) и умеете определять функции.

---

## Введение

Одна из самых мощных концепций Python — ленивые вычисления. Вместо того чтобы загружать все данные в память, мы описываем *правило* получения следующего элемента. Это позволяет обрабатывать файлы размером в терабайты, не загружая их целиком в RAM, и строить бесконечные последовательности, которые вычисляются только по мере необходимости.

Генераторы — это не просто оптимизация памяти. Это способ мышления: вы описываете поток данных, а не структуру данных. В этом уроке мы пройдём путь от протокола итераторов до сложных конвейеров из генераторов.

---

## Основная часть

### 1. Протокол итератора — как работает `for`

Любой объект, по которому можно итерироваться, реализует протокол итератора:

```python
class MyIterator:
    def __iter__(self):
        """Возвращает объект итератора (обычно self)."""
        return self

    def __next__(self):
        """Возвращает следующий элемент или вызывает StopIteration."""
        ...
```

Когда вы пишете `for item in container:`, Python делает следующее:

```python
# Во что for превращается внутри
iterator = iter(container)      # вызывает container.__iter__()
while True:
    try:
        item = next(iterator)  # вызывает iterator.__next__()
    except StopIteration:
        break
    # тело цикла
```

Понимание этого механизма — ключ к созданию собственных итераторов и генераторов.

#### Пример: самодельный итератор

```python
class Countdown:
    """Обратный отсчёт от n до 1."""

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


for num in Countdown(5):
    print(num)
# 5
# 4
# 3
# 2
# 1
```

Это работает, но 6 строк кода ради такого простого поведения — многовато. И здесь вступают генераторы.

### 2. Функции-генераторы и `yield`

Генератор — это функция, которая использует `yield` вместо `return`. Каждый вызов `yield` приостанавливает функцию, сохраняя её состояние. При следующем вызове `next()` выполнение продолжается с той же точки.

```python
def countdown(start: int):
    """Тот же Countdown, но как генератор — 2 строки вместо 12."""
    while start > 0:
        yield start
        start -= 1


for num in countdown(5):
    print(num)
```

Что здесь происходит:
1. Вызов `countdown(5)` **не выполняет тело функции**. Он возвращает generator object.
2. Первый `next()` начинает выполнение до первого `yield`.
3. `yield start` возвращает `start` и приостанавливает функцию.
4. Следующий `next()` продолжает с `start -= 1` и идёт до следующего `yield`.
5. Когда `while` заканчивается, функция завершается, и автоматически вызывается `StopIteration`.

#### Генератор — это итератор

```python
gen = countdown(3)
print(iter(gen) is gen)  # True — генератор является собственным итератором
print(next(gen))         # 3
print(next(gen))         # 2
print(next(gen))         # 1
print(next(gen))         # StopIteration
```

### 3. Генераторные выражения

Генераторное выражение — это синтаксический сахар для создания генератора без отдельной функции:

```python
# Функция-генератор
def squares(n):
    for i in range(n):
        yield i ** 2

# Генераторное выражение — то же самое, но компактнее
squares_gen = (i ** 2 for i in range(n))
```

Генераторные выражения идеальны для передачи в функции, ожидающие итератор:

```python
# Сумма квадратов — без создания промежуточного списка
total = sum(x ** 2 for x in range(1_000_000))

# Поиск первого подходящего элемента
first = next(x for x in data if x > 100)
```

### 4. `yield from` — делегирование подгенераторам

С Python 3.3 появился `yield from` — синтаксис для делегирования части итерации другому генератору.

**❌ Без `yield from`:**

```python
def flatten(nested):
    for sublist in nested:
        for item in sublist:
            yield item
```

**✅ С `yield from`:**

```python
def flatten(nested):
    for sublist in nested:
        yield from sublist
```

`yield from` делает больше, чем просто цикл. Он устанавливает двусторонний канал между вызывающим кодом и подгенератором — через него можно отправлять значения (`send()`) и исключения (`throw()`).

#### Рекурсивная распаковка вложенных списков

```python
def deep_flatten(nested):
    """Рекурсивно разворачивает вложенную структуру любой глубины."""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from deep_flatten(item)
        else:
            yield item


messy = [1, [2, [3, 4], 5], 6, [7, [8, [9]]]]
flat = list(deep_flatten(messy))
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 5. Конвейеры из генераторов

Генераторы можно объединять в конвейеры — каждый этап обрабатывает данные лениво, по одному элементу за раз. Это похоже на Unix-пайпы (`cat file | grep | sort | uniq`).

```python
def read_log_lines(path: str):
    """Читает файл построчно, убирая пробелы."""
    with open(path) as f:
        for line in f:
            yield line.strip()


def filter_errors(lines):
    """Пропускает только строки с ERROR."""
    for line in lines:
        if "ERROR" in line:
            yield line


def extract_timestamps(lines):
    """Извлекает временную метку из строки."""
    for line in lines:
        timestamp = line[:23]  # Первые 23 символа — дата и время
        yield timestamp


# Конвейер: читаем -> фильтруем -> извлекаем
log_path = "/var/log/application.log"
for ts in extract_timestamps(filter_errors(read_log_lines(log_path))):
    print(ts)
```

В любой момент времени в памяти находится только одна строка файла. Файл может быть размером 10 GB — это не имеет значения.

Конвейер можно записать более элегантно с генераторными выражениями:

```python
lines = (line.strip() for line in open("/var/log/application.log"))
errors = (line for line in lines if "ERROR" in line)
timestamps = (line[:23] for line in errors)

for ts in timestamps:
    print(ts)
```

### 6. Модуль `itertools` — строительные блоки для итераторов

`itertools` — это стандартная библиотека функций-генераторов, которые комбинируются как кирпичики. Вот самые важные:

#### Бесконечные итераторы

```python
from itertools import count, cycle, repeat

# count(start=0, step=1) — бесконечный счётчик
for i, val in zip(count(), data):
    print(i, val)  # Нумеруем элементы (альтернатива enumerate)

# cycle(iterable) — бесконечно повторяет итератор
lights = cycle(["red", "yellow", "green"])
for _ in range(10):
    print(next(lights))  # red, yellow, green, red, ...

# repeat(object, times=None) — повторяет объект
zeros = repeat(0, 5)
list(zeros)  # [0, 0, 0, 0, 0]
```

#### Комбинаторные итераторы

```python
from itertools import product, permutations, combinations, combinations_with_replacement

# product — декартово произведение
for x, y in product("AB", "12"):
    print(x, y)  # A1, A2, B1, B2

# permutations — перестановки
list(permutations("ABC", 2))
# [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# combinations — сочетания (порядок не важен)
list(combinations("ABC", 2))
# [('A', 'B'), ('A', 'C'), ('B', 'C')]

# combinations_with_replacement — сочетания с повторениями
list(combinations_with_replacement("AB", 2))
# [('A', 'A'), ('A', 'B'), ('B', 'B')]
```

#### Итераторы для объединения и фильтрации

```python
from itertools import chain, compress, dropwhile, takewhile, filterfalse

# chain — объединяет несколько итераторов в один
all_items = list(chain([1, 2], [3, 4], [5, 6]))
# [1, 2, 3, 4, 5, 6]

# compress — фильтрует по маске
data = ["a", "b", "c", "d"]
mask = [True, False, True, False]
list(compress(data, mask))  # ['a', 'c']

# takewhile/dropwhile — берут/пропускают пока условие истинно
list(takewhile(lambda x: x < 5, [1, 2, 3, 4, 5, 1, 2]))
# [1, 2, 3, 4] — остановился на 5
list(dropwhile(lambda x: x < 5, [1, 2, 3, 4, 5, 1, 2]))
# [5, 1, 2] — пропустил пока < 5, потом всё берёт
```

#### Группировка

```python
from itertools import groupby

# groupby — группирует подряд идущие элементы с одинаковым ключом
data = [
    ("food", 100),
    ("food", 50),
    ("transport", 200),
    ("food", 150),  # Не сгруппируется с предыдущими food!
]

# Важно: данные должны быть отсортированы по ключу
data_sorted = sorted(data, key=lambda x: x[0])
for category, items in groupby(data_sorted, key=lambda x: x[0]):
    amounts = [amount for _, amount in items]
    print(f"{category}: {amounts}, total={sum(amounts)}")
# food: [100, 50, 150], total=300
# transport: [200], total=200
```

### 7. Практический пример: обработка большого CSV

```python
import csv
from itertools import islice


def read_csv_lazy(path: str):
    """Лениво читает CSV-файл, возвращая словари по одному."""
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        yield from reader


def filter_by_column(rows, column: str, predicate):
    """Фильтрует строки по значению в колонке."""
    for row in rows:
        if predicate(row.get(column)):
            yield row


def select_columns(rows, *columns: str):
    """Оставляет только указанные колонки."""
    for row in rows:
        yield {col: row[col] for col in columns if col in row}


# Конвейер для обработки большого файла
path = "huge_dataset.csv"
rows = read_csv_lazy(path)
rows = filter_by_column(rows, "status", lambda s: s == "active")
rows = select_columns(rows, "id", "name", "email")

# Берём первые 100 результатов
first_hundred = list(islice(rows, 100))
```

### 8. Сравнение с другими языками

#### Java Iterator

Java требует реализации интерфейса `Iterator<T>` с методами `hasNext()` и `next()`:

```java
// Java — многословный подход с явным интерфейсом
class Countdown implements Iterator<Integer> {
    private int current;

    public Countdown(int start) {
        this.current = start;
    }

    @Override
    public boolean hasNext() {
        return current > 0;
    }

    @Override
    public Integer next() {
        if (!hasNext()) throw new NoSuchElementException();
        return current--;
    }
}
```

```python
# Python — функция-генератор, 3 строки
def countdown(start):
    while start > 0:
        yield start
        start -= 1
```

Python не требует:
- Объявления интерфейса
- Метода `hasNext()` (Python использует исключение `StopIteration`)
- Дженериков (в Python динамическая типизация)
- Проверки состояния в `next()` (алгоритм сам определяет конец)

#### C++ итераторы

C++ итераторы — мощный, но сложный механизм с категориями (input, output, forward, bidirectional, random access) и необходимостью определять `begin()`, `end()`, `operator++`, `operator*`, `operator!=`:

```cpp
// C++ — требуется определить несколько операторов
class Countdown {
    int current;
public:
    explicit Countdown(int start) : current(start) {}

    class iterator {
        int value;
    public:
        explicit iterator(int v) : value(v) {}
        int operator*() const { return value; }
        iterator& operator++() { --value; return *this; }
        bool operator!=(const iterator& other) const {
            return value != other.value;
        }
    };

    iterator begin() { return iterator(current); }
    iterator end() { return iterator(0); }
};
```

```python
# Python — yield делает всё это автоматически
def countdown(start):
    while start > 0:
        yield start
        start -= 1
```

#### JavaScript генераторы

JavaScript также имеет генераторы с `function*` и `yield`, синтаксис близок к Python:

```javascript
// JavaScript — похожий синтаксис
function* countdown(start) {
    while (start > 0) {
        yield start--;
    }
}
```

Ключевое отличие: Python-генераторы интегрированы во всю экосистему — `for`, comprehensions, `itertools`, стандартная библиотека. В JavaScript генераторы используются реже, а экосистема предпочитает async/await и промисы.

### 9. Продвинутые техники: `send()`, `throw()`, `close()`

Генераторы в Python — это не просто источники данных. Они поддерживают двустороннюю коммуникацию:

```python
def accumulator():
    """Генератор, который принимает значения через send()."""
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value


acc = accumulator()
next(acc)          # Запускаем генератор (доходит до первого yield)
print(acc.send(10))  # 10 — отправляем 10, получаем total
print(acc.send(20))  # 30
print(acc.send(5))   # 35
acc.close()          # Закрываем генератор
```

Это позволяет использовать генераторы как корутины (хотя с Python 3.5+ для этого лучше подходят `async`/`await`).

---

## Практическое задание

### Задание 1: Напишите генератор

Напишите генератор `fibonacci(n)`, который лениво генерирует первые `n` чисел Фибоначчи. Затем используйте его для вычисления суммы первых 100 чисел Фибоначчи.

```python
def fibonacci(n: int):
    """Генерирует первые n чисел Фибоначчи."""
    # Ваш код здесь
    pass


# Ожидаемое поведение:
list(fibonacci(10))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Задание 2: Конвейер для логов

Напишите три функции-генератора, которые образуют конвейер для обработки логов:

1. `read_logs(path)` — читает файл построчно, отдаёт stripped строки
2. `filter_level(lines, level)` — пропускает только строки с указанным уровнем (INFO, WARN, ERROR)
3. `extract_message(lines)` — извлекает текст сообщения (всё после двоеточия после уровня)

Пример строки лога: `2024-01-01 10:00:00 ERROR: Connection timeout`

```python
def read_logs(path: str):
    # Ваш код
    pass


def filter_level(lines, level: str):
    # Ваш код
    pass


def extract_message(lines):
    # Ваш код
    pass


# Использование:
for msg in extract_message(filter_level(read_logs("app.log"), "ERROR")):
    print(msg)
```

### Задание 3: `itertools` на практике

Решите следующие задачи, используя ТОЛЬКО функции из `itertools`:

1. Объединить 3 списка в один итератор (без создания нового списка)
2. Создать бесконечный итератор, чередующий 1 и -1: `1, -1, 1, -1, ...`
3. Из списка `[1, 2, 3, 4, 5, 6, 7, 8]` сгруппировать элементы по чётности (чётные/нечётные)

---

## Дополнительные материалы

### Документация

- [Python Glossary: Iterator](https://docs.python.org/3/glossary.html#term-iterator)
- [Python Glossary: Generator](https://docs.python.org/3/glossary.html#term-generator)
- [PEP 255 — Simple Generators](https://peps.python.org/pep-0255/)
- [PEP 342 — Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)
- [PEP 380 — Syntax for Delegating to a Subgenerator (`yield from`)](https://peps.python.org/pep-0380/)
- [itertools documentation](https://docs.python.org/3/library/itertools.html)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 14 (итераторы и генераторы), глава 16 (корутины).
- **«Effective Python»**, Бретт Слаткин — совет 16: «Используйте генераторы вместо возврата списков», совет 17: «Будьте осторожны при итерации по аргументам».

### Статьи

- [Real Python: Introduction to Python Generators](https://realpython.com/introduction-to-python-generators/)
- [Python Patterns: Generators](https://python-patterns.guide/)

### Видео

- **«Generator Tricks for Systems Programmers»**, Дэвид Бизли (PyCon 2008) — классический доклад о конвейерах из генераторов.