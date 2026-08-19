---
title: "async/await: корутины и асинхронные функции"
order: 2
tags: ["async", "await", "корутины", "asyncio"]
prerequisites: "Урок 1, генераторы"
objective: "Освоить синтаксис async/await и понять, как работают корутины"
---

# async/await: корутины и асинхронные функции

## Введение

`async` и `await` — два ключевых слова, которые изменили Python. Добавленные в
Python 3.5 (PEP 492), они сделали асинхронное программирование таким же
естественным, как и синхронное. Но за простым синтаксисом скрывается глубокая
механика: корутины, объекты awaitable, event loop.

В этом уроке мы разберём:
- Чем корутины отличаются от обычных функций и генераторов;
- Как работает `await` — что происходит «под капотом»;
- Что такое awaitable объекты: корутины, Tasks, Futures;
- Как правильно запускать корутины (`asyncio.run()`, `gather()`, `create_task()`);
- Асинхронные включения (comprehensions) и асинхронные контекстные менеджеры.

К концу урока вы будете уверенно писать асинхронные функции и понимать, **как**
и **почему** они работают.

---

## Основная часть

### 1. Корутины vs обычные функции vs генераторы

#### Обычная функция (def)

```python
def regular_function():
    return 42

result = regular_function()  # Выполняется и возвращает значение
print(type(regular_function))  # <class 'function'>
print(result)                  # 42
```

Обычная функция: один вызов → одно выполнение от начала до конца → один результат.

#### Генератор (def + yield)

```python
def generator_function():
    yield 1
    yield 2
    yield 3

gen = generator_function()     # НЕ выполняется! Возвращает генератор
print(type(gen))               # <class 'generator'>
print(next(gen))               # 1 — выполняется до первого yield
print(next(gen))               # 2 — продолжает с того же места
```

Генератор: один вызов → объект-генератор → может приостанавливаться и
возобновляться через `yield`. Состояние сохраняется между вызовами `next()`.

#### Корутина (async def + await)

```python
async def coroutine_function():
    await asyncio.sleep(1)
    return 42

coro = coroutine_function()    # НЕ выполняется! Возвращает объект корутины
print(type(coro))              # <class 'coroutine'>
# result = await coro          # Можно await-ить внутри другой корутины
# result = asyncio.run(coro)   # Или запустить через event loop
```

Корутина: один вызов → объект корутины → приостанавливается на `await` и
возобновляется, когда ожидаемое значение готово.

#### Сравнительная таблица

| Характеристика | Обычная функция | Генератор | Корутина |
|:---|---|---|---|
| Создание | `def` | `def` + `yield` | `async def` + `await` |
| Тип результата вызова | Значение (return) | generator object | coroutine object |
| Приостановка | Нет | `yield` | `await` |
| Возобновление | Нет | `next()` / `send()` | Event Loop |
| Состояние | Не сохраняется | Сохраняется | Сохраняется |
| Может await-ить | Нет | Нет | Да |
| Может yield-ить | Нет | Да | Нет (но async generator: да) |

### 2. await: что происходит «под капотом»

Когда интерпретатор встречает `await <expression>`:

```python
async def fetch_data():
    data = await some_io_operation()  # <--- await
    return data
```

Происходит следующее:

1. **Вычисляется выражение** справа от `await` — оно должно вернуть **awaitable**
   объект (корутину, Task или Future).
2. **Вызывается `__await__()`** на awaitable объекте — возвращается итератор.
3. Корутина **приостанавливается** — её состояние (локальные переменные, позиция
   в коде) сохраняется в объекте корутины.
4. **Управление возвращается в Event Loop** — он может запустить другие корутины.
5. Когда awaitable объект готов (I/O завершён, таймер истёк), Event Loop
   **возобновляет** корутину с того же места, передавая результат.

```python
# Демонстрация: корутина — это объект, который можно «продвигать» вручную
async def demo():
    print("Шаг 1")
    await asyncio.sleep(0)
    print("Шаг 2")
    return "Готово"

coro = demo()
try:
    coro.send(None)  # Запускает корутину до первого await
except StopIteration as e:
    print(f"Результат: {e.value}")
# Вывод:
# Шаг 1
# Шаг 2
# Результат: Готово
```

**Важно**: корутина — это не поток. Она не выполняется, пока Event Loop не даст
ей управление. Нет параллелизма — только конкурентность.

### 3. Awaitable объекты: корутины, Tasks, Futures

В Python есть три типа awaitable объектов:

#### 3.1 Корутины (Coroutines)

```python
async def compute():
    return 42

# coro — объект корутины, можно await-ить
coro = compute()
result = await coro  # 42
```

**Особенность**: корутину можно await-ить **только один раз**. После завершения
она становится «мёртвой»:

```python
coro = compute()
await coro  # 42
await coro  # RuntimeError: cannot reuse already awaited coroutine
```

#### 3.2 Tasks

`asyncio.Task` — это обёртка вокруг корутины, которая планирует её выполнение
в Event Loop. Task — это Future, который оборачивает корутину.

```python
async def main():
    # Создаём Task — корутина начинает выполняться немедленно
    task = asyncio.create_task(compute())
    # Task можно await-ить много раз
    result = await task  # 42
    result2 = await task  # 42 (уже завершён, возвращает кешированный результат)
```

**Ключевое отличие Task от корутины**: Task — это **запланированная** работа.
`create_task()` немедленно регистрирует корутину в Event Loop, и она начинает
выполнение при первой возможности, даже если вы ещё не сделали `await`.

```python
async def main():
    task = asyncio.create_task(asyncio.sleep(2))
    # Task уже запущен и тикает!
    print("Делаю другую работу...")
    await asyncio.sleep(1)
    print("Жду task...")
    await task  # Подождёт оставшуюся ~1 сек
    print("Готово!")
```

#### 3.3 Futures

`asyncio.Future` — низкоуровневый объект, представляющий **будущий результат**.
Обычно вы не создаёте Future напрямую — их создают библиотеки и Event Loop.

```python
# Future — это «контейнер» для результата, который появится позже
future = asyncio.Future()

# Где-то в другом месте: future.set_result(42)
# Или: future.set_exception(ValueError("ой"))

result = await future  # Блокируется, пока не будет set_result или set_exception
```

**Иерархия**: `Task` — это подкласс `Future`, который оборачивает корутину.

```
Awaitable
├── Coroutine
├── Future
│   └── Task (Future + coroutine)
```

### 4. Запуск корутин: asyncio.run(), gather(), create_task()

#### 4.1 asyncio.run() — точка входа

С Python 3.7+ `asyncio.run()` — это **стандартный способ** запустить асинхронную
программу:

```python
import asyncio

async def main():
    print("Асинхронный мир!")
    await asyncio.sleep(1)
    return 42

# ✅ Правильно: asyncio.run() создаёт Event Loop, выполняет main, закрывает Loop
result = asyncio.run(main())
print(result)  # 42
```

`asyncio.run()` делает три вещи:
1. Создаёт новый Event Loop;
2. Выполняет переданную корутину до завершения;
3. Закрывает Event Loop.

**Правило**: `asyncio.run()` должен вызываться **ровно один раз** на программу,
в точке входа. Не вызывайте его внутри других асинхронных функций.

```python
# ❌ Антипаттерн: asyncio.run() внутри асинхронной функции
async def inner():
    asyncio.run(asyncio.sleep(1))  # RuntimeError!

# ❌ Антипаттерн: несколько asyncio.run() подряд
asyncio.run(task1())
asyncio.run(task2())  # Разные Event Loop'ы — не видят друг друга
```

#### 4.2 asyncio.gather() — параллельный запуск

`gather()` запускает несколько awaitable объектов **конкурентно** и возвращает
список результатов:

```python
async def fetch(id: int) -> str:
    await asyncio.sleep(1)  # Имитация сетевого запроса
    return f"Результат {id}"

async def main():
    # ✅ Правильно: gather запускает всё параллельно
    results = await asyncio.gather(
        fetch(1),
        fetch(2),
        fetch(3),
    )
    print(results)  # ['Результат 1', 'Результат 2', 'Результат 3']
    # Общее время: ~1 сек, а не 3

asyncio.run(main())
```

**Возврат исключений**: по умолчанию `gather()` пробрасывает первое исключение.
С `return_exceptions=True` исключения возвращаются как результаты:

```python
async def might_fail(id: int) -> str:
    if id == 2:
        raise ValueError(f"Ошибка в {id}")
    return f"OK {id}"

results = await asyncio.gather(
    might_fail(1),
    might_fail(2),
    might_fail(3),
    return_exceptions=True,
)
print(results)
# ['OK 1', ValueError('Ошибка в 2'), 'OK 3']
```

#### 4.3 asyncio.create_task() — фоновые задачи

`create_task()` создаёт Task и **немедленно** планирует его выполнение. Это
позволяет запустить работу «в фоне»:

```python
async def main():
    # Запускаем фоновую задачу
    background = asyncio.create_task(asyncio.sleep(5))

    # Делаем другую работу
    await asyncio.sleep(2)
    print("Основная работа завершена")

    # Ждём фоновую задачу
    await background
    print("Фоновая задача завершена")

asyncio.run(main())
```

#### 4.4 Последовательный await vs gather: критическая разница

```python
# ❌ Антипаттерн: последовательный await
async def sequential():
    result1 = await fetch(1)  # Ждёт 1 сек
    result2 = await fetch(2)  # Ждёт ещё 1 сек
    result3 = await fetch(3)  # Ждёт ещё 1 сек
    # Общее время: 3 сек
    return [result1, result2, result3]

# ✅ Идиоматично: gather для параллельного выполнения
async def parallel():
    results = await asyncio.gather(
        fetch(1),
        fetch(2),
        fetch(3),
    )
    # Общее время: 1 сек
    return results

# ✅ Тоже идиоматично: create_task для параллельного выполнения
async def parallel_tasks():
    tasks = [
        asyncio.create_task(fetch(i))
        for i in range(1, 4)
    ]
    results = []
    for task in tasks:
        results.append(await task)
    return results
```

### 5. Асинхронные включения (comprehensions)

#### 5.1 async for

`async for` позволяет итерироваться по **асинхронному итератору** — объекту,
который при получении каждого элемента делает `await`:

```python
import asyncio

class AsyncCounter:
    """Асинхронный итератор: счётчик с задержкой."""
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def __aiter__(self):
        self.current = self.start
        return self

    async def __anext__(self):
        if self.current >= self.end:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Асинхронная задержка
        value = self.current
        self.current += 1
        return value

async def main():
    async for n in AsyncCounter(0, 5):
        print(n)  # 0, 1, 2, 3, 4 — с паузой 0.1 сек между каждым
```

#### 5.2 Async comprehensions

```python
# Асинхронное списковое включение
async def fetch_squares(nums):
    async def square(n):
        await asyncio.sleep(0.1)
        return n * n

    # ✅ async for внутри list comprehension
    results = [await square(n) async for n in async_gen(nums)]
    return results

# Асинхронный генератор
async def async_gen(items):
    for item in items:
        await asyncio.sleep(0.1)
        yield item
```

### 6. Сравнение async/await в разных языках

#### JavaScript: почти идентичный синтаксис

```javascript
// JavaScript — практически такой же синтаксис
async function fetchData() {
    const response = await fetch('https://api.example.com');
    return response.json();
}

// Promise.all() ≈ asyncio.gather()
const [a, b] = await Promise.all([fetchA(), fetchB()]);
```

**Отличия**:
- JS: `await` работает **только** с Promise (thenable);
- Python: `await` работает с любым awaitable (корутина, Task, Future);
- JS: `Promise.all()` разрешается, когда все Promise разрешены; `Promise.allSettled()` — всегда;
- Python: `gather()` + `return_exceptions=True` = `Promise.allSettled()`.

#### C#: async/await с Task<T>

```csharp
// C# — async/await встроен на уровне компилятора
async Task<string> FetchDataAsync()
{
    var client = new HttpClient();
    var response = await client.GetStringAsync("https://api.example.com");
    return response;
}

// Task.WhenAll() ≈ asyncio.gather()
var results = await Task.WhenAll(task1, task2, task3);
```

**Отличия**:
- C#: async/await — это «синтаксический сахар» над `Task<T>`, компилятор строит
  конечный автомат;
- Python: корутины — это **нативные объекты рантайма**, не синтаксический сахар;
- C#: `ConfigureAwait(false)` для управления контекстом синхронизации;
- Python: все корутины выполняются в одном потоке, контекст не нужен.

#### Java: Virtual Threads (Project Loom)

```java
// Java 21+: виртуальные потоки — другой подход к конкурентности
Thread.startVirtualThread(() -> {
    var response = httpClient.send(request, BodyHandlers.ofString());
    // Блокирующий вызов не блокирует платформенный поток
});
```

**Ключевое отличие**: Java Virtual Threads делают блокирующий код неблокирующим
**автоматически** — не нужно помечать функции `async` и `await`. Python требует
явного указания `async`/`await`, потому что асинхронность — это **выбор
разработчика**, а не свойство рантайма.

#### Сводная таблица

| Язык | Ключевые слова | Модель | Параллелизм CPU |
|:---|---|---|---|
| **Python** | `async`/`await` | Корутины + Event Loop | Нет (GIL) |
| **JavaScript** | `async`/`await` | Promise + Event Loop | Нет (Worker Threads) |
| **C#** | `async`/`await` | Task + SynchronizationContext | Да (нет GIL) |
| **Java** | Нет (Loom) | Virtual Threads | Да (нет GIL) |
| **Rust** | `async`/`.await` | Futures + Executor | Да (нет GIL) |

---

## Практическое задание

### Упражнение 1: Сравнение последовательного и конкурентного выполнения

Напишите две версии функции, которая делает несколько «запросов» (имитируйте
через `asyncio.sleep`):

```python
# template/01_sequential_vs_concurrent.py
import asyncio
import time

async def pretend_request(id: int, delay: float) -> str:
    """Имитация запроса с задержкой delay секунд."""
    print(f"[{time.strftime('%X')}] Запрос {id} начат (задержка {delay}с)")
    await asyncio.sleep(delay)
    print(f"[{time.strftime('%X')}] Запрос {id} завершён")
    return f"Данные от {id}"

async def sequential_requests():
    """Последовательное выполнение: ждём каждый запрос."""
    results = []
    for i in range(1, 6):
        result = await pretend_request(i, 1.0)
        results.append(result)
    return results

async def concurrent_requests():
    """Конкурентное выполнение: запускаем все запросы одновременно."""
    tasks = [
        pretend_request(i, 1.0)
        for i in range(1, 6)
    ]
    return await asyncio.gather(*tasks)

async def main():
    print("=== Последовательное выполнение ===")
    start = time.perf_counter()
    await sequential_requests()
    print(f"Время: {time.perf_counter() - start:.2f} сек\n")

    print("=== Конкурентное выполнение ===")
    start = time.perf_counter()
    await concurrent_requests()
    print(f"Время: {time.perf_counter() - start:.2f} сек")

if __name__ == "__main__":
    asyncio.run(main())
```

### Упражнение 2: Реализуйте awaitable объект

Реализуйте класс `LazyValue`, который можно await-ить:

```python
# template/02_awaitable.py
import asyncio
from typing import Any

class LazyValue:
    """Awaitable объект: возвращает значение после асинхронной задержки."""

    def __init__(self, value: Any, delay: float):
        self.value = value
        self.delay = delay

    def __await__(self):
        # Ваш код: вернуть итератор, который сначала спит delay,
        # а потом возвращает self.value
        pass  # Замените на реализацию

# Проверка:
async def test():
    lazy = LazyValue(42, 0.5)
    result = await lazy
    assert result == 42
    print("✅ LazyValue работает!")
```

### Упражнение 3: Асинхронный генератор с таймаутом

Напишите асинхронный генератор `async_paginated_api`, который:
- Принимает `total_pages: int`;
- На каждой итерации имитирует запрос к API (await asyncio.sleep);
- Генерирует словарь `{"page": N, "data": [...]}`;
- Если страница «загружается» дольше 2 секунд — пропускает с предупреждением.

```python
# template/03_async_paginated_api.py
import asyncio

async def async_paginated_api(total_pages: int):
    """Асинхронный генератор для пагинированного API с таймаутом."""
    # Ваш код здесь
    pass
```

### Упражнение 4: Найдите и исправьте ошибки

В следующем коде есть **5 ошибок** (стилистических и логических). Найдите и
исправьте все:

```python
# template/04_find_errors.py — КОД С ОШИБКАМИ
import asyncio

async def get_data():
    return 42

async def main():
    # Ошибка 1: ???
    result = get_data()
    print(result)

    # Ошибка 2: ???
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    await asyncio.sleep(1)

    # Ошибка 3: ???
    task = asyncio.create_task(get_data())
    result = get_data()  # вместо await task

    # Ошибка 4: ???
    asyncio.run(get_data())  # внутри main()

    # Ошибка 5: ???
    coro = get_data()
    await coro
    await coro  # повторный await корутины

asyncio.run(main())
```

---

## Дополнительные материалы

### Книги
- **«Using Asyncio in Python»** (Caleb Hattingh) — полное практическое руководство
  по asyncio. Глава 2: «The Truth About Coroutines».
- **«Python Concurrency with asyncio»** (Matthew Fowler) — глава 1-3: от корутин
  до конкурентных запросов.
- **«Fluent Python»** (Luciano Ramalho, 2-е издание) — глава 21: Async Python.

### PEP
- **PEP 492** — Coroutines with async and await syntax (Python 3.5).
- **PEP 525** — Asynchronous Generators (Python 3.6).
- **PEP 530** — Asynchronous Comprehensions (Python 3.6).

### Статьи и видео
- **Łukasz Langa: «AsyncIO + Music»** (PyCon 2019) — живая демонстрация asyncio.
- **Real Python: «Async IO in Python: A Complete Walkthrough»** — подробный
  туториал с диаграммами.
- **Super Fast Python: «Python Asyncio Coroutine Guide»** — справочник по корутинам.

### Что дальше?

В следующем уроке мы углубимся в управление задачами: `asyncio.Task`, `gather()`,
`wait()`, `as_completed()`, отмену задач и таймауты.