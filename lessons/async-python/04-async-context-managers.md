---
title: "Асинхронные контекстные менеджеры и итераторы"
order: 4
tags: ["async-with", "async-for", "контекстные-менеджеры", "итераторы"]
prerequisites: "Урок 3, контекстные менеджеры"
objective: "Освоить асинхронные контекстные менеджеры и асинхронную итерацию"
---

# Асинхронные контекстные менеджеры и итераторы

## Введение

В синхронном мире Python мы используем `with` для гарантированного освобождения
ресурсов и `for` для итерации. Но в асинхронном мире открытие и закрытие ресурса
может быть асинхронной операцией — например, установка TCP-соединения или
аутентификация в базе данных.

В этом уроке мы разберём:
- `async with` и протокол `__aenter__` / `__aexit__`;
- Создание собственных асинхронных контекстных менеджеров;
- `async for` и протокол `__aiter__` / `__anext__`;
- Асинхронные генераторы (`async def` + `yield`);
- Примитивы синхронизации: `asyncio.Lock`, `Semaphore`, `Event`, `Condition`;
- Реальные примеры: aiohttp сессии, asyncpg транзакции, aiofiles.

К концу урока вы будете уверенно управлять асинхронными ресурсами и итерацией
в коде на asyncio.

---

## Основная часть

### 1. async with: протокол __aenter__ / __aexit__

#### Синхронный контекстный менеджер (напоминание)

```python
class SyncConnection:
    def __enter__(self):
        print("Открываем соединение...")
        self.conn = self._connect()  # Блокирующая операция
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Закрываем соединение...")
        self.conn.close()
        return False  # Не подавляем исключения

with SyncConnection() as conn:
    conn.send("данные")
# Здесь соединение гарантированно закрыто
```

#### Асинхронный контекстный менеджер

```python
import asyncio

class AsyncConnection:
    async def __aenter__(self):
        print("Асинхронно открываем соединение...")
        await asyncio.sleep(0.1)  # Имитация TCP handshake
        self.conn = "connected"
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Асинхронно закрываем соединение...")
        await asyncio.sleep(0.05)  # Имитация graceful close
        self.conn = None
        return False  # Не подавляем исключения

async def main():
    async with AsyncConnection() as conn:
        print(f"Работаем с: {conn}")
        # Может быть исключение — __aexit__ всё равно вызовется
    print("Соединение закрыто")

asyncio.run(main())
```

#### Протокол __aexit__ подробно

`__aexit__` получает три аргумента (как и синхронный `__exit__`):
- `exc_type` — тип исключения (или `None`, если не было);
- `exc_val` — значение исключения;
- `exc_tb` — traceback.

Возвращает `True`, чтобы подавить исключение, или `False` (и другие falsy
значения), чтобы пробросить его дальше.

```python
class SuppressErrors:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Подавляем ошибку: {exc_val}")
            return True  # Подавляем исключение
        return False

async def main():
    async with SuppressErrors():
        raise ValueError("Что-то пошло не так")
    print("Продолжаем выполнение!")  # Достижимо!
```

### 2. Создание асинхронных контекстных менеджеров

#### Способ 1: Класс с __aenter__ / __aexit__

```python
class AsyncDatabaseSession:
    """Асинхронная сессия базы данных."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._conn = None

    async def __aenter__(self):
        print(f"Подключаюсь к {self.dsn}...")
        await asyncio.sleep(0.2)  # Имитация подключения
        self._conn = {"dsn": self.dsn, "id": id(self)}
        print("Подключено")
        return self._conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            print("Закрываю соединение...")
            await asyncio.sleep(0.1)  # Имитация закрытия

            if exc_type is not None:
                print(f"Откатываю транзакцию из-за: {exc_val}")
                await asyncio.sleep(0.05)  # ROLLBACK
            else:
                print("Коммичу транзакцию")
                await asyncio.sleep(0.05)  # COMMIT

            self._conn = None
        return False

async def main():
    async with AsyncDatabaseSession("postgresql://localhost/mydb") as conn:
        print(f"Выполняю запросы через: {conn['id']}")
        # Если здесь исключение — произойдёт автоматический ROLLBACK
```

#### Способ 2: asynccontextmanager декоратор

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def database_session(dsn: str):
    """Асинхронный контекстный менеджер через декоратор."""
    print(f"Подключаюсь к {dsn}...")
    await asyncio.sleep(0.2)
    conn = {"dsn": dsn, "id": id(dsn)}
    print("Подключено")

    try:
        yield conn  # Тело async with выполняется здесь
        print("Коммит транзакции")
        await asyncio.sleep(0.05)
    except Exception:
        print("Откат транзакции")
        await asyncio.sleep(0.05)
        raise  # Пробрасываем исключение
    finally:
        print("Закрываю соединение...")
        await asyncio.sleep(0.1)

async def main():
    async with database_session("postgresql://localhost/mydb") as conn:
        print(f"Работаю с: {conn}")
```

**Правило**: `@asynccontextmanager` — предпочтительный способ для простых
менеджеров. Класс — когда нужна сложная логика или состояние.

#### Способ 3: contextlib.AsyncExitStack

```python
from contextlib import AsyncExitStack

async def main():
    async with AsyncExitStack() as stack:
        # Регистрируем несколько ресурсов — все будут закрыты при выходе
        conn1 = await stack.enter_async_context(AsyncDatabaseSession("db1"))
        conn2 = await stack.enter_async_context(AsyncDatabaseSession("db2"))

        # Можно также зарегистрировать callback для очистки
        stack.push_async_callback(lambda: asyncio.sleep(0.1))

        print(f"Работаю с {conn1} и {conn2}")
    # Все три ресурса закрыты в обратном порядке (LIFO)
```

### 3. async for: протокол __aiter__ / __anext__

#### Синхронный итератор (напоминание)

```python
class Countdown:
    def __init__(self, start: int):
        self.start = start

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in Countdown(5):
    print(n)  # 5, 4, 3, 2, 1
```

#### Асинхронный итератор

```python
class AsyncCountdown:
    def __init__(self, start: int):
        self.start = start

    def __aiter__(self):
        self.current = self.start
        return self

    async def __anext__(self):
        if self.current <= 0:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)  # Асинхронная операция между элементами
        value = self.current
        self.current -= 1
        return value

async def main():
    async for n in AsyncCountdown(5):
        print(n)  # 5, 4, 3, 2, 1 — с паузой 0.1 сек между
```

#### Асинхронный генератор (async def + yield)

Самый простой способ создать асинхронный итератор:

```python
async def async_countdown(start: int):
    """Асинхронный генератор: yield с await внутри."""
    for i in range(start, 0, -1):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for n in async_countdown(5):
        print(n)

    # Асинхронное списковое включение (Python 3.6+)
    squares = [n * n async for n in async_countdown(3)]
    print(squares)  # [9, 4, 1]
```

**Важные свойства асинхронных генераторов**:
- `yield` приостанавливает генератор (как в синхронном);
- `await` внутри приостанавливает на время ожидания;
- Автоматически реализуют `__aiter__` и `__anext__`;
- Поддерживают `async for` и `async comprehensions`;
- Не могут содержать `return value` (только пустой `return`).

```python
# ❌ Антипаттерн: return с значением в async-генераторе
async def bad_generator():
    yield 1
    return "done"  # SyntaxError в Python < 3.12, игнорируется в 3.12+

# ✅ Идиоматично: просто yield
async def good_generator():
    yield 1
    yield 2
    # Завершается с StopAsyncIteration
```

### 4. Примитивы синхронизации asyncio

#### asyncio.Lock

```python
# asyncio.Lock — асинхронный аналог threading.Lock
# Гарантирует, что только одна корутина входит в критическую секцию

shared_counter = 0
lock = asyncio.Lock()

async def safe_increment():
    global shared_counter
    async with lock:  # Ждём, пока lock освободится
        current = shared_counter
        await asyncio.sleep(0.01)  # Имитация работы
        shared_counter = current + 1

async def main():
    tasks = [asyncio.create_task(safe_increment()) for _ in range(100)]
    await asyncio.gather(*tasks)
    print(shared_counter)  # 100 — всегда!
```

**Важно**: `asyncio.Lock` не защищает от гонок в многопоточном коде. Он работает
только внутри одного Event Loop. Для межпоточной синхронизации используйте
`threading.Lock`.

#### asyncio.Semaphore

```python
# Ограничивает количество корутин, одновременно выполняющих операцию
semaphore = asyncio.Semaphore(5)  # Максимум 5 одновременных запросов

async def rate_limited_request(url: str):
    async with semaphore:
        print(f"Запрашиваю {url}")
        await asyncio.sleep(1)  # Имитация запроса
        return f"Ответ от {url}"

async def main():
    urls = [f"https://api.example.com/{i}" for i in range(50)]
    tasks = [rate_limited_request(url) for url in urls]
    results = await asyncio.gather(*tasks)
    # 50 запросов, но не более 5 одновременно
```

#### asyncio.Event

```python
# Позволяет корутинам ждать события
event = asyncio.Event()

async def waiter(name: str):
    print(f"{name} ждёт события...")
    await event.wait()  # Блокируется, пока event не будет установлен
    print(f"{name} получил событие!")

async def setter():
    await asyncio.sleep(2)
    print("Устанавливаю событие")
    event.set()  # Все wait() разблокируются

async def main():
    tasks = [asyncio.create_task(waiter(f"W{i}")) for i in range(3)]
    tasks.append(asyncio.create_task(setter()))
    await asyncio.gather(*tasks)
```

#### asyncio.Condition

```python
# Более сложный примитив: ждать условие с уведомлением
condition = asyncio.Condition()
items = []

async def producer():
    for i in range(5):
        await asyncio.sleep(0.5)
        async with condition:
            items.append(i)
            print(f"Произведено: {i}")
            condition.notify(1)  # Разбудить одного потребителя

async def consumer(name: str):
    while True:
        async with condition:
            while not items:
                await condition.wait()  # Ждать уведомления
            item = items.pop(0)
            print(f"{name} потребил: {item}")
        if item == 4:
            break

async def main():
    await asyncio.gather(
        producer(),
        consumer("C1"),
        consumer("C2"),
    )
```

### 5. Реальные примеры использования

#### 5.1 aiohttp: асинхронная HTTP-сессия

```python
import aiohttp
import asyncio

async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    """Получить содержимое URL через асинхронную сессию."""
    async with session.get(url) as response:
        # session.get возвращает контекстный менеджер
        return await response.text()

async def main():
    # ClientSession — асинхронный контекстный менеджер
    async with aiohttp.ClientSession() as session:
        urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
        ]
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for url, text in zip(urls, results):
            print(f"{url}: {len(text)} байт")
    # Здесь сессия закрыта — все соединения освобождены

asyncio.run(main())
```

**Почему это важно**: `aiohttp.ClientSession` переиспользует TCP-соединения
(connection pooling). Если не закрыть сессию через `async with`, соединения
«утекут» — это приведёт к исчерпанию сокетов.

#### 5.2 asyncpg: асинхронный PostgreSQL

```python
import asyncpg
import asyncio

async def get_users(conn: asyncpg.Connection, min_age: int):
    """Получить пользователей старше min_age."""
    async with conn.transaction():
        # Транзакция: автоматический BEGIN/COMMIT/ROLLBACK
        rows = await conn.fetch(
            "SELECT id, name, age FROM users WHERE age > $1",
            min_age,
        )
        return [dict(row) for row in rows]

async def main():
    # asyncpg.Connection — асинхронный контекстный менеджер
    async with asyncpg.connect(
        user="postgres",
        password="secret",
        database="mydb",
        host="localhost",
    ) as conn:
        users = await get_users(conn, 18)
        print(f"Найдено {len(users)} пользователей")
    # Соединение закрыто

asyncio.run(main())
```

#### 5.3 aiofiles: асинхронная работа с файлами

```python
import aiofiles
import asyncio

async def process_logs(filepath: str):
    """Асинхронно читать большой файл построчно."""
    async with aiofiles.open(filepath, mode="r") as f:
        async for line in f:  # Асинхронная итерация по строкам
            line = line.strip()
            if line:
                # Обработка строки
                await asyncio.sleep(0)  # Дать другим задачам шанс
                print(f"Строка: {line[:50]}...")

# ВНИМАНИЕ: aiofiles использует потоки под капотом (run_in_executor)
# Настоящего асинхронного файлового I/O в Python пока нет
```

**Важное предупреждение**: на Linux/macOS файловый I/O **всегда блокирующий** на
уровне ядра (нет настоящего `O_NONBLOCK` для обычных файлов). `aiofiles` и
`aiofile` используют пул потоков (`run_in_executor`) для эмуляции асинхронности.
Это нормально для asyncio, но важно понимать ограничение.

#### 5.4 Собственный пул соединений

```python
class AsyncConnectionPool:
    """Асинхронный пул соединений с ограничением."""

    def __init__(self, dsn: str, max_size: int = 10):
        self.dsn = dsn
        self.max_size = max_size
        self._semaphore = asyncio.Semaphore(max_size)
        self._pool: list[dict] = []
        self._in_use: set[int] = set()

    async def acquire(self):
        await self._semaphore.acquire()
        # Ищем свободное соединение или создаём новое
        if self._pool:
            conn = self._pool.pop()
        else:
            conn = await self._create_connection()
        self._in_use.add(id(conn))
        return conn

    async def release(self, conn):
        self._in_use.discard(id(conn))
        self._pool.append(conn)
        self._semaphore.release()

    async def _create_connection(self):
        await asyncio.sleep(0.1)  # Имитация подключения
        return {"dsn": self.dsn, "id": id(self)}

    @asynccontextmanager
    async def connection(self):
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)

# Использование:
async def main():
    pool = AsyncConnectionPool("postgresql://localhost/mydb", max_size=5)
    async with pool.connection() as conn:
        print(f"Использую соединение: {conn}")
```

### 6. Сравнение с другими языками

#### JavaScript: for-await-of

```javascript
// Асинхронный итератор в JavaScript
async function* asyncGenerator() {
    for (let i = 5; i > 0; i--) {
        await new Promise(r => setTimeout(r, 100));
        yield i;
    }
}

// for await...of — аналог async for
for await (const n of asyncGenerator()) {
    console.log(n);  // 5, 4, 3, 2, 1
}

// Асинхронный контекстный менеджер: using (Stage 3, ES202X)
// await using conn = await db.connect();  // Пока proposal
```

**Ключевые отличия**:
- JS: `for await...of` — ключевое слово `await` встроено в синтаксис цикла;
- Python: `async for` — отдельный синтаксис, `for` и `async for` несовместимы;
- JS: нет встроенного асинхронного контекстного менеджера (пока proposal);
- Python: `async with` — полноценный протокол с `__aenter__`/`__aexit__`.

#### C#: IAsyncDisposable и IAsyncEnumerable

```csharp
// Асинхронный контекстный менеджер: IAsyncDisposable
await using (var conn = new DbConnection())
{
    // conn.DisposeAsync() вызовется при выходе
}

// Асинхронная итерация: IAsyncEnumerable
await foreach (var item in GetItemsAsync())
{
    Console.WriteLine(item);
}

// Асинхронный генератор
async IAsyncEnumerable<int> GenerateAsync()
{
    for (int i = 5; i > 0; i--)
    {
        await Task.Delay(100);
        yield return i;
    }
}
```

**C# имеет более богатую встроенную поддержку**: `IAsyncDisposable` и
`IAsyncEnumerable` — часть стандартной библиотеки и компилятора. Python
добавил асинхронные протоколы позже, но они так же хорошо интегрированы.

#### Java: try-with-resources (нет асинхронной версии)

```java
// Java: синхронный try-with-resources — нет асинхронного варианта!
try (var conn = dataSource.getConnection()) {
    // conn.close() вызывается автоматически
    // Но getConnection() — блокирующий вызов
}

// В асинхронном коде приходится вручную:
var conn = dataSource.getConnection();  // Блокирует поток ОС
try {
    // работа с conn
} finally {
    conn.close();
}
```

**Java отстаёт в этой области**: нет асинхронных контекстных менеджеров
на уровне языка. Project Loom частично решает проблему, делая блокирующий
код «лёгким», но идеоматический асинхронный код всё ещё требует ручного
управления ресурсами.

---

## Практическое задание

### Упражнение 1: Асинхронный пул соединений

Реализуйте класс `AsyncPool` — асинхронный контекстный менеджер для управления
пулом объектов:

```python
# template/01_async_pool.py
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, TypeVar

T = TypeVar("T")

class AsyncPool:
    """Асинхронный пул с ограничением на количество одновременных пользователей."""

    def __init__(self, max_size: int = 5):
        self._semaphore = asyncio.BoundedSemaphore(max_size)
        self._resources: list[T] = []

    async def add_resource(self, resource: T) -> None:
        """Добавить ресурс в пул."""
        self._resources.append(resource)

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[T]:
        """Взять ресурс из пула, гарантированно вернуть."""
        # Ваш код: использовать семафор, взять ресурс, вернуть в finally
        pass

# Тест:
async def test():
    pool = AsyncPool[str](max_size=2)
    await pool.add_resource("resource-1")
    await pool.add_resource("resource-2")

    async def worker(name: str):
        async with pool.acquire() as r:
            print(f"{name} взял {r}")
            await asyncio.sleep(0.5)
            print(f"{name} вернул {r}")

    await asyncio.gather(
        worker("A"), worker("B"), worker("C"),  # C ждёт
    )
```

### Упражнение 2: Асинхронный генератор страниц API

Напишите асинхронный генератор `paginated_api`, который:
- Принимает `base_url: str` и `total_pages: int`;
- На каждой итерации делает «запрос» (`await asyncio.sleep`) и возвращает
  `{"page": N, "items": [...]}`;
- Поддерживает повторные попытки при ошибке (до 3 раз);
- Использует семафор для ограничения параллельных запросов (опционально).

```python
# template/02_paginated_api.py
import asyncio
import random
from typing import AsyncIterator

async def paginated_api(
    base_url: str,
    total_pages: int,
    max_retries: int = 3,
) -> AsyncIterator[dict]:
    """Асинхронный генератор для пагинированного API."""
    # Ваш код
    pass

async def main():
    async for page in paginated_api("https://api.example.com/data", total_pages=5):
        print(f"Страница {page['page']}: {len(page['items'])} записей")
```

### Упражнение 3: Асинхронный контекстный менеджер для транзакции

Реализуйте `@asynccontextmanager` для транзакции базы данных:

```python
# template/03_transaction.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

class FakeDB:
    """Имитация асинхронной БД."""
    def __init__(self):
        self.data = {}

    async def execute(self, query: str, **params):
        await asyncio.sleep(0.1)
        print(f"  SQL: {query} | params={params}")
        return "OK"

    async def commit(self):
        await asyncio.sleep(0.05)
        print("  COMMIT")

    async def rollback(self):
        await asyncio.sleep(0.05)
        print("  ROLLBACK")

@asynccontextmanager
async def transaction(db: FakeDB) -> AsyncIterator[FakeDB]:
    """Асинхронный контекстный менеджер для транзакции."""
    # Ваш код:
    # 1. BEGIN (неявно)
    # 2. yield db
    # 3. COMMIT если не было исключений
    # 4. ROLLBACK если было исключение
    pass

async def main():
    db = FakeDB()

    async with transaction(db) as tx:
        await tx.execute("INSERT INTO users VALUES ($1, $2)", name="Alice", age=30)
        await tx.execute("UPDATE users SET age = $1 WHERE name = $2", age=31, name="Alice")
    print("Транзакция закоммичена\n")

    try:
        async with transaction(db) as tx:
            await tx.execute("INSERT INTO users VALUES ($1, $2)", name="Bob", age=25)
            raise ValueError("Что-то пошло не так!")
    except ValueError:
        print("Транзакция откатилась")
```

### Упражнение 4: Асинхронный reader/circular buffer

Реализуйте асинхронный циклический буфер с `async for`:

```python
# template/04_circular_buffer.py
import asyncio
from collections import deque

class AsyncCircularBuffer:
    """Асинхронный циклический буфер: async for читает, push добавляет."""

    def __init__(self, max_size: int, timeout: float | None = None):
        self._buffer = deque(maxlen=max_size)
        self._event = asyncio.Event()
        self._timeout = timeout
        self._closed = False

    def push(self, item):
        """Добавить элемент (синхронный метод)."""
        self._buffer.append(item)
        self._event.set()

    def close(self):
        """Закрыть буфер — больше не будет элементов."""
        self._closed = True
        self._event.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        # Ваш код:
        # 1. Ждать, пока не появится элемент или буфер не закроется
        # 2. Если буфер закрыт и пуст — StopAsyncIteration
        # 3. Иначе вернуть элемент
        pass

# Тест:
async def main():
    buffer = AsyncCircularBuffer(max_size=100)

    async def producer():
        for i in range(5):
            await asyncio.sleep(0.2)
            buffer.push(i)
            print(f"Произведено: {i}")
        buffer.close()

    async def consumer():
        async for item in buffer:
            print(f"Потреблено: {item}")
        print("Буфер закрыт — конец итерации")

    await asyncio.gather(producer(), consumer())
```

---

## Дополнительные материалы

### Книги
- **«Python Concurrency with asyncio»** (Matthew Fowler) — глава 5: «Async Context
  Managers» и глава 6: «Async Iterators and Generators».
- **«Fluent Python»** (Luciano Ramalho, 2-е издание) — глава 21: разделы об
  async with и async for.
- **«Using Asyncio in Python»** (Caleb Hattingh) — глава 4: «Async Context
  Managers and Iterators».

### PEP
- **PEP 492** — Coroutines with async and await (включая async with и async for).
- **PEP 525** — Asynchronous Generators.
- **PEP 530** — Asynchronous Comprehensions.

### Библиотеки
- **aiohttp** — асинхронный HTTP-клиент/сервер (`ClientSession` как async CM).
- **asyncpg** — асинхронный драйвер PostgreSQL (connection и transaction как async CM).
- **aiofiles** — асинхронные файловые операции (async with/for для файлов).
- **aioredis** — асинхронный клиент Redis (async with для подключения).

### Что дальше?

В финальном уроке мы соберём всё вместе и изучим продвинутые асинхронные
паттерны: producer-consumer, очереди, worker pool, rate limiting и реальные
архитектурные примеры.