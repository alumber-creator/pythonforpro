---
title: "Конкурентность и параллелизм: выбор правильной модели"
order: 4
tags: ["конкурентность", "параллелизм", "threading", "multiprocessing", "asyncio", "GIL"]
prerequisites: "Уроки 2-3, базовое понимание GIL и asyncio"
objective: "Научиться выбирать и применять правильную модель конкурентности для разных типов задач"
---

# Конкурентность и параллелизм: выбор правильной модели

## Введение

> "Конкурентность — это композиция независимых вычислений. Параллелизм — это одновременное выполнение вычислений." — Роб Пайк, соавтор Go

Python предлагает несколько моделей конкурентного и параллельного выполнения, и выбор между ними — одно из самых важных архитектурных решений в performance-ориентированном проекте. Неправильный выбор может сделать код **медленнее** однопоточного.

В этом уроке мы разберём:

- **threading** — потоки и GIL: когда они полезны;
- **multiprocessing** — истинный параллелизм для CPU-bound задач;
- **asyncio** — кооперативная многозадачность для I/O;
- **concurrent.futures** — высокоуровневый API для пулов;
- **Паттерны и ловушки**: гонки данных, дедлоки, shared state.

### 🎯 Цель урока

Научиться выбирать и применять правильную модель конкурентности для разных типов задач.

### 📋 Предпосылки

Уроки 2–3, базовое понимание GIL (Global Interpreter Lock) и asyncio.

---

## Основная часть

### 1. Дерево решений: какую модель выбрать?

```text
Задача требует параллельного/конкурентного выполнения?
    │
    ├─ Нет → Однопоточный синхронный код
    │
    └─ Да → Какой тип задачи?
           │
           ├─ CPU-bound (вычисления)
           │      │
           │      ├─ Числовые операции (NumPy, линейная алгебра)?
           │      │   └─ NumPy уже отпускает GIL → threading ⚠️
           │      │
           │      ├─ C-расширения, отпускающие GIL?
           │      │   └─ threading
           │      │
           │      └─ Чистый Python или C-расширения без GIL release?
           │          └─ multiprocessing
           │
           └─ I/O-bound (сеть, диск, БД)
                  │
                  ├─ Тысячи одновременных соединений?
                  │   └─ asyncio
                  │
                  ├─ Десятки-сотни соединений?
                  │   └─ threading или asyncio
                  │
                  └─ Существующий синхронный код?
                      └─ concurrent.futures.ThreadPoolExecutor
```

---

### 2. Глубокое понимание GIL

GIL (Global Interpreter Lock) — это мьютекс, который защищает доступ к объектам Python от одновременного изменения из разных потоков. В любой момент времени **только один поток** исполняет байткод Python.

#### 2.1 Что GIL защищает?

```python
import threading
import sys

# GIL гарантирует, что эти операции атомарны:
x = []           # Создание объекта
x.append(1)      # Одиночный list.append
d = {"a": 1}    # Создание словаря
d["b"] = 2       # Присваивание ключа

# Но не эти:
x = x + [1]      # Чтение + запись — неатомарно!
d["c"] += 1      # Чтение + сложение + запись — неатомарно!
```

#### 2.2 Когда GIL отпускается?

GIL **освобождается** в следующих случаях:

| Операция                                  | GIL отпущен? | Примеры                              |
|-------------------------------------------|--------------|--------------------------------------|
| I/O операции (read, write, recv, send)    | ✅ Да        | `file.read()`, `socket.recv()`       |
| Вызовы C-расширений (без доступа к Python)| ✅ Да        | NumPy вычисления, `hashlib.sha256()` |
| `time.sleep()`                            | ✅ Да        | `time.sleep(1)`                      |
| Ожидание блокировок (threading.Lock)      | ✅ Да        | `lock.acquire()`                     |
| Сетевые вызовы в `requests`/`urllib`      | ✅ Да        | HTTP-запросы к внешним серверам      |
| Чистый Python-код (байткод)               | ❌ Нет       | Циклы, вычисления, работа со строками|

#### 2.3 Демонстрация: GIL в действии

```python
import threading
import time

# CPU-bound задача: два потока = медленнее одного!
def cpu_bound_count(n: int) -> None:
    """Считаем в цикле — чистая CPU-нагрузка."""
    for _ in range(n):
        _ = sum(range(100))


def demonstrate_gil_cpu() -> None:
    """Демонстрация: GIL убивает параллелизм для CPU-bound."""
    N = 50

    # Однопоточный
    start = time.perf_counter()
    cpu_bound_count(N)
    single_time = time.perf_counter() - start
    print(f"Однопоточный (CPU-bound):  {single_time:.3f}s")

    # Двухпоточный
    t1 = threading.Thread(target=cpu_bound_count, args=(N,))
    t2 = threading.Thread(target=cpu_bound_count, args=(N,))

    start = time.perf_counter()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    multi_time = time.perf_counter() - start
    print(f"Двухпоточный (CPU-bound):  {multi_time:.3f}s")
    print(f"Замедление: {multi_time / single_time:.1f}x (ожидаем ~2x из-за GIL)")


# I/O-bound задача: потоки помогают!
def io_bound_sleep(seconds: float) -> None:
    """Имитация I/O: time.sleep() отпускает GIL."""
    time.sleep(seconds)


def demonstrate_gil_io() -> None:
    """Демонстрация: GIL отпускается при I/O."""
    SEC = 0.5

    # Однопоточный: 10 последовательных sleep
    start = time.perf_counter()
    for _ in range(10):
        io_bound_sleep(SEC)
    single_time = time.perf_counter() - start
    print(f"Однопоточный (I/O-bound):  {single_time:.3f}s")

    # Многопоточный: 10 потоков, каждый спит 0.5s
    threads = [threading.Thread(target=io_bound_sleep, args=(SEC,))
               for _ in range(10)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    multi_time = time.perf_counter() - start
    print(f"Многопоточный (I/O-bound): {multi_time:.3f}s")
    print(f"Ускорение: {single_time / multi_time:.1f}x")


if __name__ == "__main__":
    demonstrate_gil_cpu()
    print()
    demonstrate_gil_io()
```

---

### 3. threading: I/O-bound и C-расширения

#### 3.1 Пул потоков с concurrent.futures

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import urllib.request
from typing import Any


def fetch_url(url: str) -> tuple[str, int, float]:
    """Загружает URL и возвращает статус-код."""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            elapsed = time.perf_counter() - start
            return url, response.status, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - start
        return url, -1, elapsed


def fetch_many_threaded(urls: list[str], max_workers: int = 10) -> list[tuple[str, int, float]]:
    """Параллельная загрузка URL через пул потоков."""
    results: list[tuple[str, int, float]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Запускаем все задачи
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}

        # Собираем результаты по мере завершения
        for future in as_completed(future_to_url):
            results.append(future.result())

    return results


def fetch_many_sequential(urls: list[str]) -> list[tuple[str, int, float]]:
    """Последовательная загрузка для сравнения."""
    return [fetch_url(url) for url in urls]


# Бенчмарк
URLS = [
    "https://httpbin.org/delay/0.5",
    "https://httpbin.org/delay/0.5",
    "https://httpbin.org/delay/0.5",
    "https://httpbin.org/delay/0.5",
    "https://httpbin.org/delay/0.5",
]

print("=== Последовательная загрузка ===")
start = time.perf_counter()
seq_results = fetch_many_sequential(URLS)
seq_time = time.perf_counter() - start
print(f"Время: {seq_time:.2f}s")

print("\n=== Многопоточная загрузка (10 workers) ===")
start = time.perf_counter()
threaded_results = fetch_many_threaded(URLS, max_workers=10)
threaded_time = time.perf_counter() - start
print(f"Время: {threaded_time:.2f}s")
print(f"Ускорение: {seq_time / threaded_time:.1f}x")
```

#### 3.2 Паттерн: Producer-Consumer с Queue

```python
import threading
import queue
import time
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    """Задача для обработки."""
    task_id: int
    data: Any


def producer(task_queue: queue.Queue[Task], num_tasks: int) -> None:
    """Производитель: генерирует задачи."""
    for i in range(num_tasks):
        task = Task(task_id=i, data=f"data_{i}")
        task_queue.put(task)
        print(f"  Producer: создана задача {i}")
        time.sleep(random.uniform(0.01, 0.05))  # Имитация генерации


def consumer(task_queue: queue.Queue[Task], worker_id: int) -> None:
    """Потребитель: обрабатывает задачи из очереди."""
    while True:
        try:
            task = task_queue.get(timeout=1.0)
        except queue.Empty:
            print(f"  Consumer-{worker_id}: очередь пуста, выход")
            return

        # Имитация обработки (I/O-bound)
        print(f"  Consumer-{worker_id}: обрабатываю задачу {task.task_id}")
        time.sleep(random.uniform(0.1, 0.3))

        task_queue.task_done()


def run_producer_consumer(num_producers: int = 1,
                          num_consumers: int = 3,
                          num_tasks: int = 10) -> None:
    """Запуск producer-consumer системы."""
    task_queue: queue.Queue[Task] = queue.Queue()

    # Запуск потребителей
    consumers = []
    for i in range(num_consumers):
        t = threading.Thread(target=consumer, args=(task_queue, i), daemon=True)
        t.start()
        consumers.append(t)

    # Запуск производителей
    producers = []
    for i in range(num_producers):
        t = threading.Thread(target=producer, args=(task_queue, num_tasks // num_producers))
        t.start()
        producers.append(t)

    # Ждём завершения производителей
    for t in producers:
        t.join()

    # Ждём, пока очередь опустеет
    task_queue.join()

    # Ждём завершения потребителей
    for t in consumers:
        t.join(timeout=2.0)

    print("Все задачи обработаны.")


if __name__ == "__main__":
    run_producer_consumer()
```

#### 3.3 Потокобезопасные структуры

```python
import threading
from collections import Counter


class ThreadSafeCounter:
    """Потокобезопасный счётчик на основе Lock."""

    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, delta: int = 1) -> int:
        with self._lock:
            self._value += delta
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def worker(counter: ThreadSafeCounter, iterations: int) -> None:
    """Потоковая функция: инкрементирует счётчик."""
    for _ in range(iterations):
        counter.increment()


def demonstrate_race_condition() -> None:
    """Демонстрация гонки данных и её решения."""
    # Без блокировки (гонка данных!)
    unsafe_counter = 0

    def unsafe_worker() -> None:
        nonlocal unsafe_counter
        for _ in range(100_000):
            unsafe_counter += 1  # Неатомарно!

    threads = [threading.Thread(target=unsafe_worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"❌ Без блокировки: {unsafe_counter} (ожидали 1 000 000)")

    # С блокировкой (ThreadSafeCounter)
    safe_counter = ThreadSafeCounter()
    threads = [threading.Thread(target=worker, args=(safe_counter, 100_000))
               for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"✅ С блокировкой: {safe_counter.value} (ожидали 1 000 000)")


demonstrate_race_condition()
```

---

### 4. multiprocessing: истинный параллелизм для CPU-bound

#### 4.1 ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import math
import os


def cpu_intensive_task(n: int) -> tuple[int, int, float]:
    """CPU-bound задача: вычисление простых чисел."""
    pid = os.getpid()
    start = time.perf_counter()

    # Наивный поиск простых чисел до n
    count = 0
    for num in range(2, n + 1):
        is_prime = True
        limit = int(math.sqrt(num)) + 1
        for divisor in range(2, limit):
            if num % divisor == 0:
                is_prime = False
                break
        if is_prime:
            count += 1

    elapsed = time.perf_counter() - start
    return pid, count, elapsed


def compare_cpu_parallel(sizes: list[int]) -> None:
    """Сравнение однопроцессного и многопроцессного выполнения."""
    print(f"Количество ядер CPU: {os.cpu_count()}")

    # Последовательный
    print("\n=== Последовательное выполнение ===")
    start = time.perf_counter()
    for size in sizes:
        pid, count, elapsed = cpu_intensive_task(size)
        print(f"  PID={pid}: primes up to {size}: {count} ({elapsed:.2f}s)")
    seq_time = time.perf_counter() - start
    print(f"Общее время: {seq_time:.2f}s")

    # Параллельный (ProcessPoolExecutor)
    print("\n=== Параллельное выполнение (ProcessPoolExecutor) ===")
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=len(sizes)) as executor:
        futures = {executor.submit(cpu_intensive_task, size): size
                   for size in sizes}
        for future in as_completed(futures):
            pid, count, elapsed = future.result()
            size = futures[future]
            print(f"  PID={pid}: primes up to {size}: {count} ({elapsed:.2f}s)")
    par_time = time.perf_counter() - start
    print(f"Общее время: {par_time:.2f}s")
    print(f"Ускорение: {seq_time / par_time:.1f}x")


if __name__ == "__main__":
    compare_cpu_parallel([50_000, 60_000, 70_000, 80_000])
```

#### 4.2 Обмен данными между процессами

```python
import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np


def process_with_queue() -> None:
    """Обмен через multiprocessing.Queue (сериализация pickle)."""
    def worker(q: mp.Queue, worker_id: int) -> None:
        for i in range(5):
            q.put(f"Worker-{worker_id}: item {i}")

    q: mp.Queue[str] = mp.Queue()
    processes = [mp.Process(target=worker, args=(q, i)) for i in range(3)]

    for p in processes:
        p.start()

    for _ in range(15):
        print(q.get())

    for p in processes:
        p.join()


def process_with_shared_memory() -> None:
    """Обмен через SharedMemory (zero-copy, только Python 3.8+)."""
    # Создаём разделяемую память
    size = np.dtype(np.float64).itemsize * 1000
    shm = shared_memory.SharedMemory(create=True, size=size)
    shared_array = np.ndarray((1000,), dtype=np.float64, buffer=shm.buf)

    # Заполняем в родительском процессе
    shared_array[:] = np.arange(1000, dtype=np.float64)
    print(f"Родитель: shared_array[:5] = {shared_array[:5]}")

    def worker(shm_name: str, shape: tuple[int, ...], dtype: np.dtype) -> None:
        existing_shm = shared_memory.SharedMemory(name=shm_name)
        arr = np.ndarray(shape, dtype=dtype, buffer=existing_shm.buf)
        # Модифицируем в дочернем процессе
        arr[:] *= 2
        existing_shm.close()

    p = mp.Process(target=worker, args=(shm.name, (1000,), np.dtype(np.float64)))
    p.start()
    p.join()

    print(f"После worker: shared_array[:5] = {shared_array[:5]}")

    shm.close()
    shm.unlink()


if __name__ == "__main__":
    process_with_queue()
    print()
    process_with_shared_memory()
```

#### 4.3 Multiprocessing: подводные камни

| Проблема                   | Причина                                    | Решение                                |
|----------------------------|--------------------------------------------|----------------------------------------|
| Высокий оверхед spawn      | `spawn` (Windows/macOS) копирует процесс   | Использовать `fork` на Linux           |
| Оверхед сериализации       | pickle для аргументов и результата         | SharedMemory, mmap                     |
| Ограничение памяти         | Каждый процесс имеет своё адресное пространство | Уменьшить число workers               |
| Не работает в интерактивном режиме | spawn требует `if __name__ == "__main__"` | Всегда использовать guard              |
| Дочерние процессы не завершаются | Pool может висеть                        | `pool.terminate()`, `with`-контекст    |

---

### 5. asyncio: кооперативная многозадачность для высоконагруженного I/O

#### 5.1 Асинхронный HTTP-клиент

```python
import asyncio
import time
from typing import Any

import aiohttp


async def fetch_async(session: aiohttp.ClientSession,
                      url: str) -> dict[str, Any]:
    """Асинхронная загрузка URL."""
    start = time.perf_counter()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            elapsed = time.perf_counter() - start
            return {
                "url": url,
                "status": resp.status,
                "elapsed": elapsed,
                "size": len(await resp.read()),
            }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"url": url, "status": -1, "elapsed": elapsed, "error": str(e)}


async def fetch_many_async(urls: list[str],
                           concurrency: int = 10) -> list[dict[str, Any]]:
    """Асинхронная загрузка многих URL с ограничением конкурентности."""
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_fetch(session: aiohttp.ClientSession,
                            url: str) -> dict[str, Any]:
        async with semaphore:
            return await fetch_async(session, url)

    async with aiohttp.ClientSession() as session:
        tasks = [bounded_fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return list(results)


async def main() -> None:
    urls = [f"https://httpbin.org/delay/0.5" for _ in range(10)]

    print("=== asyncio: 10 запросов ===")
    start = time.perf_counter()
    results = await fetch_many_async(urls, concurrency=10)
    elapsed = time.perf_counter() - start

    for r in results:
        print(f"  {r['url']}: status={r['status']}, time={r['elapsed']:.3f}s")
    print(f"Общее время: {elapsed:.2f}s (ожидаем ~0.5s)")


if __name__ == "__main__":
    asyncio.run(main())
```

#### 5.2 Асинхронный Producer-Consumer

```python
import asyncio
import random
from dataclasses import dataclass


@dataclass
class WorkItem:
    item_id: int
    data: str


async def async_producer(queue: asyncio.Queue[WorkItem],
                         num_items: int) -> None:
    """Асинхронный производитель."""
    for i in range(num_items):
        item = WorkItem(item_id=i, data=f"payload_{i}")
        await queue.put(item)
        print(f"  Producer: создан item {i}")
        await asyncio.sleep(random.uniform(0.01, 0.05))


async def async_consumer(queue: asyncio.Queue[WorkItem],
                         worker_id: int) -> None:
    """Асинхронный потребитель."""
    while True:
        try:
            item = await asyncio.wait_for(queue.get(), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"  Consumer-{worker_id}: таймаут, выход")
            return

        # Имитация асинхронной обработки
        print(f"  Consumer-{worker_id}: обрабатываю item {item.item_id}")
        await asyncio.sleep(random.uniform(0.1, 0.3))

        queue.task_done()


async def run_async_producer_consumer(num_items: int = 10,
                                      num_consumers: int = 3) -> None:
    """Запуск асинхронной producer-consumer системы."""
    queue: asyncio.Queue[WorkItem] = asyncio.Queue(maxsize=5)

    # Запускаем производителя и потребителей параллельно
    await asyncio.gather(
        async_producer(queue, num_items),
        *(async_consumer(queue, i) for i in range(num_consumers)),
    )

    print("Все задачи обработаны.")


if __name__ == "__main__":
    asyncio.run(run_async_producer_consumer())
```

#### 5.3 Совмещение asyncio с синхронным кодом

```python
import asyncio
import concurrent.futures
import time


def blocking_cpu_task(n: int) -> int:
    """Синхронная CPU-bound задача (блокирует event loop!)."""
    total = 0
    for i in range(n):
        total += i * i
    return total


async def run_blocking_in_executor() -> None:
    """Запуск синхронной функции в пуле потоков (не блокирует event loop)."""
    loop = asyncio.get_running_loop()

    print("Запускаем CPU-bound задачу в executor...")
    start = time.perf_counter()

    # Запускаем в отдельном потоке (не блокирует event loop)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_cpu_task, 10_000_000)

    elapsed = time.perf_counter() - start
    print(f"Результат: {result}, время: {elapsed:.2f}s")

    # Для CPU-bound лучше использовать ProcessPoolExecutor
    print("Запускаем CPU-bound задачу в ProcessPoolExecutor...")
    start = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_cpu_task, 10_000_000)

    elapsed = time.perf_counter() - start
    print(f"Результат: {result}, время: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(run_blocking_in_executor())
```

---

### 6. Бенчмарк: все модели в одном тесте

```python
"""
Комплексный бенчмарк: сравнение всех моделей конкурентности.

Тест: 20 задач, каждая из которых:
- 50% времени: CPU-bound (вычисление простых чисел)
- 50% времени: I/O-bound (asyncio.sleep / time.sleep)
"""

import time
import asyncio
import threading
import multiprocessing as mp
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
)
from typing import Callable, Any


def cpu_work(n: int = 5000) -> int:
    """CPU-bound: подсчёт простых чисел."""
    count = 0
    for num in range(2, n + 1):
        is_prime = True
        for div in range(2, int(num ** 0.5) + 1):
            if num % div == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def io_work(seconds: float = 0.1) -> None:
    """I/O-bound: сон."""
    time.sleep(seconds)


def mixed_task(task_id: int) -> tuple[int, int, float]:
    """Смешанная задача: CPU + I/O."""
    start = time.perf_counter()
    prime_count = cpu_work(5000)
    io_work(0.1)
    elapsed = time.perf_counter() - start
    return task_id, prime_count, elapsed


async def async_mixed_task(task_id: int) -> tuple[int, int, float]:
    """Асинхронная версия смешанной задачи."""
    start = time.perf_counter()
    # CPU-часть выполняем в executor, чтобы не блокировать event loop
    loop = asyncio.get_running_loop()
    prime_count = await loop.run_in_executor(None, cpu_work, 5000)
    await asyncio.sleep(0.1)  # Асинхронный I/O
    elapsed = time.perf_counter() - start
    return task_id, prime_count, elapsed


def run_sequential(num_tasks: int) -> float:
    """Последовательное выполнение."""
    start = time.perf_counter()
    for i in range(num_tasks):
        mixed_task(i)
    return time.perf_counter() - start


def run_threading(num_tasks: int, max_workers: int = 10) -> float:
    """ThreadPoolExecutor."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(mixed_task, i) for i in range(num_tasks)]
        for future in as_completed(futures):
            future.result()
    return time.perf_counter() - start


def run_multiprocessing(num_tasks: int, max_workers: int = 4) -> float:
    """ProcessPoolExecutor."""
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(mixed_task, i) for i in range(num_tasks)]
        for future in as_completed(futures):
            future.result()
    return time.perf_counter() - start


async def run_asyncio(num_tasks: int) -> float:
    """asyncio.gather."""
    start = time.perf_counter()
    tasks = [async_mixed_task(i) for i in range(num_tasks)]
    await asyncio.gather(*tasks)
    return time.perf_counter() - start


def run_asyncio_sync(num_tasks: int) -> float:
    """Запуск asyncio из синхронного кода."""
    return asyncio.run(run_asyncio(num_tasks))


def run_benchmark(num_tasks: int = 20) -> None:
    """Запуск полного бенчмарка."""
    print(f"Бенчмарк: {num_tasks} смешанных задач (CPU + I/O)")
    print(f"CPU ядер: {mp.cpu_count()}")
    print("-" * 50)

    methods: list[tuple[str, Callable[[], float]]] = [
        ("Sequential", lambda: run_sequential(num_tasks)),
        ("Threading (10)", lambda: run_threading(num_tasks, 10)),
        ("Multiprocessing (4)", lambda: run_multiprocessing(num_tasks, 4)),
        ("asyncio", lambda: run_asyncio_sync(num_tasks)),
    ]

    results: dict[str, float] = {}
    for name, method in methods:
        elapsed = method()
        results[name] = elapsed
        print(f"{name:25s}: {elapsed:.2f}s")

    baseline = results["Sequential"]
    print("-" * 50)
    for name, elapsed in results.items():
        if name != "Sequential":
            print(f"{name:25s} ускорение: {baseline / elapsed:.1f}x")


if __name__ == "__main__":
    run_benchmark()
```

---

### 7. Питфолы: гонки данных, дедлоки, shared state

#### 7.1 Гонка данных (Race Condition)

```python
import threading

# ❌ Антипаттерн: несинхронизированный доступ к разделяемому состоянию
class UnsafeBankAccount:
    def __init__(self) -> None:
        self.balance = 0

    def deposit(self, amount: int) -> None:
        # balance += amount — это чтение + сложение + запись = неатомарно!
        self.balance += amount

    def withdraw(self, amount: int) -> None:
        if self.balance >= amount:
            self.balance -= amount


# ✅ Паттерн: синхронизация через Lock
from threading import Lock


class SafeBankAccount:
    def __init__(self) -> None:
        self._balance = 0
        self._lock = Lock()

    def deposit(self, amount: int) -> None:
        with self._lock:
            self._balance += amount

    def withdraw(self, amount: int) -> None:
        with self._lock:
            if self._balance >= amount:
                self._balance -= amount

    @property
    def balance(self) -> int:
        with self._lock:
            return self._balance
```

#### 7.2 Дедлок (Deadlock)

```python
import threading
import time

# ❌ Антипаттерн: дедлок из-за неконсистентного порядка блокировок
lock_a = threading.Lock()
lock_b = threading.Lock()


def thread1_bad() -> None:
    with lock_a:
        time.sleep(0.1)  # Имитация работы
        with lock_b:      # Дедлок: thread2 уже держит lock_b
            print("Thread 1: got both locks")


def thread2_bad() -> None:
    with lock_b:
        time.sleep(0.1)
        with lock_a:      # Дедлок: thread1 уже держит lock_a
            print("Thread 2: got both locks")


# ✅ Паттерн: консистентный порядок блокировок
def thread1_good() -> None:
    with lock_a:
        with lock_b:
            print("Thread 1: got both locks (consistent order)")


def thread2_good() -> None:
    with lock_a:           # Всегда lock_a → lock_b
        with lock_b:
            print("Thread 2: got both locks (consistent order)")
```

#### 7.3 Livelock и starvation

```python
# Starvation: низкоприоритетный поток никогда не получает блокировку
# Livelock: потоки постоянно меняют состояние, но не прогрессируют

# Решение: таймауты и backoff
import random

def acquire_with_backoff(lock: threading.Lock,
                         max_attempts: int = 10) -> bool:
    """Захват блокировки с экспоненциальным backoff."""
    for attempt in range(max_attempts):
        if lock.acquire(timeout=0.1):
            return True
        # Экспоненциальный backoff + jitter
        time.sleep((2 ** attempt) * 0.01 + random.uniform(0, 0.01))
    return False
```

---

### 8. Сравнение с другими языками

#### Go: горутины

| Аспект                | Python (asyncio/threading)          | Go (goroutines)                     |
|-----------------------|-------------------------------------|-------------------------------------|
| Модель                | Кооперативная (asyncio) / Системные потоки | Преимущественно кооперативная (GOMAXPROCS) |
| Легковесность         | ~1 KB (asyncio task) / ~8 MB (thread) | ~4 KB (goroutine)                  |
| Переключение контекста| await (явное) / OS (потоки)         | Автоматическое (runtime)            |
| Параллелизм           | multiprocessing                     | Встроенный (GOMAXPROCS)             |
| Каналы                | asyncio.Queue                       | Встроенные channels                 |
| Стоимость создания    | Низкая (task) / Высокая (thread)    | Очень низкая                        |
| 1M одновременных задач| asyncio ✅ / threading ❌           | ✅                                  |

#### Java: виртуальные потоки (Project Loom)

| Аспект                | Python                              | Java (Virtual Threads)               |
|-----------------------|-------------------------------------|--------------------------------------|
| Потоки ОС             | threading (дорогие)                 | Platform threads (дорогие)           |
| Лёгкие задачи         | asyncio (корутины)                  | Virtual threads (Project Loom, Java 21+) |
| Синтаксис             | async/await (окрашенные функции)    | Синхронный (без окрашивания)         |
| Миграция              | Требует переписывания на async/await| Прозрачная (замена Executor)         |
| Дебаггинг             | Сложный (корутины)                  | Простой (стектрейсы как у потоков)   |

#### Erlang/Elixir: акторы

| Аспект                | Python                              | Erlang/Elixir (Actor model)          |
|-----------------------|-------------------------------------|--------------------------------------|
| Модель                | Разделяемая память + блокировки     | Никакой разделяемой памяти (message passing) |
| Изоляция              | Нет (гонки данных)                  | Полная (процессы изолированы)        |
| Сбой                  | Может затронуть весь процесс        | Let it crash (изолированные сбои)    |
| Масштабирование       | multiprocessing                     | Встроенное (BEAM VM)                 |
| Сложность             | Низкая (для простых случаев)        | Высокая (другая парадигма)           |

#### C++: std::async, std::thread

| Аспект                | Python                              | C++                                  |
|-----------------------|-------------------------------------|--------------------------------------|
| Потоки                | threading (GIL!)                    | std::thread (настоящий параллелизм)  |
| Асинхронность         | asyncio (event loop)                | std::async, boost::asio              |
| Параллельные алгоритмы| Нет                                 | C++17 Parallel STL                   |
| Атомарные операции    | Ограниченные (GIL)                  | std::atomic (полный контроль)        |
| Memory ordering       | Нет                                 | acquire/release/relaxed              |

---

### 9. Сводная таблица: выбор модели

| Модель                    | CPU-bound | I/O-bound | High-concurrency | Простота | Память      |
|---------------------------|-----------|-----------|------------------|----------|-------------|
| Однопоточный синхронный   | ❌         | ❌         | ❌                | ⭐⭐⭐⭐⭐   | Низкая      |
| threading                 | ❌ (GIL)   | ✅         | ⚠️ (до ~100)     | ⭐⭐⭐⭐     | Средняя     |
| multiprocessing           | ✅         | ❌ (оверхед)| ❌ (тяжёлые процессы) | ⭐⭐⭐   | Высокая     |
| asyncio                   | ❌ (блокирует)| ✅       | ✅ (до ~100K)     | ⭐⭐       | Низкая      |
| asyncio + run_in_executor | ✅         | ✅         | ✅                | ⭐        | Низкая      |

---

## Практическое задание

### Задача: веб-скрапер с бенчмарком

Реализуйте веб-скрапер, который загружает страницы и извлекает заголовки (`<title>`), тремя способами:

1. **Последовательный** (baseline)
2. **Threading** (ThreadPoolExecutor)
3. **asyncio** (aiohttp + asyncio.gather)

#### Исходный код

```python
"""
Веб-скрапер: последовательный, многопоточный, асинхронный.

Сравните производительность для 50 URL.
"""
import time
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple


class PageInfo(NamedTuple):
    url: str
    title: str
    status: int
    elapsed: float


URLS = [
    "https://www.python.org/",
    "https://docs.python.org/3/",
    "https://pypi.org/",
    "https://github.com/",
    "https://stackoverflow.com/",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://realpython.com/",
    "https://peps.python.org/",
    "https://httpbin.org/",
    "https://news.ycombinator.com/",
] * 5  # 50 URL

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def extract_title(html: str) -> str:
    """Извлекает заголовок из HTML."""
    match = TITLE_RE.search(html)
    if match:
        return match.group(1).strip()
    return "(no title)"


def fetch_page(url: str) -> PageInfo:
    """Загружает страницу и извлекает заголовок."""
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            title = extract_title(html)
            return PageInfo(url, title, resp.status, time.perf_counter() - start)
    except Exception as e:
        return PageInfo(url, str(e), -1, time.perf_counter() - start)


def run_sequential(urls: list[str]) -> tuple[list[PageInfo], float]:
    """Последовательное выполнение."""
    start = time.perf_counter()
    results = [fetch_page(url) for url in urls]
    elapsed = time.perf_counter() - start
    return results, elapsed


def run_threaded(urls: list[str], max_workers: int = 20) -> tuple[list[PageInfo], float]:
    """Многопоточное выполнение."""
    start = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_page, url): url for url in urls}
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - start
    return results, elapsed


# --- ВАША РЕАЛИЗАЦИЯ ---
# run_async(urls) с использованием aiohttp
# async def run_async(urls: list[str]) -> tuple[list[PageInfo], float]:
#     ...


def main() -> None:
    print(f"Скрапинг {len(URLS)} URL...\n")

    # Sequential
    results_seq, time_seq = run_sequential(URLS)
    print(f"{'Sequential':20s}: {time_seq:.2f}s")
    for r in results_seq[:3]:
        print(f"  {r.title[:50]}...")

    # Threaded
    results_thr, time_thr = run_threaded(URLS, max_workers=20)
    print(f"\n{'Threading (20)':20s}: {time_thr:.2f}s")
    print(f"Ускорение vs sequential: {time_seq / time_thr:.1f}x")

    # Async (реализуйте самостоятельно)
    # results_async, time_async = asyncio.run(run_async(URLS))
    # print(f"\n{'asyncio':20s}: {time_async:.2f}s")
    # print(f"Ускорение vs sequential: {time_seq / time_async:.1f}x")


if __name__ == "__main__":
    main()
```

### Шаги выполнения

1. **Запустите baseline** (последовательный + threading) и зафиксируйте результаты.

2. **Реализуйте асинхронную версию** с использованием `aiohttp`:
   ```bash
   pip install aiohttp
   ```

3. **Добавьте ограничение конкурентности** (Semaphore) и исследуйте, как оно влияет на производительность при разных `max_concurrency` (5, 10, 20, 50).

4. **Добавьте CPU-bound задачу** в скрапер (например, парсинг HTML через BeautifulSoup) и сравните, как изменится поведение threading vs asyncio.

5. **Постройте график** времени выполнения от числа URL для каждой модели (10, 20, 50, 100 URL).

6. **Исследуйте влияние GIL**: добавьте искусственную CPU-нагрузку (цикл вычислений) в `fetch_page` и измерьте degradation для threading.

### Ожидаемые результаты

- Таблица: время выполнения для sequential, threading, asyncio (50 URL)
- График масштабирования (10–100 URL)
- Вывод о выборе модели для веб-скрапинга
- Анализ влияния Semaphore на производительность asyncio
- Объяснение, почему threading деградирует при добавлении CPU-нагрузки

---

## Дополнительные материалы

### Книги

- **Using Asyncio in Python**, Caleb Hattingh — полное руководство по asyncio
- **Fluent Python**, Luciano Ramalho — глава 19: Concurrency Models
- **High Performance Python**, Micha Gorelick & Ian Ozsvald — главы 8–10
- **Python Concurrency with asyncio**, Matthew Fowler

### Инструменты

- [aiometer](https://github.com/encode/aiometer) — измерение конкурентности в asyncio
- [anyio](https://github.com/agronholm/anyio) — единый API для asyncio и trio
- [trio](https://github.com/python-trio/trio) — альтернативная библиотека structured concurrency
- [uvloop](https://github.com/MagicStack/uvloop) — замена event loop на libuv (как в Node.js)

### Онлайн-ресурсы

- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [Python Concurrency: The Tricky Bits](https://www.youtube.com/watch?v=MCs5OvhV9Ag) — Raymond Hettinger
- [Understanding the Python GIL](https://www.youtube.com/watch?v=Obt-vMVdM8s) — David Beazley
- [Łukasz Langa: AsyncIO + Music](https://www.youtube.com/watch?v=E-\_1tONF6rE)
- [Structured Concurrency (trio blog)](https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/)

### Сравнительная таблица конкурентности в разных языках

| Язык         | Модель                       | Параллелизм CPU | Конкурентность I/O | Сложность |
|-------------|------------------------------|-----------------|--------------------|-----------|
| **Python**  | threading + GIL / asyncio / mp | ⭐⭐ (mp)       | ⭐⭐⭐⭐ (asyncio)  | ⭐⭐–⭐⭐⭐ |
| **Go**      | Goroutines + channels        | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐           | ⭐⭐       |
| **Java**    | Virtual threads + ForkJoin   | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐           | ⭐⭐⭐      |
| **Erlang**  | Actor model (BEAM)           | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐           | ⭐⭐⭐⭐     |
| **C++**     | std::thread + async          | ⭐⭐⭐⭐⭐        | ⭐⭐⭐              | ⭐⭐⭐⭐⭐    |
| **Rust**    | tokio / async-std + rayon    | ⭐⭐⭐⭐⭐        | ⭐⭐⭐⭐⭐           | ⭐⭐⭐⭐     |
| **Node.js** | Event loop + worker threads  | ⭐⭐ (workers)  | ⭐⭐⭐⭐⭐           | ⭐⭐       |