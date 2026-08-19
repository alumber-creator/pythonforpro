---
title: "asyncio: Tasks, Futures и управление конкурентными операциями"
order: 3
tags: ["asyncio", "tasks", "futures", "gather", "wait"]
prerequisites: "Урок 2"
objective: "Освоить управление конкурентными задачами в asyncio"
---

# asyncio: Tasks, Futures и управление конкурентными операциями

## Введение

Когда корутины написаны, встаёт вопрос: **как ими управлять**? Как запустить
несколько задач одновременно, как дождаться первой завершившейся, как отменить
задачу, которая выполняется слишком долго, как обрабатывать ошибки в
конкурентных операциях?

В этом уроке мы детально разберём инструменты управления задачами в asyncio:
- `asyncio.Task` — обёртка для конкурентного выполнения корутин;
- `asyncio.gather()` — параллельный запуск с агрегацией результатов;
- `asyncio.wait()` и `asyncio.as_completed()` — гибкое ожидание;
- Отмена задач: `cancel()`, `CancelledError`, shield;
- Таймауты: `wait_for()` и `timeout()` (Python 3.11+);
- `asyncio.TaskGroup` (Python 3.11+) — structured concurrency;
- Обработка ошибок в конкурентных задачах.

К концу урока вы сможете построить надёжную систему конкурентных операций с
правильной обработкой ошибок и отменой.

---

## Основная часть

### 1. asyncio.Task: глубокое погружение

#### Что такое Task?

`asyncio.Task` — это **подкласс Future**, который:
- Оборачивает корутину;
- Планирует её выполнение в Event Loop;
- Отслеживает состояние (pending, done, cancelled);
- Хранит результат или исключение;
- Позволяет отменить выполнение.

```python
import asyncio

async def work():
    await asyncio.sleep(1)
    return "Результат"

async def main():
    task = asyncio.create_task(work())
    print(f"Готов? {task.done()}")      # False
    print(f"Отменён? {task.cancelled()}")  # False

    result = await task
    print(f"Готов? {task.done()}")      # True
    print(f"Результат: {result}")       # "Результат"
    print(f"Результат ещё раз: {await task}")  # "Результат" (кеширован)

asyncio.run(main())
```

#### Жизненный цикл Task

```
                    create_task()
                         │
                         ▼
    ┌──────────────────────────────────────┐
    │              PENDING                  │
    │  (корутина ещё не завершилась)        │
    └──────┬───────────────┬───────────────┘
           │               │
    успех  │               │  исключение
           ▼               ▼
    ┌──────────┐    ┌──────────────┐
    │  DONE    │    │  DONE (exc)  │
    │ result() │    │ exception()  │
    └──────────┘    └──────────────┘

    cancel() ──► CANCELLED ──► CancelledError при await
```

#### create_task vs ensure_future

```python
# ✅ Предпочтительный способ (Python 3.7+)
task = asyncio.create_task(coro)

# ⚠️ Устаревший/низкоуровневый способ
task = asyncio.ensure_future(coro)

# Разница: ensure_future не требует работающего Event Loop
# (может быть вызвана вне асинхронного контекста)
```

**Правило**: используйте `create_task()` внутри асинхронных функций.
`ensure_future()` — только когда вам нужен Task вне Event Loop (редко).

#### Сохранение ссылок на Task

```python
# ❌ Антипаттерн: потеря ссылки на Task
async def bad():
    asyncio.create_task(work())  # Task создан, но ссылка потеряна!
    # Сборщик мусора может удалить Task до завершения
    await asyncio.sleep(2)

# ✅ Идиоматично: сохраняем ссылку
async def good():
    task = asyncio.create_task(work())  # Ссылка сохранена
    await asyncio.sleep(2)
    await task  # Явно дожидаемся

# ✅ Идиоматично: TaskGroup управляет ссылками за нас
async def better():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(work())  # TaskGroup хранит ссылку
```

### 2. asyncio.gather(): параллельный запуск с агрегацией

#### Базовое использование

```python
async def fetch(id: int, delay: float) -> dict:
    await asyncio.sleep(delay)
    return {"id": id, "data": f"value_{id}"}

async def main():
    results = await asyncio.gather(
        fetch(1, 2.0),
        fetch(2, 1.0),
        fetch(3, 0.5),
    )
    print(results)
    # [
    #   {'id': 1, 'data': 'value_1'},
    #   {'id': 2, 'data': 'value_2'},
    #   {'id': 3, 'data': 'value_3'},
    # ]
    # Порядок результатов соответствует порядку аргументов!
```

#### Обработка исключений в gather

```python
async def might_fail(id: int) -> str:
    await asyncio.sleep(0.1)
    if id == 2:
        raise ValueError(f"Задача {id} упала")
    return f"OK {id}"

async def main():
    # По умолчанию: первое исключение пробрасывается
    try:
        results = await asyncio.gather(
            might_fail(1),
            might_fail(2),  # Упадёт здесь
            might_fail(3),
        )
    except ValueError as e:
        print(f"Поймано: {e}")  # Поймано: Задача 2 упала
        # Другие задачи отменены!

    # С return_exceptions=True: исключения возвращаются как результаты
    results = await asyncio.gather(
        might_fail(1),
        might_fail(2),
        might_fail(3),
        return_exceptions=True,
    )
    print(results)
    # ['OK 1', ValueError('Задача 2 упала'), 'OK 3']
```

#### gather с уже созданными Task

```python
async def main():
    # gather принимает и корутины, и Task
    task1 = asyncio.create_task(fetch(1, 1.0))
    task2 = asyncio.create_task(fetch(2, 2.0))

    # Task уже выполняются, gather просто ждёт их
    results = await asyncio.gather(task1, task2)
```

### 3. asyncio.wait() и asyncio.as_completed()

#### asyncio.wait(): гибкое ожидание

`wait()` — более низкоуровневый примитив, чем `gather()`. Он позволяет ждать
задачи с разными стратегиями:

```python
import asyncio

async def task(name: str, delay: float, fail: bool = False):
    await asyncio.sleep(delay)
    if fail:
        raise ValueError(f"{name} упала")
    return f"{name} завершена"

async def main():
    tasks = {
        asyncio.create_task(task("A", 2.0)),
        asyncio.create_task(task("B", 1.0)),
        asyncio.create_task(task("C", 3.0, fail=True)),
    }

    # Ждать ВСЕ задачи (даже если некоторые упадут)
    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    for t in done:
        if t.exception():
            print(f"{t.get_name()}: ошибка — {t.exception()}")
        else:
            print(f"{t.get_name()}: результат — {t.result()}")

# Вывод:
# B: результат — B завершена
# A: результат — A завершена
# C: ошибка — C упала
```

**Стратегии ожидания**:

| Константа | Поведение |
|:---|---|
| `ALL_COMPLETED` | Ждать завершения **всех** задач (по умолчанию) |
| `FIRST_COMPLETED` | Ждать **первую** завершившуюся (успех или ошибка) |
| `FIRST_EXCEPTION` | Ждать **первую** ошибку или все успешные |

```python
# FIRST_COMPLETED: реагируем на первую готовую
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
fastest = done.pop()
print(f"Первая: {fastest.result()}")  # B — самая быстрая

# Не забываем отменить оставшиеся!
for p in pending:
    p.cancel()
```

#### asyncio.as_completed(): обработка по мере готовности

`as_completed()` возвращает итератор, который выдаёт задачи **по мере их
завершения** (а не в порядке запуска):

```python
async def main():
    tasks = [
        asyncio.create_task(task("A", 3.0)),
        asyncio.create_task(task("B", 1.0)),
        asyncio.create_task(task("C", 2.0)),
    ]

    for coro in asyncio.as_completed(tasks):
        try:
            result = await coro
            print(f"Завершена: {result}")
        except Exception as e:
            print(f"Ошибка: {e}")

# Вывод (в порядке завершения):
# Завершена: B завершена  ← через 1 сек
# Завершена: C завершена  ← через 2 сек
# Завершена: A завершена  ← через 3 сек
```

**Когда использовать**:
- `gather()` — нужны все результаты в исходном порядке;
- `as_completed()` — нужно реагировать на результаты по мере поступления;
- `wait()` — нужен тонкий контроль (отмена pending, сложные стратегии).

### 4. Отмена задач: cancel() и CancelledError

#### Базовое использование

```python
async def long_running():
    try:
        print("Начинаю долгую работу...")
        await asyncio.sleep(60)  # Очень долго
        print("Завершено!")
        return "Результат"
    except asyncio.CancelledError:
        print("Задача отменена, подчищаю ресурсы...")
        # Важно: пробрасываем CancelledError после очистки!
        raise

async def main():
    task = asyncio.create_task(long_running())
    await asyncio.sleep(0.1)  # Даём задаче стартовать
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("main: задача отменена, продолжаем")
```

#### Правильная обработка CancelledError

```python
# ✅ Идиоматично: очистка ресурсов при отмене
async def cleanup_on_cancel():
    resource = await acquire_resource()
    try:
        await asyncio.sleep(100)
    except asyncio.CancelledError:
        await resource.close()     # Асинхронная очистка
        raise                      # Пробрасываем CancelledError!
    finally:
        # finally тоже выполняется при отмене
        pass

# ❌ Антипаттерн: подавление CancelledError
async def bad_suppress():
    try:
        await asyncio.sleep(100)
    except asyncio.CancelledError:
        print("Отмена — но я продолжаю!")
        return "Результат"  # Не пробрасываем CancelledError!
    # Task не будет считаться cancelled — done() = True, cancelled() = False
```

**Важно**: подавление `CancelledError` — это почти всегда ошибка. Если вы его
поймали, вы **должны** пробросить его дальше (или заменить на другой
`CancelledError`), чтобы Task считался отменённым.

#### shield(): защита от отмены

```python
async def critical_section():
    # Этот код НЕ будет отменён, даже если внешний Task отменят
    await asyncio.shield(asyncio.sleep(5))
    print("Критическая секция завершена")

async def main():
    task = asyncio.create_task(critical_section())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Отмена после shield")  # Сработает после shield
```

### 5. Таймауты: wait_for() и timeout()

#### asyncio.wait_for()

```python
async def slow_operation():
    await asyncio.sleep(10)
    return "Готово"

async def main():
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
    except asyncio.TimeoutError:
        print("Операция превысила таймаут!")
        # Важно: slow_operation отменена автоматически
```

**Особенность**: `wait_for()` отменяет внутреннюю корутину при таймауте.
Если корутина не обрабатывает `CancelledError`, она просто остановится.

#### asyncio.timeout() (Python 3.11+)

Новый контекстный менеджер — более гибкий, чем `wait_for()`:

```python
# Python 3.11+
async def main():
    async with asyncio.timeout(2.0):
        # Все операции внутри имеют общий таймаут 2 сек
        await asyncio.sleep(1)
        await asyncio.sleep(1)
        await asyncio.sleep(1)  # Здесь TimeoutError

    # Если нужно разное поведение при таймауте:
    try:
        async with asyncio.timeout(2.0) as cm:
            await asyncio.sleep(3)
    except TimeoutError:
        if cm.expired:
            print("Таймаут истёк")
```

**Сравнение `wait_for` и `timeout`**:

| Характеристика | `wait_for()` | `timeout()` (3.11+) |
|:---|---:|---:|
| Синтаксис | Функция | Контекстный менеджер |
| Область | Одна корутина | Блок кода |
| Отмена | Автоматическая | Автоматическая |
| Проверка истечения | `TimeoutError` | `cm.expired` |
| Python | 3.4+ | 3.11+ |

### 6. asyncio.TaskGroup (Python 3.11+): structured concurrency

`TaskGroup` — это **структурная конкурентность**: все задачи, созданные внутри
группы, гарантированно завершаются (или отменяются) при выходе из блока.

```python
# Python 3.11+
async def fetch(id: int) -> str:
    await asyncio.sleep(1.0 / id)
    if id == 3:
        raise ValueError(f"Ошибка в {id}")
    return f"Данные {id}"

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(fetch(1))
            task2 = tg.create_task(fetch(2))
            task3 = tg.create_task(fetch(3))  # Упадёт
            task4 = tg.create_task(fetch(4))
    except ExceptionGroup as eg:
        # Все ошибки из группы собраны в ExceptionGroup
        print(f"Исключений: {len(eg.exceptions)}")
        for exc in eg.exceptions:
            print(f"  - {exc}")
        # Все задачи группы гарантированно завершены (или отменены)

asyncio.run(main())
```

**Ключевые свойства TaskGroup**:
1. При выходе из блока **все задачи завершены** (успешно, с ошибкой, или отменены);
2. Если одна задача падает — **отменяются все остальные**;
3. Ошибки собираются в `ExceptionGroup` (Python 3.11+);
4. Нельзя потерять ссылку на Task — группа управляет ими.

```python
# ❌ Антипаттерн: потерянные задачи
async def bad():
    asyncio.create_task(work())  # Может потеряться
    asyncio.create_task(work())  # Может потеряться
    # Нет гарантии, что задачи завершатся

# ✅ Идиоматично: TaskGroup
async def good():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(work())  # Группа следит
        tg.create_task(work())  # Группа следит
    # Здесь все задачи точно завершены
```

### 7. Обработка ошибок в конкурентных задачах

#### Стратегия 1: Сбор всех ошибок

```python
async def robust_gather(*coros, default=None):
    """Безопасный gather: возвращает (результаты, ошибки)."""
    results = []
    errors = []
    for coro in asyncio.as_completed(
        [asyncio.create_task(c) for c in coros]
    ):
        try:
            result = await coro
            results.append(result)
        except Exception as e:
            errors.append(e)
    return results, errors
```

#### Стратегия 2: Retry с exponential backoff

```python
import random

async def fetch_with_retry(
    coro_factory,
    max_retries: int = 3,
    base_delay: float = 1.0,
):
    """Выполнить корутину с повторными попытками."""
    for attempt in range(max_retries):
        try:
            return await coro_factory()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            print(f"Попытка {attempt + 1} не удалась: {e}. "
                  f"Повтор через {delay:.2f}с")
            await asyncio.sleep(delay)
```

#### Стратегия 3: Circuit Breaker

```python
class CircuitBreaker:
    """Предохранитель: блокирует вызовы после N ошибок подряд."""

    def __init__(self, failure_threshold: int, recovery_timeout: float):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "closed"  # closed | open | half_open

    async def call(self, coro_factory):
        import time
        if self.state == "open":
            if time.monotonic() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise RuntimeError("Circuit breaker is OPEN")

        try:
            result = await coro_factory()
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### 8. Сравнение с другими языками

#### JavaScript: Promise.all / allSettled / race

```javascript
// Promise.all() ≈ asyncio.gather() (без return_exceptions)
const results = await Promise.all([fetchA(), fetchB(), fetchC()]);
// Первая ошибка → всё падает

// Promise.allSettled() ≈ asyncio.gather(return_exceptions=True)
const settled = await Promise.allSettled([fetchA(), fetchB(), fetchC()]);
// Всегда массив {status, value/reason}

// Promise.race() ≈ asyncio.wait(FIRST_COMPLETED)
const fastest = await Promise.race([fetchA(), fetchB(), fetchC()]);
// Первый результат (успех или ошибка)

// Promise.any() ≈ asyncio.wait(FIRST_COMPLETED) + фильтр успешных
const firstSuccess = await Promise.any([fetchA(), fetchB(), fetchC()]);
// Первый успешный результат; AggregateError если все упали
```

#### Java: CompletableFuture

```java
// CompletableFuture.allOf() ≈ asyncio.gather()
CompletableFuture<Void> all = CompletableFuture.allOf(future1, future2, future3);
all.join();  // Блокирует поток ОС!

// Отмена задачи
future.cancel(true);  // mayInterruptIfRunning

// Таймаут
future.orTimeout(2, TimeUnit.SECONDS);
```

**Ключевое отличие**: Java `CompletableFuture` может блокировать поток ОС вызовом
`.join()` или `.get()` — это не проблема в Java (нет GIL), но в Python это
заблокировало бы Event Loop.

#### C#: Task.WhenAll / WhenAny

```csharp
// Task.WhenAll() ≈ asyncio.gather()
var results = await Task.WhenAll(task1, task2, task3);

// Task.WhenAny() ≈ asyncio.wait(FIRST_COMPLETED)
var first = await Task.WhenAny(task1, task2, task3);

// Таймаут с CancellationToken
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(2));
await task.WaitAsync(cts.Token);
```

---

## Практическое задание

### Упражнение 1: Конкурентный краулер с таймаутом

Напишите асинхронный «краулер», который:
- Принимает список URL (имитировать через `asyncio.sleep`);
- Запускает все запросы конкурентно;
- Каждый запрос имеет таймаут 2 секунды;
- Собирает успешные результаты и ошибки отдельно;
- Если запрос падает, это не должно влиять на остальные.

```python
# template/01_crawler.py
import asyncio
from dataclasses import dataclass
from typing import Any

@dataclass
class CrawlResult:
    url: str
    data: Any | None = None
    error: str | None = None

async def crawl_url(url: str, delay: float, fail: bool = False) -> str:
    """Имитация запроса к URL."""
    await asyncio.sleep(delay)
    if fail:
        raise ConnectionError(f"Не удалось подключиться к {url}")
    return f"<html>{url}</html>"

async def crawl_many(urls: list[tuple[str, float, bool]]) -> list[CrawlResult]:
    """Ваша реализация: конкурентный краулер с таймаутом."""
    # 1. Создать Task для каждого URL
    # 2. Обернуть каждый в wait_for(timeout=2.0)
    # 3. Собрать результаты через gather с return_exceptions=True
    # 4. Преобразовать в CrawlResult
    pass

# Тест:
async def test():
    urls = [
        ("https://site1.com", 1.0, False),
        ("https://site2.com", 3.0, False),  # Таймаут
        ("https://site3.com", 0.5, True),   # Ошибка
        ("https://site4.com", 1.5, False),
    ]
    results = await crawl_many(urls)
    for r in results:
        print(r)
```

### Упражнение 2: TaskGroup для загрузки с отменой

Используя `TaskGroup` (Python 3.11+), напишите функцию `download_all`, которая:
- Одновременно загружает N ресурсов;
- Если любой ресурс падает — отменяет ВСЕ остальные;
- Возвращает список результатов (только успешные).

### Упражнение 3: Реализуйте семафор для ограничения конкурентности

```python
# template/03_semaphore.py
import asyncio

async def rate_limited_fetch(
    sem: asyncio.Semaphore,
    url: str,
    delay: float,
) -> str:
    """Скачать URL, но не более N одновременных запросов."""
    # Ваш код: использовать semaphore
    pass

async def main():
    sem = asyncio.Semaphore(3)  # Максимум 3 одновременных запроса
    urls = [(f"url_{i}", 1.0) for i in range(20)]
    tasks = [rate_limited_fetch(sem, url, delay) for url, delay in urls]
    results = await asyncio.gather(*tasks)
    print(f"Загружено {len(results)} ресурсов")
```

### Упражнение 4: Graceful shutdown

Напишите асинхронный сервер (имитацию), который:
- Запускает 5 «обработчиков» (бесконечные корутины);
- При получении сигнала (Ctrl+C или `asyncio.sleep(10)`) отменяет все обработчики;
- Каждый обработчик должен корректно очистить свои ресурсы при отмене;
- Дождаться завершения всех обработчиков.

```python
# template/04_graceful_shutdown.py
import asyncio
import signal

async def handler(name: str, queue: asyncio.Queue):
    """Обработчик: читает из очереди и обрабатывает."""
    try:
        while True:
            item = await queue.get()
            # Обработка...
            print(f"[{name}] обработал: {item}")
            queue.task_done()
    except asyncio.CancelledError:
        print(f"[{name}] завершает работу...")
        # Очистка ресурсов обработчика
        raise

async def main():
    # Ваш код: создать очередь, запустить обработчики,
    # реализовать graceful shutdown
    pass
```

---

## Дополнительные материалы

### Книги
- **«Python Concurrency with asyncio»** (Matthew Fowler) — главы 4-6: Tasks,
  cancellation, timeouts, error handling.
- **«Using Asyncio in Python»** (Caleb Hattingh) — глава 3: «Asyncio Tasks».
- **«Fluent Python»** (Luciano Ramalho, 2-е издание) — глава 21: раздел о Task.

### PEP
- **PEP 3156** — Asynchronous IO Support Rebooted (asyncio design).
- **PEP 654** — Exception Groups and except* (Python 3.11).
- **PEP 680** — tomllib (supporting structured concurrency).

### Статьи
- **Nathaniel J. Smith: «Notes on structured concurrency»** — фундаментальная
  статья о концепции structured concurrency.
- **Real Python: «Python asyncio.create_task()»** — подробный туториал.
- **Super Fast Python: «Asyncio Task Cancellation»** — все аспекты отмены задач.

### Что дальше?

В следующем уроке мы изучим асинхронные контекстные менеджеры и итераторы —
ключевые инструменты для работы с ресурсами в асинхронном мире.