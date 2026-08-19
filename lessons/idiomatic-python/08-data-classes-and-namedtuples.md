---
title: "Data Classes и Named Tuples: структуры данных без шаблонного кода"
order: 8
tags:
  - dataclasses
  - namedtuple
  - типы
  - структуры
prerequisites: "Классы, кортежи, словари"
objective: "Освоить dataclasses и namedtuples для создания лаконичных структур данных"
---

# Data Classes и Named Tuples: структуры данных без шаблонного кода

## 🎯 Цель урока

Освоить `namedtuple`, `dataclasses` и связанные инструменты для создания структур данных с минимумом шаблонного кода. Научиться выбирать правильный тип данных для каждой задачи.

## 📋 Предпосылки

Вы умеете определять классы в Python, работаете с кортежами и словарями. Понимаете разницу между изменяемыми и неизменяемыми типами.

---

## Введение

Сколько строк кода нужно, чтобы создать класс, который просто хранит данные? В Java — 30+ (поля, конструктор, геттеры, сеттеры, equals, hashCode, toString). В Python — 1 строка с `@dataclass` или `namedtuple`. Python последовательно следует принципу «Simple is better than complex»: если ваш класс — это просто контейнер для данных, вы не должны писать шаблонный код.

В этом уроке мы разберём три инструмента для создания структур данных — `namedtuple`, `dataclasses` и `typing.NamedTuple` — и научимся выбирать правильный для каждой ситуации.

---

## Основная часть

### 1. Проблема: классы с шаблонным кодом

Вот как выглядит простой контейнер данных в «традиционном» Python-стиле:

**❌ Шаблонный код (20+ строк ради простого хранилища):**

```python
class Point:
    """Точка на плоскости."""

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))
```

**✅ Идиоматичный Python (1 строка):**

```python
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float
```

Всё. `__init__`, `__repr__`, `__eq__` — генерируются автоматически. Это не магия — это осознанный дизайн языка, который говорит: «не пиши шаблонный код, сосредоточься на логике».

### 2. `namedtuple` — неизменяемые структуры данных из коробки

`namedtuple` создаёт подкласс кортежа с именованными полями. Это идеальный выбор для неизменяемых записей.

```python
from collections import namedtuple

# Создание namedtuple
Point = namedtuple("Point", ["x", "y"])

# Использование
p = Point(10, 20)
print(p.x)       # 10 — доступ по имени
print(p.y)       # 20
print(p[0])      # 10 — доступ по индексу (как обычный кортеж)
print(p)         # Point(x=10, y=20) — красивый repr

# Неизменяемость
try:
    p.x = 30
except AttributeError as e:
    print(e)  # can't set attribute
```

#### Три способа определения полей

```python
# 1. Список строк
Point = namedtuple("Point", ["x", "y"])

# 2. Одна строка с пробелами/запятыми
Point = namedtuple("Point", "x y")
Point = namedtuple("Point", "x, y")

# 3. С использованием typing.NamedTuple (предпочтительный способ)
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float
```

Третий способ (через класс) предпочтителен: он поддерживает аннотации типов и проверяется mypy.

#### Полезные методы namedtuple

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y", "z"])
p = Point(1, 2, 3)

# _replace — создаёт новый экземпляр с изменёнными полями
p2 = p._replace(x=10)
print(p2)  # Point(x=10, y=2, z=3)
print(p)   # Point(x=1, y=2, z=3) — оригинал не изменился

# _asdict — преобразование в словарь
d = p._asdict()
print(d)  # {'x': 1, 'y': 2, 'z': 3}

# _fields — кортеж имён полей
print(Point._fields)  # ('x', 'y', 'z')

# _make — создание из итератора
data = [10, 20, 30]
p3 = Point._make(data)
print(p3)  # Point(x=10, y=20, z=30)
```

#### Практический пример: записи из базы данных

```python
from collections import namedtuple

# Определяем структуру строки
User = namedtuple("User", ["id", "name", "email", "active"])


def get_users(conn):
    """Возвращает пользователей из БД как namedtuple."""
    cursor = conn.execute("SELECT id, name, email, active FROM users")
    return [User(*row) for row in cursor]


# Использование
users = get_users(connection)
for user in users:
    if user.active:
        print(f"{user.name} <{user.email}>")
```

### 3. `dataclasses` — декларативные классы данных (Python 3.7+)

`@dataclass` — это эволюция `namedtuple` для случаев, когда нужна изменяемость и больше контроля.

```python
from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int
    email: str = ""  # Значение по умолчанию


# Автоматически генерируются: __init__, __repr__, __eq__
alice = Person("Alice", 30, "alice@example.com")
bob = Person("Bob", 25)

print(alice)           # Person(name='Alice', age=30, email='alice@example.com')
print(alice == bob)    # False (сравнение по значениям, а не по ссылкам!)
alice.age = 31         # Изменяемый — в отличие от namedtuple
```

#### Параметры `@dataclass`

```python
@dataclass(
    init=True,           # Генерировать __init__
    repr=True,           # Генерировать __repr__
    eq=True,             # Генерировать __eq__
    order=False,         # Генерировать __lt__, __le__, __gt__, __ge__
    unsafe_hash=False,   # Генерировать __hash__
    frozen=False,        # Сделать неизменяемым (как namedtuple)
    slots=False,         # Использовать __slots__ (Python 3.10+)
)
class Config:
    host: str
    port: int = 5432
```

#### `frozen=True` — неизменяемые dataclass

```python
@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float


p = ImmutablePoint(1.0, 2.0)
try:
    p.x = 5.0
except AttributeError as e:
    print(e)  # can't set attribute
```

#### `order=True` — сравнимые dataclass

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int


v1 = Version(1, 0, 0)
v2 = Version(2, 0, 0)
v3 = Version(1, 5, 0)

print(v1 < v2)   # True
print(v1 < v3)   # True
print(sorted([v2, v3, v1]))
# [Version(major=1, minor=0, patch=0),
#  Version(major=1, minor=5, patch=0),
#  Version(major=2, minor=0, patch=0)]
```

### 4. Поле `field()` — тонкая настройка

```python
from dataclasses import dataclass, field


@dataclass
class InventoryItem:
    name: str
    unit_price: float
    quantity_on_hand: int = 0

    # Вычисляемое поле: не попадает в __init__
    total_cost: float = field(init=False)

    def __post_init__(self):
        """Вызывается после __init__ для вычисляемых полей и валидации."""
        self.total_cost = self.unit_price * self.quantity_on_hand


item = InventoryItem("Widget", 9.99, 10)
print(item.total_cost)  # 99.9
```

#### `field()` с параметрами по умолчанию

```python
@dataclass
class User:
    name: str
    tags: list[str] = field(default_factory=list)  # Не []!
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


# Без default_factory была бы классическая ошибка:
# все экземпляры делили бы ОДИН список!
u1 = User("Alice")
u2 = User("Bob")
u1.tags.append("admin")
print(u2.tags)  # [] — у каждого свой список (правильно!)
```

#### `field()` с метаданными

```python
@dataclass
class APIConfig:
    url: str = field(metadata={"env": "API_URL"})
    timeout: int = field(default=30, metadata={"unit": "seconds"})
    retries: int = field(default=3, metadata={"min": 0, "max": 10})


# Метаданные доступны через fields()
from dataclasses import fields

for f in fields(APIConfig):
    print(f"{f.name}: {f.metadata}")
# url: {'env': 'API_URL'}
# timeout: {'unit': 'seconds'}
# retries: {'min': 0, 'max': 10}
```

### 5. `__post_init__` — валидация и вычисления

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Ширина и высота должны быть положительными")
        self.area = self.width * self.height


# Правильно
r = Rectangle(5, 10)
print(r.area)  # 50.0

# Валидация
try:
    Rectangle(-1, 10)
except ValueError as e:
    print(e)  # Ширина и высота должны быть положительными
```

### 6. Наследование dataclass

```python
@dataclass
class Vehicle:
    brand: str
    model: str
    year: int = 2024


@dataclass
class Car(Vehicle):
    doors: int = 4
    electric: bool = False


@dataclass
class Motorcycle(Vehicle):
    sidecar: bool = False


car = Car("Tesla", "Model 3", 2024, electric=True)
moto = Motorcycle("Harley-Davidson", "Sportster", 2023)
print(car)   # Car(brand='Tesla', model='Model 3', year=2024, doors=4, electric=True)
print(moto)  # Motorcycle(brand='Harley-Davidson', model='Sportster', year=2023, sidecar=False)
```

Поля родительских классов идут первыми. Это гарантирует правильный порядок параметров в `__init__`.

### 7. Когда использовать что: словарь vs namedtuple vs dataclass vs класс

| Критерий | `dict` | `namedtuple` | `@dataclass` | Обычный `class` |
|----------|--------|-------------|-------------|-----------------|
| **Строк в коде** | 1 | 1-2 | 4-5 | 20+ |
| **Изменяемость** | Да | Нет | Да (если не frozen) | Да |
| **Доступ по имени** | `d["key"]` | `p.field` | `p.field` | `p.field` |
| **Проверка типов** | Нет | `NamedTuple` | Да | Да |
| **Сравнение** | По значениям | По значениям | По значениям | По ссылкам |
| **Хешируемость** | Нет | Да | Если frozen | По умолчанию да |
| **Итерация** | По ключам | По значениям | Нет (если не iter) | Нет |
| **Методы** | Нет | Можно, но неудобно | Да | Да |
| **Наследование** | Нет | Ограничено | Да | Да |
| **Память** | Много | Мало | Средне | Средне |

#### Правило выбора

```
Нужна простая запись (как struct в C)?
├── Неизменяемая? → namedtuple / NamedTuple
├── Изменяемая?   → @dataclass
└── Сложная логика, инварианты, наследование? → Обычный class с @property

Нужен JSON/API ответ?
├── Временный, одноразовый? → dict
└── Многоразовый, типобезопасный? → @dataclass + asdict()
```

### 8. `asdict()` и `astuple()` — преобразование dataclass

```python
from dataclasses import dataclass, asdict, astuple


@dataclass
class User:
    name: str
    age: int
    email: str = ""


user = User("Alice", 30, "alice@example.com")

# В словарь
d = asdict(user)
print(d)  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}

# В кортеж
t = astuple(user)
print(t)  # ('Alice', 30, 'alice@example.com')

# В JSON
import json

json_str = json.dumps(asdict(user))
print(json_str)  # {"name": "Alice", "age": 30, "email": "alice@example.com"}
```

### 9. `dataclasses` vs `pydantic` — когда нужна валидация

`dataclasses` — это стандартная библиотека. Для продвинутой валидации есть `pydantic`:

```python
# Стандартный dataclass — валидацию нужно писать вручную
@dataclass
class User:
    name: str
    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age must be non-negative")


# Pydantic — валидация из коробки
from pydantic import BaseModel, Field


class UserPydantic(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)  # >= 0


# Автоматическая валидация при создании
try:
    UserPydantic(name="", age=-5)
except Exception as e:
    print(e)  # Несколько ошибок валидации
```

Для большинства случаев достаточно `dataclasses`. Pydantic нужен когда:
- Данные приходят извне (API, файлы конфигурации)
- Нужна автоматическая валидация и десериализация
- Работаете с FastAPI

### 10. Сравнение с другими языками

#### Java Records (Java 14+)

Java Records — это ответ Java на `data class`:

```java
// Java 14+ — Records
public record Point(int x, int y) {}
// Автоматически: конструктор, геттеры, equals, hashCode, toString
```

```python
# Python — dataclass (тот же функционал, но более гибкий)
@dataclass
class Point:
    x: int
    y: int
```

Java Records всегда неизменяемы. Python `@dataclass` может быть изменяемым или неизменяемым (`frozen=True`). Java Records не поддерживают наследование от не-record классов. Python dataclass — обычные классы, поддерживают всё наследование.

#### C++ structs

C++ struct — это просто класс с публичными полями по умолчанию:

```cpp
// C++ — struct, нужно писать конструктор, операторы сравнения
struct Point {
    int x;
    int y;

    Point(int x, int y) : x(x), y(y) {}

    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
};
```

```python
# Python — одна строка, всё включено
@dataclass
class Point:
    x: int
    y: int
```

C++20 добавил `operator==` по умолчанию, но всё равно нужно писать конструктор.

#### JavaScript / TypeScript

JavaScript не имеет встроенного механизма для структур данных (кроме объектов):

```typescript
// TypeScript — интерфейс + ручное создание
interface Point {
    x: number;
    y: number;
}

const p: Point = { x: 10, y: 20 };
```

```python
# Python — dataclass даёт repr, сравнение, хеширование и валидацию
@dataclass
class Point:
    x: float
    y: float
```

TypeScript-интерфейсы — это только типы времени компиляции. Python dataclass — это runtime-классы с автоматически сгенерированными методами: `__init__`, `__repr__`, `__eq__`, и, опционально, `__hash__`, `__lt__`, `__le__`, `__gt__`, `__ge__`.

---

## Практическое задание

### Задание 1: Система заказов

Создайте систему типов для интернет-магазина, используя `dataclass`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Address:
    """Адрес доставки."""
    # Ваш код: street, city, zip_code, country
    pass


@dataclass
class OrderItem:
    """Позиция в заказе."""
    # Ваш код: product_id, name, quantity, unit_price
    # total_price должно вычисляться в __post_init__
    pass


@dataclass
class Order:
    """Заказ."""
    # Ваш код: order_id, items (list[OrderItem]), shipping_address (Address),
    # created_at (datetime, default=datetime.now), status (str, default="pending")
    # total должно вычисляться в __post_init__
    pass


# Использование:
address = Address("123 Main St", "New York", "10001", "USA")
item1 = OrderItem("P001", "Widget", 2, 9.99)
item2 = OrderItem("P002", "Gadget", 1, 24.50)
order = Order("ORD-001", [item1, item2], address)

print(order)
print(f"Total: ${order.total:.2f}")
```

### Задание 2: Конфигурация с приоритетами

Напишите `dataclass` для конфигурации приложения с поддержкой слияния (как в уроке 6 с `**`):

```python
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    """Конфигурация приложения с методом merge."""
    host: str = "localhost"
    port: int = 5432
    debug: bool = False
    timeout: int = 30

    def merge(self, other: "AppConfig") -> "AppConfig":
        """
        Создаёт новую конфигурацию, где не-дефолтные значения
        из other переопределяют значения self.
        """
        # Ваш код
        pass


# Использование:
defaults = AppConfig()
user_config = AppConfig(host="db.example.com", timeout=60)
final = defaults.merge(user_config)
print(final)
# AppConfig(host='db.example.com', port=5432, debug=False, timeout=60)
```

### Задание 3: Транзакции с namedtuple

Создайте `NamedTuple` для представления банковской транзакции и функцию для фильтрации транзакций:

```python
from typing import NamedTuple
from datetime import datetime


class Transaction(NamedTuple):
    """Банковская транзакция."""
    id: str
    amount: float
    category: str
    timestamp: datetime
    description: str = ""


def filter_transactions(
    transactions: list[Transaction],
    *,
    min_amount: float = 0.0,
    max_amount: float = float("inf"),
    categories: set[str] | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[Transaction]:
    """
    Фильтрует транзакции по заданным критериям.
    Все параметры, кроме transactions — keyword-only.
    """
    # Ваш код
    pass


# Тестовые данные
from datetime import datetime, timedelta

now = datetime.now()
transactions = [
    Transaction("T1", 100.0, "food", now - timedelta(days=1)),
    Transaction("T2", 500.0, "rent", now - timedelta(days=2)),
    Transaction("T3", 50.0, "food", now - timedelta(hours=5)),
    Transaction("T4", 1000.0, "salary", now - timedelta(days=3)),
    Transaction("T5", 200.0, "entertainment", now),
]

# Фильтрация: только food за последние 2 дня
result = filter_transactions(
    transactions,
    categories={"food"},
    date_from=now - timedelta(days=2),
)
print(result)
# [Transaction(id='T1', ...), Transaction(id='T3', ...)]
```

---

## Дополнительные материалы

### Документация

- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [collections.namedtuple documentation](https://docs.python.org/3/library/collections.html#collections.namedtuple)
- [typing.NamedTuple documentation](https://docs.python.org/3/library/typing.html#typing.NamedTuple)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 2 (последовательности) и глава 11 (интерфейсы: от протоколов до ABC).
- **«Effective Python»**, Бретт Слаткин — совет 37: «Используйте dataclasses вместо namedtuple когда нужна изменяемость», совет 38: «Используйте dataclasses для классов с состоянием».

### Статьи

- [Real Python: Using Python dataclasses](https://realpython.com/python-data-classes/)
- [Real Python: Write Pythonic and Clean Code With namedtuple](https://realpython.com/python-namedtuple/)
- [Python Patterns: Data Classes](https://python-patterns.guide/)

### Видео

- **«Dataclasses: The code generator to end all code generators»**, Реймонд Хеттингер (PyCon 2018) — доклад автора PEP 557.
- **«Python's Class Development Toolkit»**, Реймонд Хеттингер — о правильном использовании `namedtuple`, `dataclass` и `@property`.