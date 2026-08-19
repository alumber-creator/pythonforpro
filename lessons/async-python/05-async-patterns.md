---
title: "Асинхронные паттерны: очереди, producer-consumer и реальные примеры"
order: 5
tags: ["паттерны", "очереди", "producer-consumer", "aiohttp", "asyncpg"]
prerequisites: "Урок 4"
objective: "Освоить практические асинхронные паттерны для реальных приложений"
---

# Асинхронные паттерны: очереди, producer-consumer и реальные примеры

## Введение

Мы изучили корутины, задачи, контекстные менеджеры и итераторы. Теперь пришло
время собрать всё вместе и построить **реальные асинхронные системы**. В этом
уроке мы разберём паттерны, которые встречаются в каждом втором asyncio-проекте:

- **Producer-Consumer** с `asyncio.Queue` — основа обработки потоков данных;
- **Worker Pool** — пул обработчиков для конкурентной обработки задач;
- **Backpressure** через ограничение размера очереди;
- **Rate Limiting** с семафорами;
- **Graceful Shutdown** — корректное завершение асинхронной системы;
- **Микширование async и sync кода** через `run_in_executor()`;
- **Реальные примеры**: HTTP-клиент на aiohttp, работа с БД через asyncpg;
- **Распространённые ошибки**: блокировка Event Loop, забытый await, потерянные Task.

К концу урока вы сможете спроектировать и реализовать асинхронный сервис, готовый
к production.

---

## Основная часть

### 1. Producer-Consumer с asyncio.Queue

#### Базовый паттерн

```python
import asyncio
from typing import Any

async def producer(queue: asyncio.Queue, n: int):
    """Производит элементы и кладёт в очередь."""
    for i in range(n):
        await asyncio.sleep(0.1)  # Имитация создания элемента
        item = f"item-{i}"
        await queue.put(item)
        print(f"Произведено: {item}")
    # Сигнал завершения: кладём None-сторожей
    await queue.put(None)

async def consumer(queue: asyncio.Queue, name: str):
    """Потребляет элементы из очереди."""
    while True:
        item = await queue.get()
        if item is None:
            # Сторож: пора заканчивать
            queue.task_done()
            print(f"{name}: завершаю работу")
            break
        await asyncio.sleep(0.2)  # Имитация обработки
        print(f"{name} обработал: {item}")
        queue.task_done()

async def main():
    queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=10)

    # Запускаем производителя и потребителей
    prod = asyncio.create_task(producer(queue, 10))
    consumers = [
        asyncio.create_task(consumer(queue, f"C{i}"))
        for i in range(3)
    ]

    await prod  # Ждём завершения производителя
    await queue.join()  # Ждём, пока все элементы обработаны

    # Отправляем сторожей каждому потребителю
    for _ in consumers:
        await queue.put(None)

    await asyncio.gather(*consumers)  # Ждём завершения потребителей
    print("Все задачи завершены")

asyncio.run(main())
```

**Ключевые моменты**:
- `queue.put()` — **асинхронный** метод (ждёт, если очередь полна);
- `queue.get()` — **асинхронный** метод (ждёт, если очередь пуста);
- `queue.join()` — ждёт, пока все элементы не будут помечены `task_done()`;
- `queue.task_done()` — сообщает очереди, что элемент обработан;
- `None`-сторож — стандартный способ сигнализировать о завершении.

#### Backpressure через ограничение очереди

```python
# maxsize=10: если очередь полна, producer ждёт на queue.put()
# Это создаёт backpressure — производитель не может обогнать потребителей
queue = asyncio.Queue(maxsize=10)

async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        await asyncio.sleep(0.01)  # Быстрый производитель
        await queue.put(f"item-{i}")  # Блокируется, если очередь полна
        print(f"Произведено: {i}, размер очереди: {queue.qsize()}")

async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await asyncio.sleep(0.5)  # Медленный потребитель
        print(f"{name} обработал: {item}, размер очереди: {queue.qsize()}")
        queue.task_done()
```

**Результат**: производитель быстро заполнит очередь до 10 элементов и
заблокируется на `queue.put()`, ожидая, пока потребители освободят место.
Это **backpressure** — естественное ограничение скорости.

### 2. Worker Pool паттерн

```python
import asyncio
from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class WorkItem:
    """Элемент работы для пула."""
    id: int
    data: Any

class AsyncWorkerPool:
    """Пул асинхронных обработчиков."""

    def __init__(
        self,
        worker_count: int,
        handler: Callable[[Any], Awaitable[Any]],
        queue_size: int = 100,
    ):
        self.queue: asyncio.Queue[WorkItem | None] = asyncio.Queue(maxsize=queue_size)
        self.handler = handler
        self.worker_count = worker_count
        self._workers: list[asyncio.Task] = []

    async def start(self):
        """Запустить пул обработчиков."""
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.worker_count)
        ]
        print(f"Запущено {self.worker_count} обработчиков")

    async def submit(self, item: Any) -> None:
        """Отправить элемент на обработку."""
        work = WorkItem(id=id(item), data=item)
        await self.queue.put(work)

    async def stop(self):
        """Остановить пул: дождаться обработки всех элементов."""
        # Ждём, пока очередь опустеет
        await self.queue.join()

        # Отправляем сторожей
        for _ in range(self.worker_count):
            await self.queue.put(None)

        # Ждём завершения обработчиков
        await asyncio.gather(*self._workers)
        print("Пул остановлен")

    async def _worker(self, worker_id: int):
        """Один обработчик пула."""
        while True:
            item = await self.queue.get()
            if item is None:
                self.queue.task_done()
                print(f"Обработчик {worker_id} завершил работу")
                break
            try:
                result = await self.handler(item.data)
                print(f"[W{worker_id}] обработал {item.id}: {result}")
            except Exception as e:
                print(f"[W{worker_id}] ошибка на {item.id}: {e}")
            finally:
                self.queue.task_done()

# Использование:
async def image_resizer(image_data: bytes) -> str:
    """Имитация обработки изображения."""
    await asyncio.sleep(0.5)  # Имитация CPU + I/O работы
    return f"resized_{len(image_data)}_bytes"

async def main():
    pool = AsyncWorkerPool(
        worker_count=4,
        handler=image_resizer,
        queue_size=20,
    )
    await pool.start()

    # Отправляем 50 изображений на обработку
    for i in range(50):
        await pool.submit(f"image_{i}_data".encode())
        print(f"Отправлено изображение {i}")

    await pool.stop()
    print("Все изображения обработаны")

asyncio.run(main())
```

### 3. Rate Limiting с семафорами

```python
import asyncio
import time
from collections import deque
from typing import Callable, Awaitable, TypeVar

T = TypeVar("T")

class RateLimiter:
    """Ограничитель частоты запросов: не более N запросов в секунду."""

    def __init__(self, max_rate: int, time_window: float = 1.0):
        self.max_rate = max_rate
        self.time_window = time_window
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Дождаться разрешения на выполнение запроса."""
        async with self._lock:
            now = time.monotonic()

            # Удаляем старые временные метки
            while self._timestamps and self._timestamps[0] < now - self.time_window:
                self._timestamps.popleft()

            if len(self._timestamps) >= self.max_rate:
                # Ждём, пока не освободится слот
                wait_time = self._timestamps[0] + self.time_window - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                # Рекурсивно повторяем после ожидания
                return await self.acquire()

            self._timestamps.append(now)

    async def call(self, coro_factory: Callable[[], Awaitable[T]]) -> T:
        """Выполнить корутину с соблюдением лимита."""
        await self.acquire()
        return await coro_factory()


# Использование:
async def api_request(id: int) -> str:
    """Имитация запроса к API."""
    await asyncio.sleep(0.1)
    return f"result_{id}"

async def main():
    limiter = RateLimiter(max_rate=5)  # 5 запросов в секунду

    start = time.perf_counter()
    tasks = [
        limiter.call(lambda i=i: api_request(i))
        for i in range(20)
    ]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start

    print(f"20 запросов, лимит 5/сек: {elapsed:.2f} сек")
    # Должно быть примерно 4 секунды (20/5 = 4)
    print(f"Результаты: {len(results)}")

asyncio.run(main())
```

### 4. Graceful Shutdown

Корректное завершение асинхронной системы — одна из самых сложных задач:

```python
import asyncio
import signal
from typing import Any

class AsyncService:
    """Асинхронный сервис с graceful shutdown."""

    def __init__(self):
        self.queue: asyncio.Queue[Any] = asyncio.Queue()
        self._tasks: list[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()
        self._running = False

    async def start(self):
        """Запустить сервис."""
        self._running = True
        print("Сервис запущен")

        # Запускаем обработчики
        self._tasks = [
            asyncio.create_task(self._handler(i))
            for i in range(3)
        ]
        self._tasks.append(asyncio.create_task(self._producer()))

    async def stop(self):
        """Остановить сервис (graceful)."""
        print("Начинаю graceful shutdown...")
        self._running = False
        self._shutdown_event.set()

        # Ждём, пока очередь опустеет (с таймаутом)
        try:
            await asyncio.wait_for(self.queue.join(), timeout=5.0)
        except asyncio.TimeoutError:
            print("Таймаут graceful shutdown — принудительная отмена")

        # Отменяем все задачи
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Ждём отмену с таймаутом
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._tasks, return_exceptions=True),
                timeout=3.0,
            )
        except asyncio.TimeoutError:
            print("Некоторые задачи не завершились вовремя")

        print("Сервис остановлен")

    async def _producer(self):
        """Производитель: генерирует данные."""
        count = 0
        while self._running:
            await asyncio.sleep(0.1)
            await self.queue.put(f"data-{count}")
            count += 1
        # После остановки кладём сторожей
        for _ in self._tasks[:-1]:  # По одному на обработчик
            await self.queue.put(None)

    async def _handler(self, worker_id: int):
        """Обработчик: читает из очереди."""
        while True:
            try:
                item = await self.queue.get()
                if item is None:
                    self.queue.task_done()
                    print(f"Обработчик {worker_id} завершил работу")
                    break
                await asyncio.sleep(0.2)
                print(f"[W{worker_id}] обработал: {item}")
                self.queue.task_done()
            except asyncio.CancelledError:
                print(f"Обработчик {worker_id} отменён")
                raise


async def main():
    service = AsyncService()

    # Обработка сигналов (Ctrl+C)
    loop = asyncio.get_running_loop()

    def signal_handler():
        print("\nПолучен сигнал остановки")
        asyncio.create_task(service.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows не поддерживает add_signal_handler
            pass

    await service.start()

    # Имитация работы в течение 3 секунд
    await asyncio.sleep(3)
    await service.stop()

asyncio.run(main())
```

### 5. Микширование async и sync кода: run_in_executor

#### Проблема: блокирующий код в Event Loop

```python
# ❌ Антипаттерн: блокировка Event Loop синхронным кодом
async def bad_handler():
    import time
    # time.sleep() БЛОКИРУЕТ весь Event Loop!
    time.sleep(5)  # Все остальные корутины заморожены на 5 сек
    return "Готово"

# ✅ Идиоматично: вынос блокирующего кода в поток
async def good_handler():
    loop = asyncio.get_running_loop()
    # Выполнить в отдельном потоке — Event Loop не блокируется
    result = await loop.run_in_executor(None, blocking_function)
    return result

def blocking_function():
    import time
    time.sleep(5)  # Блокирует поток, но не Event Loop
    return "Готово"
```

#### Варианты run_in_executor

```python
import concurrent.futures
import asyncio

# 1. ThreadPoolExecutor (по умолчанию)
async def run_in_thread():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,  # None = default ThreadPoolExecutor
        cpu_intensive_task,
    )
    return result

# 2. ProcessPoolExecutor (для CPU-bound)
async def run_in_process():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(
            pool,
            cpu_intensive_task,
        )
    return result

# 3. Собственный пул (переиспользуемый)
async def run_in_custom_pool():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        tasks = [
            loop.run_in_executor(pool, blocking_io, url)
            for url in urls
        ]
        results = await asyncio.gather(*tasks)
    return results
```

**Когда использовать `run_in_executor`**:
- Синхронные библиотеки без асинхронных аналогов (например, `requests`);
- CPU-bound операции (лучше `ProcessPoolExecutor`);
- Блокирующий файловый I/O на Linux;
- Синхронные драйверы баз данных.

### 6. Реальные примеры

#### 6.1 Асинхронный HTTP-клиент с aiohttp и rate limiting

```python
import asyncio
import aiohttp
from typing import Any

class AsyncHTTPClient:
    """Асинхронный HTTP-клиент с rate limiting и retry."""

    def __init__(
        self,
        max_concurrent: int = 10,
        max_rate: int = 50,  # запросов в секунду
        max_retries: int = 3,
    ):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._rate_limiter = RateLimiter(max_rate)
        self._max_retries = max_retries
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "AsyncPythonCourse/1.0"},
        )
        return self

    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()

    async def fetch(self, url: str) -> dict[str, Any]:
        """Получить URL с retry и rate limiting."""
        async with self._semaphore:
            for attempt in range(self._max_retries):
                try:
                    await self._rate_limiter.acquire()
                    async with self._session.get(url) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return {"url": url, "status": resp.status, "data": data}
                except aiohttp.ClientError as e:
                    if attempt == self._max_retries - 1:
                        return {"url": url, "error": str(e)}
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
            return {"url": url, "error": "max_retries_exceeded"}

    async def fetch_many(self, urls: list[str]) -> list[dict[str, Any]]:
        """Конкурентно получить много URL."""
        tasks = [self.fetch(url) for url in urls]
        return await asyncio.gather(*tasks)


async def main():
    async with AsyncHTTPClient(max_concurrent=5, max_rate=10) as client:
        urls = [
            f"https://httpbin.org/get?id={i}"
            for i in range(20)
        ]
        results = await client.fetch_many(urls)
        success = sum(1 for r in results if "error" not in r)
        print(f"Успешно: {success}/{len(results)}")

asyncio.run(main())
```

#### 6.2 Асинхронный доступ к БД с asyncpg

```python
import asyncio
import asyncpg

async def init_db(pool: asyncpg.Pool):
    """Инициализация схемы БД."""
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

async def bulk_insert_users(
    pool: asyncpg.Pool,
    users: list[dict[str, str]],
) -> int:
    """Массовая вставка пользователей с конкурентностью."""
    async def insert_one(user: dict) -> int:
        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """INSERT INTO users (name, email)
                       VALUES ($1, $2)
                       ON CONFLICT (email) DO NOTHING
                       RETURNING id""",
                    user["name"],
                    user["email"],
                )
                return row["id"] if row else 0

    tasks = [insert_one(u) for u in users]
    ids = await asyncio.gather(*tasks)
    return sum(1 for i in ids if i > 0)


async def get_users_by_domain(
    pool: asyncpg.Pool,
    domain: str,
) -> list[dict]:
    """Получить пользователей по домену email."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, email FROM users WHERE email LIKE $1",
            f"%@{domain}",
        )
        return [dict(row) for row in rows]


async def main():
    # Создаём пул соединений
    async with asyncpg.create_pool(
        dsn="postgresql://postgres:secret@localhost:5432/mydb",
        min_size=5,
        max_size=20,
    ) as pool:
        await init_db(pool)

        # Вставляем пользователей
        users = [
            {"name": f"User_{i}", "email": f"user{i}@example.com"}
            for i in range(100)
        ]
        inserted = await bulk_insert_users(pool, users)
        print(f"Вставлено: {inserted}")

        # Получаем пользователей
        domain_users = await get_users_by_domain(pool, "example.com")
        print(f"example.com: {len(domain_users)} пользователей")

asyncio.run(main())
```

### 7. Распространённые ошибки (anti-patterns)

#### Ошибка 1: Блокировка Event Loop

```python
# ❌ Синхронный sleep
async def bad():
    import time
    time.sleep(5)  # Блокирует Event Loop на 5 секунд!

# ❌ Синхронный HTTP-запрос
async def bad_http():
    import requests
    resp = requests.get("https://httpbin.org/get")  # Блокирует!

# ❌ Тяжёлые вычисления
async def bad_cpu():
    sum(i * i for i in range(10_000_000))  # Блокирует!

# ✅ Исправление
async def good():
    await asyncio.sleep(5)  # Не блокирует
    # или:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, blocking_func)
```

#### Ошибка 2: Забытый await

```python
# ❌ Корутина не запущена — результат не получен
async def bad():
    result = fetch_data()  # coroutine object, не результат!
    print(result)  # <coroutine object fetch_data at 0x...>

# ✅ Исправление
async def good():
    result = await fetch_data()
    print(result)  # Реальные данные
```

#### Ошибка 3: Потерянные Task

```python
# ❌ Task создан, но ссылка не сохранена
async def bad():
    asyncio.create_task(long_operation())  # Может быть собран GC!
    # Или: Task не дожидается — возможна потеря результата/ошибки

# ✅ Исправление
async def good():
    task = asyncio.create_task(long_operation())
    # ... другая работа ...
    await task  # Явно дожидаемся

# ✅ Или TaskGroup
async def better():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(long_operation())
```

#### Ошибка 4: async без await

```python
# ❌ async-функция без await — бессмысленна
async def bad():
    return 42  # Это синхронная функция с async-обёрткой

# ✅ Исправление: либо убрать async, либо добавить await
def good_sync():
    return 42

async def good_async():
    await asyncio.sleep(0)
    return 42
```

#### Ошибка 5: Слишком много конкурентных задач

```python
# ❌ 100 000 одновременных Task — перегрузка Event Loop
async def bad():
    tasks = [
        asyncio.create_task(process(item))
        for item in huge_list  # 100 000 элементов
    ]
    await asyncio.gather(*tasks)

# ✅ Исправление: семафор или пул
async def better():
    sem = asyncio.Semaphore(100)  # Максимум 100 одновременно
    async def limited(item):
        async with sem:
            return await process(item)

    tasks = [limited(item) for item in huge_list]
    await asyncio.gather(*tasks)
```

### 8. Сравнение с другими языками

#### JavaScript: Worker Threads

```javascript
// Node.js Worker Threads — аналог run_in_executor
const { Worker } = require('worker_threads');

function runInWorker(workerData) {
    return new Promise((resolve, reject) => {
        const worker = new Worker('./worker.js', { workerData });
        worker.on('message', resolve);
        worker.on('error', reject);
    });
}

// Обратите внимание: в JS нет GIL, Worker Threads — для CPU-bound
```

#### Java: ExecutorService

```java
// Java ExecutorService — богатый API для управления потоками
ExecutorService executor = Executors.newFixedThreadPool(10);

// Асинхронное выполнение с Future
Future<String> future = executor.submit(() -> {
    Thread.sleep(5000);  // Блокирует поток, но не основной
    return "result";
});

// Отмена задачи
future.cancel(true);

// Пул с таймаутом
executor.awaitTermination(5, TimeUnit.SECONDS);
executor.shutdownNow();
```

**Сравнение с Python**: `ExecutorService` в Java — это полноценный менеджер
потоков с богатым API для управления жизненным циклом, стратегиями очередей
и отклонения задач. В Python `run_in_executor` — минималистичный мост между
async и sync мирами.

#### Go: горутины и каналы

```go
// Go: горутины + каналы — очень похоже на asyncio.Queue
func producer(ch chan<- string, n int) {
    for i := 0; i < n; i++ {
        time.Sleep(100 * time.Millisecond)
        ch <- fmt.Sprintf("item-%d", i)
    }
    close(ch)
}

func consumer(ch <-chan string, name string) {
    for item := range ch {
        time.Sleep(200 * time.Millisecond)
        fmt.Printf("%s: %s\n", name, item)
    }
}

func main() {
    ch := make(chan string, 10)  // Буферизированный канал
    go producer(ch, 10)
    go consumer(ch, "C1")
    go consumer(ch, "C2")
    time.Sleep(5 * time.Second)
}
```

**Сравнение с Python**:

| Характеристика | Python asyncio | Go |
|:---|---:|---|
| Модель | Кооперативная (один поток) | Вытесняющая (M:N, горутины) |
| Каналы/Очереди | `asyncio.Queue` | `chan` |
| Завершение | `None`-сторож | `close(channel)` |
| Параллелизм | Нет (GIL) | Да (горутины на разных ядрах) |
| Backpressure | `maxsize` в Queue | `make(chan T, size)` |

---

## Практическое задание

### Упражнение 1: Асинхронный веб-скрапер

Напишите асинхронный скрапер, который:
- Получает список URL из входной очереди;
- Скачивает каждый URL с ограничением в 5 одновременных запросов;
- Извлекает заголовок страницы (title tag);
- Результаты кладёт в выходную очередь;
- Использует pattern Producer-Consumer с двумя очередями.

```python
# template/01_web_scraper.py
import asyncio
import re
from dataclasses import dataclass

@dataclass
class ScrapeResult:
    url: str
    title: str | None = None
    error: str | None = None

async def scraper_worker(
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    semaphore: asyncio.Semaphore,
    worker_id: int,
):
    """Обработчик: берёт URL из input_queue, кладёт результат в output_queue."""
    # Ваш код:
    # 1. Взять URL из input_queue (сторож: None)
    # 2. Подождать семафор
    # 3. Сделать «запрос» (asyncio.sleep + имитация парсинга)
    # 4. Положить ScrapeResult в output_queue
    pass

async def main():
    urls = [f"https://example.com/page/{i}" for i in range(30)]
    # Ваш код: создать очереди, запустить воркеров, собрать результаты
    pass

asyncio.run(main())
```

### Упражнение 2: Rate Limiter с временным окном

Реализуйте `SlidingWindowRateLimiter`, который:
- Ограничивает количество запросов в скользящем окне (например, 100 запросов
  за последние 60 секунд);
- Использует `deque` для хранения временных меток;
- Корректно работает с конкурентными вызовами (использует `asyncio.Lock`);
- Возвращает примерное время ожидания, если лимит исчерпан.

```python
# template/02_sliding_window.py
import asyncio
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> float:
        """Попытаться получить разрешение.
        Возвращает время ожидания (0 если можно сразу)."""
        # Ваш код
        pass

    async def wait_and_acquire(self) -> None:
        """Дождаться разрешения."""
        # Ваш код
        pass
```

### Упражнение 3: Graceful Shutdown с drain

Реализуйте функцию `graceful_shutdown`, которая:
- Принимает список `asyncio.Task`;
- Отменяет их все;
- Ждёт завершения с таймаутом 5 секунд;
- Если таймаут истёк — принудительно завершает event loop;
- Логирует состояние каждой задачи (успех, ошибка, отмена, таймаут).

```python
# template/03_graceful_shutdown.py
import asyncio
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class ShutdownReport:
    task_name: str
    status: TaskStatus
    result: object = None
    error: str | None = None

async def graceful_shutdown(
    tasks: list[asyncio.Task],
    timeout: float = 5.0,
) -> list[ShutdownReport]:
    """Graceful shutdown: отменить задачи и собрать отчёт."""
    # Ваш код
    pass
```

### Упражнение 4: Асинхронный конвейер (Pipeline)

Постройте асинхронный конвейер обработки данных из трёх стадий:
1. **Stage 1 (Reader)**: читает «данные» (генерирует числа);
2. **Stage 2 (Processor)**: преобразует (возводит в квадрат) с задержкой;
3. **Stage 3 (Writer)**: «сохраняет» результат (логирует).

Каждая стадия — отдельная корутина. Стадии соединены через `asyncio.Queue`.
Реализуйте backpressure и корректное завершение конвейера.

```python
# template/04_pipeline.py
import asyncio

async def stage_reader(output: asyncio.Queue, n: int):
    """Генерирует числа от 1 до n."""
    pass

async def stage_processor(
    input_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    worker_id: int,
):
    """Возводит в квадрат с задержкой."""
    pass

async def stage_writer(input_queue: asyncio.Queue):
    """Логирует результаты."""
    pass

async def run_pipeline(n: int, processor_count: int):
    """Запустить конвейер."""
    # Ваш код:
    # 1. Создать 2 очереди (reader→processor, processor→writer)
    # 2. Запустить reader, N процессоров, writer
    # 3. Дождаться завершения reader
    # 4. Дождаться, пока очередь processor опустеет
    # 5. Отправить сторожей процессорам
    # 6. Дождаться процессоров
    # 7. Отправить сторожа writer
    # 8. Дождаться writer
    pass

asyncio.run(run_pipeline(50, processor_count=4))
```

---

## Дополнительные материалы

### Книги
- **«Python Concurrency with asyncio»** (Matthew Fowler) — главы 7-10: очереди,
  producer-consumer, graceful shutdown, интеграция с sync-кодом.
- **«Using Asyncio in Python»** (Caleb Hattingh) — глава 5: «Real-World Asyncio».
- **«Architecture Patterns with Python»** (Harry Percival, Bob Gregory) — глава
  об асинхронных паттернах и message buses.

### Статьи и доклады
- **Nathaniel J. Smith: «Notes on structured concurrency»** — теория,
  стоящая за TaskGroup и graceful shutdown.
- **Lynn Root: «asyncio: We Did It Wrong»** (PyCon 2019) — разбор реальных
  ошибок в production asyncio-коде.
- **Andrew Svetlov: «asyncio in Production»** — практические советы по
  развёртыванию asyncio-сервисов.

### Инструменты
- **`asyncio.Task.all_tasks()`** — получить все активные задачи (для отладки).
- **`loop.slow_callback_duration`** — установить порог для обнаружения
  медленных колбеков (Python 3.11+).
- **`PYTHONASYNCIODEBUG=1`** — режим отладки asyncio (медленные колбеки,
  незакрытые транспорты).
- **`aiomonitor`** — мониторинг asyncio-приложений в реальном времени.
- **`aiohttp-devtools`** — инструменты разработчика для aiohttp.

### Что дальше?

Вы завершили курс «Async Python»! Теперь вы знаете:
- Как работает GIL и почему asyncio — правильный выбор для I/O-bound задач;
- Синтаксис `async`/`await` и механику корутин;
- Управление задачами: `Task`, `gather`, `wait`, отмена, таймауты;
- Асинхронные контекстные менеджеры и итераторы;
- Паттерны: producer-consumer, worker pool, rate limiting, graceful shutdown.

**Рекомендуемый путь дальше**:
1. **FastAPI** — асинхронный веб-фреймворк (строится на asyncio);
2. **SQLAlchemy 2.0** — асинхронный ORM с async/await;
3. **Celery** vs **arq** — сравнение синхронных и асинхронных очередей задач;
4. **uvloop** — замена event loop на основе libuv (быстрее в 2-4 раза);
5. **Trio** — альтернативная библиотека с structured concurrency как
   философией по умолчанию.