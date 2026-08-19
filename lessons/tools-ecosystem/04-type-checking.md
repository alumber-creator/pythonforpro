---
title: "Статическая типизация: mypy, type hints, Protocols"
order: 4
tags: ["типизация", "mypy", "type-hints", "Protocol", "Generics"]
prerequisites: "Базовый Python, опыт со статически типизированными языками"
objective: "Освоить систему типов Python: type hints, mypy, протоколы и дженерики"
---

# Статическая типизация: mypy, type hints, Protocols

## Введение

### 🎯 Цель урока

Освоить систему постепенной типизации Python: от базовых type hints до продвинутых дженериков и протоколов. Научиться использовать `mypy` для статической проверки типов и писать код, который документирует себя через аннотации.

### 📋 Предпосылки

- Уверенный Python: функции, классы, декораторы, модули
- Опыт работы со статически типизированными языками (Java, C++, C#, TypeScript) будет полезен
- Урок 3: линтинг и форматирование (базовая настройка mypy)

### Философия постепенной типизации

Python — динамически типизированный язык. Однако с версии 3.5 (PEP 484) в язык добавлены **type hints** — аннотации типов, которые не влияют на выполнение, но позволяют статическим анализаторам проверять корректность кода. Это **постепенная типизация** (gradual typing): вы можете типизировать код по частям, начиная с критических участков.

```python
# Без типов — «динамический» Python
def calculate(x, y):
    return x + y

# С типами — «статический» Python
def calculate(x: int, y: int) -> int:
    return x + y
```

---

## Основная часть

### 1. Базовые type hints (PEP 484)

#### Примитивные типы

```python
# Базовые типы
name: str = "Alice"
age: int = 30
price: float = 99.99
is_active: bool = True
data: bytes = b"hello"

# Аннотации функций
def greet(name: str) -> str:
    return f"Hello, {name}!"

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# None — отдельный тип
def find_user(user_id: int) -> str | None:
    """Возвращает имя пользователя или None, если не найден."""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)
```

#### Коллекции (Python 3.9+)

```python
# До Python 3.9 требовался typing
from typing import List, Dict, Set, Tuple, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

# Python 3.9+: встроенные типы с []
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Все варианты
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
unique_ids: set[int] = {1, 2, 3}
point: tuple[float, float] = (3.0, 4.0)
matrix: list[list[int]] = [[1, 2], [3, 4]]
```

#### Optional и Union

```python
# Optional[X] — это Union[X, None]
from typing import Optional, Union

def get_user_optional(email: str) -> Optional[dict]:
    """Optional — старое, но часто встречается."""
    ...

def get_user_modern(email: str) -> dict | None:
    """Python 3.10+: X | None."""
    ...

# Union — «или»
def parse_value(raw: str) -> int | float | str:
    """Пытается распарсить строку в число, иначе возвращает строку."""
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw
```

### 2. Продвинутые типы

#### Any и NoReturn

```python
from typing import Any, NoReturn

# Any — отключает проверку типов
def deserialize(data: str) -> Any:
    """Парсит JSON — тип результата неизвестен."""
    import json
    return json.loads(data)

# NoReturn — функция никогда не завершается нормально
def fail(message: str) -> NoReturn:
    """Выбрасывает исключение и никогда не возвращает значение."""
    raise RuntimeError(message)

def infinite_loop() -> NoReturn:
    """Бесконечный цикл — никогда не завершается."""
    while True:
        pass
```

#### Callable — функции как тип

```python
from typing import Callable

# Сигнатура: (аргументы) -> возвращаемый тип
Handler = Callable[[str, int], bool]

def register_handler(handler: Handler) -> None:
    ...

def my_handler(name: str, code: int) -> bool:
    return len(name) == code

register_handler(my_handler)  # ✅ OK

# С любым количеством аргументов
Callback = Callable[..., None]

def on_event(callback: Callback) -> None:
    ...
```

#### Literal — точные значения

```python
from typing import Literal

# Только конкретные строки
def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

set_mode("read")    # ✅ OK
set_mode("delete")  # ❌ mypy error

# Часто используется с Union
def create_button(
    style: Literal["primary", "secondary", "danger"],
    size: Literal["small", "medium", "large"],
) -> None:
    ...

# И с bool
def set_flag(flag: Literal[True]) -> None:
    """Принимает ТОЛЬКО True, не bool."""
    ...
```

#### TypedDict — типизированные словари

```python
from typing import TypedDict

class User(TypedDict):
    """Структура пользователя с типами полей."""
    id: int
    name: str
    email: str
    is_active: bool

class UserWithOptional(TypedDict, total=False):
    """Все поля опциональны."""
    id: int
    name: str
    bio: str

def create_user(data: User) -> None:
    """mypy проверит, что все поля User присутствуют."""
    print(f"Creating user {data['name']}...")

# ✅ OK — все поля на месте
create_user({"id": 1, "name": "Alice", "email": "a@b.com", "is_active": True})

# ❌ mypy error: missing 'email'
create_user({"id": 1, "name": "Alice", "is_active": True})
```

#### NamedTuple — типизированные кортежи

```python
from typing import NamedTuple

class Point(NamedTuple):
    """Точка в 2D-пространстве."""
    x: float
    y: float

    def distance(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

class HTTPResponse(NamedTuple):
    status_code: int
    headers: dict[str, str]
    body: bytes

p = Point(3.0, 4.0)
print(p.distance())  # 5.0
print(p.x, p.y)      # 3.0 4.0
```

### 3. Дженерики (Generics)

#### TypeVar — переменные типа

```python
from typing import TypeVar

T = TypeVar("T")            # Любой тип
K = TypeVar("K")            # Ключ
V = TypeVar("V")            # Значение
N = TypeVar("N", int, float)  # Только int или float

def first(items: list[T]) -> T | None:
    """Возвращает первый элемент или None."""
    return items[0] if items else None

def identity(value: T) -> T:
    """Возвращает то же значение того же типа."""
    return value

# mypy выводит типы:
x = first([1, 2, 3])       # x: int | None
y = first(["a", "b", "c"])  # y: str | None
```

#### Generic-классы

```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Stack(Generic[T]):
    """Обобщённый стек — работает с любым типом."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

# Использование
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
# int_stack.push("hello")  # ❌ mypy error

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

```python
class KeyValueStore(Generic[K, V]):
    """Обобщённое хранилище ключ-значение."""

    def __init__(self) -> None:
        self._store: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._store.get(key)

    def set(self, key: K, value: V) -> None:
        self._store[key] = value

    def items(self) -> list[tuple[K, V]]:
        return list(self._store.items())

# Использование
store: KeyValueStore[str, int] = KeyValueStore()
store.set("count", 42)
value = store.get("count")  # value: int | None
```

#### Bounded TypeVar

```python
from typing import TypeVar

# Ограниченный TypeVar: только наследники указанного класса
from collections.abc import Sized

S = TypeVar("S", bound=Sized)

def get_length(obj: S) -> int:
    """Работает с любым объектом, у которого есть __len__."""
    return len(obj)

get_length([1, 2, 3])   # ✅ OK
get_length("hello")      # ✅ OK
get_length({"a": 1})     # ✅ OK
# get_length(42)          # ❌ mypy error: int не имеет __len__
```

### 4. Протоколы (PEP 544) — структурная типизация

Протоколы — это Python-версия «утиной типизации» (duck typing) со статической проверкой. Вместо наследования от абстрактного класса вы описываете интерфейс, и любой класс, который ему соответствует, автоматически подходит.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Flyable(Protocol):
    """Протокол: всё, что может летать."""

    def fly(self, distance: float) -> str:
        """Лететь на указанное расстояние."""
        ...

class Bird:
    def fly(self, distance: float) -> str:
        return f"Flying {distance} km"

class Airplane:
    def fly(self, distance: float) -> str:
        return f"Cruising at {distance} km"

class Fish:
    def swim(self, depth: float) -> str:
        return f"Swimming at {depth} m"

def travel(vehicle: Flyable, distance: float) -> str:
    """Принимает ВСЁ, что реализует Flyable — без наследования!"""
    return vehicle.fly(distance)

travel(Bird(), 10.0)      # ✅ OK
travel(Airplane(), 1000.0)  # ✅ OK
# travel(Fish(), 10.0)       # ❌ mypy error: Fish не имеет fly()
```

#### Реальный пример: SupportsRead

```python
from typing import Protocol

class SupportsRead(Protocol):
    """Протокол для всего, что можно читать."""

    def read(self, size: int = -1) -> str:
        """Читает данные."""
        ...

class FileReader:
    def read(self, size: int = -1) -> str:
        return "file content"

class StringBuffer:
    def read(self, size: int = -1) -> str:
        return "buffer content"

class NetworkStream:
    def read(self, size: int = -1) -> str:
        return "network data"

    def connect(self) -> None:
        ...

def process_data(source: SupportsRead) -> None:
    """Работает с ЛЮБЫМ читаемым источником."""
    content = source.read(1024)
    print(f"Read: {content}")

# Все три работают без общего базового класса!
process_data(FileReader())
process_data(StringBuffer())
process_data(NetworkStream())
```

#### Протоколы с методами и свойствами

```python
from typing import Protocol

class Comparable(Protocol):
    """Протокол для объектов, поддерживающих сравнение."""

    def __lt__(self, other: "Comparable") -> bool: ...
    def __le__(self, other: "Comparable") -> bool: ...
    def __gt__(self, other: "Comparable") -> bool: ...
    def __ge__(self, other: "Comparable") -> bool: ...

class DataStore(Protocol):
    """Протокол хранилища данных."""

    @property
    def is_connected(self) -> bool: ...

    def connect(self, url: str) -> None: ...
    def disconnect(self) -> None: ...
    def execute(self, query: str) -> list[dict]: ...

# Любой класс, реализующий эти методы, совместим с DataStore
```

### 5. Type Narrowing — сужение типов

```python
from typing import Union

def process(value: int | str | list[int]) -> str:
    """Type narrowing через isinstance."""
    if isinstance(value, int):
        # Здесь value: int
        return str(value * 2)
    elif isinstance(value, str):
        # Здесь value: str
        return value.upper()
    else:
        # Здесь value: list[int]
        return ", ".join(str(x) for x in value)

def get_length(value: int | str | None) -> int:
    """Type narrowing через проверку на None."""
    if value is None:
        return 0
    # Здесь value: int | str
    if isinstance(value, int):
        return len(str(value))
    else:
        # Здесь value: str
        return len(value)
```

```python
from typing import assert_never

def handle_status(status: Literal["ok", "error", "pending"]) -> str:
    """Исчерпывающая проверка всех вариантов."""
    if status == "ok":
        return "All good"
    elif status == "error":
        return "Something went wrong"
    elif status == "pending":
        return "Still working..."
    else:
        # Если добавить новый статус, mypy предупредит здесь
        assert_never(status)
```

### 6. Type Guards с `TypeGuard` и `TypeIs`

```python
from typing import TypeGuard

def is_string_list(value: list[object]) -> TypeGuard[list[str]]:
    """Проверяет, что все элементы списка — строки."""
    return all(isinstance(item, str) for item in value)

def process(items: list[object]) -> str:
    if is_string_list(items):
        # Здесь items: list[str] (mypy понимает это!)
        return ", ".join(items)
    return str(items)
```

### 7. Продвинутая конфигурация mypy

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true

# Дополнительные проверки
warn_return_any = true
warn_unused_configs = true
warn_unreachable = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_generics = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
show_error_codes = true
enable_error_code = ["ignore-without-code", "redundant-expr"]

# Сторонние типы
[[tool.mypy.overrides]]
module = [
    "tests.*",
    "docs.*",
]
ignore_errors = true

[[tool.mypy.overrides]]
module = [
    "myproject.migrations.*",
]
ignore_errors = true
```

### 8. Сравнение с экосистемами других языков

#### TypeScript

| Аспект | Python (mypy/pyright) | TypeScript |
|--------|----------------------|------------|
| Философия | Постепенная типизация | Постепенная типизация |
| Проверка типов | Внешний инструмент (mypy) | Компилятор (tsc) |
| Структурная типизация | Protocol | Интерфейсы (по умолчанию) |
| Дженерики | TypeVar, Generic | `<T>` |
| Union Types | `X \| Y` | `X \| Y` |
| Type Narrowing | `isinstance` | `typeof`, `instanceof` |
| Any | `Any` | `any` |
| Unknown | Нет прямого аналога | `unknown` |

```typescript
// TypeScript
function first<T>(items: T[]): T | undefined {
    return items[0];
}

interface Flyable {
    fly(distance: number): string;
}
```

```python
# Python
def first(items: list[T]) -> T | None:
    return items[0] if items else None

class Flyable(Protocol):
    def fly(self, distance: float) -> str: ...
```

#### Java: Generics

| Аспект | Python | Java |
|--------|--------|------|
| Стирание типов | Нет (mypy проверяет) | Да (JVM) |
| Variance | Нет (пока) | `? extends T`, `? super T` |
| Generic-классы | `class Stack(Generic[T])` | `class Stack<T>` |
| Ограничения | `TypeVar('T', bound=Base)` | `<T extends Base>` |
| Wildcards | Нет прямого аналога | `List<? extends Number>` |

```java
// Java
public class Stack<T> {
    private List<T> items = new ArrayList<>();

    public void push(T item) {
        items.add(item);
    }

    public T pop() {
        return items.isEmpty() ? null : items.remove(items.size() - 1);
    }
}
```

```python
# Python
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None
```

#### C++: Templates

| Аспект | Python | C++ |
|--------|--------|-----|
| Механизм | Аннотации (не влияют на runtime) | Генерация кода (компиляция) |
| Проверка | Внешняя (mypy) | Встроенная (компилятор) |
| SFINAE / Concepts | Protocol | Concepts (C++20) |
| Ограничения | TypeVar bound | `requires` clause |

#### C#: Generics

| Аспект | Python | C# |
|--------|--------|-----|
| Reified generics | Нет | Да (рантайм) |
| Ограничения | `TypeVar('T', bound=Base)` | `where T : Base` |
| Контравариантность | Нет | `in T` |
| Ковариантность | Нет | `out T` |

### 9. ✅ Идиоматичное использование

```python
# ✅ ПРАВИЛЬНО: используйте X | Y вместо Union[X, Y] (Python 3.10+)
def process(value: str | int) -> str: ...

# ✅ ПРАВИЛЬНО: используйте list[X] вместо typing.List[X] (Python 3.9+)
def process(items: list[str]) -> None: ...

# ✅ ПРАВИЛЬНО: используйте Protocol для duck typing
class Reader(Protocol):
    def read(self) -> str: ...

# ✅ ПРАВИЛЬНО: используйте TypeVar для обобщённого кода
T = TypeVar("T")
def first(items: list[T]) -> T | None: ...

# ✅ ПРАВИЛЬНО: используйте @override для явного переопределения (Python 3.12+)
from typing import override

class Child(Parent):
    @override
    def method(self) -> str: ...

# ✅ ПРАВИЛЬНО: используйте Final для констант
from typing import Final
MAX_RETRIES: Final = 3
```

### 10. ❌ Антипаттерны

```python
# ❌ НЕПРАВИЛЬНО: Any вместо конкретного типа
def get_user() -> Any:  # Слишком широко
    ...

# ❌ НЕПРАВИЛЬНО: игнорировать ошибки mypy без комментария
result = complex_call()  # type: ignore
# Должно быть:  # type: ignore[attr-defined]  # legacy API, will be fixed in v2

# ❌ НЕПРАВИЛЬНО: Optional вместо Union с None
# Python 3.10+: используйте X | None
def find_user() -> str | None:  # ✅
    ...

# ❌ НЕПРАВИЛЬНО: смешивать старые и новые стили
from typing import List, Optional  # Старый стиль
def process(items: list[str]) -> str | None:  # Новый стиль
    ...
# Выберите один стиль и придерживайтесь его

# ❌ НЕПРАВИЛЬНО: не использовать type narrowing
def process(value: str | int | None) -> str:
    return str(value)  # Пропущена проверка на None!
```

### 11. Когда типизация помогает, а когда избыточна

| Ситуация | Типизировать? | Почему |
|----------|:---:|--------|
| Публичное API библиотеки | ✅ Обязательно | Пользователи ожидают типы |
| Внутренний код проекта | ✅ Рекомендуется | Баги находят раньше |
| Одноразовые скрипты | ❌ Не нужно | Затраты > пользы |
| Прототипирование | ❌ Не нужно | Типы мешают скорости |
| Миграция легаси | ✅ Постепенно | Критические модули в первую очередь |
| Data Science ноутбуки | ⚠️ Опционально | По желанию |

---

## Практическое задание

### Задача: типизировать библиотеку для работы с данными

1. **Создайте проект** с виртуальным окружением:

```bash
mkdir typing-workshop
cd typing-workshop
python -m venv .venv
source .venv/bin/activate
pip install mypy
```

2. **Создайте файл `data_lib.py`** со следующим нетипизированным кодом:

```python
# data_lib.py — БЕЗ типов (версия ДО)
class DataStore:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def all(self):
        return list(self._data.items())


def filter_by(items, predicate):
    return [item for item in items if predicate(item)]


def group_by(items, key_func):
    result = {}
    for item in items:
        k = key_func(item)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


def first(items):
    return items[0] if items else None


def safe_divide(a, b):
    if b == 0:
        return None
    return a / b
```

3. **Типизируйте код**:

```python
# data_lib.py — ПОСЛЕ типизации
from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
R = TypeVar("R")


class DataStore(Generic[K, V]):
    """Обобщённое хранилище данных с типобезопасным доступом."""

    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def set(self, key: K, value: V) -> None:
        """Сохраняет значение по ключу."""
        self._data[key] = value

    def get(self, key: K, default: V | None = None) -> V | None:
        """Возвращает значение по ключу или default."""
        return self._data.get(key, default)

    def all(self) -> list[tuple[K, V]]:
        """Возвращает все пары ключ-значение."""
        return list(self._data.items())


def filter_by(items: list[T], predicate: Callable[[T], bool]) -> list[T]:
    """Фильтрует список по предикату."""
    return [item for item in items if predicate(item)]


def group_by(items: list[T], key_func: Callable[[T], K]) -> dict[K, list[T]]:
    """Группирует элементы по ключу."""
    result: dict[K, list[T]] = {}
    for item in items:
        k = key_func(item)
        if k not in result:
            result[k] = []
        result[k].append(item)
    return result


def first(items: list[T]) -> T | None:
    """Возвращает первый элемент списка или None."""
    return items[0] if items else None


def safe_divide(a: float, b: float) -> float | None:
    """Безопасное деление: возвращает None при делении на ноль."""
    return None if b == 0 else a / b
```

4. **Создайте тестовый файл `test_types.py`**:

```python
"""Проверка типов — должно пройти mypy без ошибок."""
from data_lib import DataStore, filter_by, group_by, first, safe_divide

# Тест DataStore
store: DataStore[str, int] = DataStore()
store.set("count", 42)
store.set("score", 100)
value = store.get("count")  # value: int | None
all_items = store.all()     # all_items: list[tuple[str, int]]

# Проверка типа: несовместимые операции
# store.set("name", 123)    # ✅ OK — int разрешён
# store.set(123, "hello")   # ❌ mypy error — ключ должен быть str

# Тест filter_by
numbers = [1, 2, 3, 4, 5, 6]
evens = filter_by(numbers, lambda x: x % 2 == 0)
# evens: list[int]

words = ["hello", "world", "python", "code"]
long_words = filter_by(words, lambda w: len(w) > 4)
# long_words: list[str]

# Тест group_by
users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "user"},
    {"name": "Charlie", "role": "admin"},
]
grouped = group_by(users, lambda u: u["role"])
# grouped: dict[str, list[dict]]

# Тест first
first_num = first([1, 2, 3])        # first_num: int | None
first_str = first(["a", "b", "c"])   # first_str: str | None
first_empty = first([])              # first_empty: None (тип неизвестен)

# Тест safe_divide
result = safe_divide(10.0, 2.0)  # result: float | None (5.0)
error = safe_divide(10.0, 0.0)   # error: float | None (None)
```

5. **Запустите mypy**:

```bash
mypy --strict data_lib.py test_types.py
```

6. **Создайте протокол** для сериализации:

```python
# serialization.py
from typing import Protocol


class Serializable(Protocol):
    """Протокол: всё, что можно сериализовать в dict."""

    def to_dict(self) -> dict[str, object]:
        """Сериализует объект в словарь."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Serializable":
        """Десериализует объект из словаря."""
        ...


class User:
    """Реализует Serializable без наследования!"""

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "age": self.age}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "User":
        return cls(name=str(data["name"]), age=int(data["age"]))


class Product:
    """Тоже реализует Serializable без наследования!"""

    def __init__(self, title: str, price: float) -> None:
        self.title = title
        self.price = price

    def to_dict(self) -> dict[str, object]:
        return {"title": self.title, "price": self.price}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Product":
        return cls(title=str(data["title"]), price=float(data["price"]))


def save_to_json(obj: Serializable, path: str) -> None:
    """Сохраняет ЛЮБОЙ сериализуемый объект в JSON."""
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj.to_dict(), f, indent=2)


def load_from_json(cls: type[Serializable], path: str) -> Serializable:
    """Загружает ЛЮБОЙ сериализуемый объект из JSON."""
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return cls.from_dict(data)


# Использование
user = User("Alice", 30)
save_to_json(user, "user.json")
loaded_user = load_from_json(User, "user.json")
```

7. **Проверьте протоколы через mypy**:

```bash
mypy --strict serialization.py
```

---

## Дополнительные материалы

### 📚 Официальная документация

- [typing — Support for type hints](https://docs.python.org/3/library/typing.html) — стандартная библиотека типов
- [mypy documentation](https://mypy.readthedocs.io/) — полное руководство
- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) — оригинальное предложение
- [PEP 544 — Protocols](https://peps.python.org/pep-0544/) — структурная типизация
- [PEP 604 — Union types as X | Y](https://peps.python.org/pep-0604/) — новый синтаксис Union
- [PEP 585 — Type Hinting Generics in Standard Collections](https://peps.python.org/pep-0585/) — list[X] вместо List[X]

### 🎥 Видео и статьи

- [Type hints cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) — шпаргалка по type hints
- [Python Type Checking (Real Python)](https://realpython.com/python-type-checking/) — гид по статической типизации
- [Protocols and structural subtyping](https://mypy.readthed.io/en/stable/protocols.html) — mypy о протоколах

### 🔗 Связанные уроки

- **Урок 3**: Линтинг и форматирование — настройка mypy в pre-commit
- **Урок 5**: Документирование кода — типы в docstrings

### 🛠 Альтернативные инструменты

- [pyright](https://github.com/microsoft/pyright) — статический анализатор типов от Microsoft (быстрее mypy)
- [pyre](https://pyre-check.org/) — анализатор типов от Meta (Facebook)

### 💡 Ключевые выводы

1. **Постепенная типизация** — типизируйте то, что критично, пропускайте прототипы
2. **`X | Y`** вместо `Union[X, Y]` — современный Python 3.10+
3. **`list[X]`** вместо `List[X]` — современный Python 3.9+
4. **Protocol** — структурная типизация без наследования
5. **TypeVar** — обобщённое программирование с сохранением типов
6. **Type Narrowing** — mypy понимает `isinstance`, `is None`, `assert`
7. **mypy --strict** — максимальная проверка для продакшен-кода