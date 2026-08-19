---
title: "Data Classes: продвинутые возможности и паттерны"
order: 6
tags: ["dataclasses", "поля", "наследование", "field"]
prerequisites: "Базовое понимание dataclasses, классы, наследование"
objective: "Освоить продвинутые возможности dataclasses: field, __post_init__, наследование, слоты"
---

## Введение

`dataclasses` — один из самых популярных модулей стандартной библиотеки Python с момента его появления в Python 3.7. На первый взгляд это просто декоратор, который избавляет от написания шаблонного `__init__`. Но за этой простотой скрывается богатый набор возможностей: тонкая настройка полей через `field()`, валидация в `__post_init__`, замороженные (frozen) экземпляры, слоты и наследование.

В этом уроке мы выйдем за рамки базового `@dataclass` и изучим продвинутые паттерны, которые делают dataclasses мощным инструментом для моделирования данных.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Использовать все параметры `field()` для тонкой настройки поведения полей
- Реализовывать валидацию и пост-обработку в `__post_init__`
- Строить иерархии dataclasses с правильным наследованием
- Выбирать между dataclass, NamedTuple, TypedDict и Pydantic в зависимости от задачи

### 📋 Предпосылки

Вы должны знать основы dataclasses: как объявить класс с `@dataclass`, как работают базовые поля и значения по умолчанию. Также нужно понимание наследования классов и аннотаций типов.

---

## Основная часть

### 1. `field()` — все параметры

Функция `field()` — это основной инструмент настройки поведения отдельных полей в dataclass:

```python
from dataclasses import dataclass, field


@dataclass
class Product:
    # Полный набор параметров field()
    name: str = field(
        default="Unnamed",          # Значение по умолчанию
        init=True,                   # Включать ли в __init__
        repr=True,                   # Включать ли в __repr__
        hash=None,                   # Участвует ли в хешировании
        compare=True,                # Участвует ли в сравнении (__eq__)
        metadata={"unit": "text"},   # Пользовательские метаданные
    )
    price: float = field(
        default=0.0,
        metadata={"unit": "USD", "min": 0.0},
    )
    tags: list = field(
        default_factory=list,  # Фабрика для изменяемого значения по умолчанию
        repr=False,            # Не показывать в repr
    )
    _internal_id: str = field(
        default="",
        init=False,            # Не включать в __init__ — вычисляется в __post_init__
        repr=False,
        compare=False,
    )
```

#### Разбор параметров `field()`

| Параметр | Тип | По умолчанию | Описание |
|---|---|---|---|
| `default` | Any | `MISSING` | Значение по умолчанию (нельзя с `default_factory`) |
| `default_factory` | Callable | `MISSING` | Фабрика значений по умолчанию (для изменяемых типов) |
| `init` | bool | `True` | Включать ли поле в `__init__` |
| `repr` | bool | `True` | Включать ли поле в `__repr__` |
| `hash` | bool | `None` | Использовать ли поле в `__hash__` |
| `compare` | bool | `True` | Использовать ли поле в `__eq__` и других сравнениях |
| `metadata` | dict | `None` | Словарь пользовательских метаданных |

#### `default_factory` — когда значение по умолчанию изменяемо

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Order:
    # ❌ НЕПРАВИЛЬНО: список — изменяемый тип, будет общим для всех экземпляров
    # items: list = []

    # ✅ ПРАВИЛЬНО: default_factory создаёт новый список для каждого экземпляра
    items: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


o1 = Order()
o2 = Order()

o1.items.append("item1")
print(o1.items)  # ['item1']
print(o2.items)  # [] — у каждого свой список!

print(o1.created_at)  # Время создания o1
print(o2.created_at)  # Другое время — у каждого свой datetime
```

#### `metadata` — для пользовательской информации

```python
from dataclasses import dataclass, field, fields


@dataclass
class User:
    name: str = field(metadata={"required": True, "max_length": 100})
    email: str = field(metadata={"required": True, "format": "email"})
    age: int = field(metadata={"min_value": 0, "max_value": 150})


def validate_dataclass(instance):
    """Пример валидации на основе metadata полей."""
    for f in fields(instance):
        value = getattr(instance, f.name)
        meta = f.metadata

        if meta.get("required") and value is None:
            raise ValueError(f"Поле {f.name} обязательно")

        if "max_length" in meta and len(str(value)) > meta["max_length"]:
            raise ValueError(
                f"{f.name}: длина {len(str(value))} > {meta['max_length']}"
            )

        if "min_value" in meta and value < meta["min_value"]:
            raise ValueError(
                f"{f.name}: {value} < {meta['min_value']}"
            )

        if "max_value" in meta and value > meta["max_value"]:
            raise ValueError(
                f"{f.name}: {value} > {meta['max_value']}"
            )

    return True


u = User(name="Alice", email="alice@example.com", age=30)
validate_dataclass(u)  # OK

# u2 = User(name="", email="bad", age=200)
# validate_dataclass(u2)  # ValueError
```

### 2. `__post_init__` — валидация и вычисления

`__post_init__` вызывается сразу после `__init__` и идеально подходит для валидации и вычисления производных полей:

```python
from dataclasses import dataclass, field


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False, repr=True)  # Вычисляется в __post_init__

    def __post_init__(self):
        # Валидация
        if self.width <= 0:
            raise ValueError(f"Ширина должна быть положительной, получено {self.width}")
        if self.height <= 0:
            raise ValueError(f"Высота должна быть положительной, получено {self.height}")

        # Вычисление производного поля
        self.area = self.width * self.height


r = Rectangle(5, 10)
print(r)       # Rectangle(width=5, height=10, area=50)
# Rectangle(-1, 10)  # ValueError: Ширина должна быть положительной...
```

#### Продвинутый пример: проверка связей между полями

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DateRange:
    start: datetime
    end: datetime
    duration_days: int = field(init=False)

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError(
                f"start ({self.start}) должен быть раньше end ({self.end})"
            )
        self.duration_days = (self.end - self.start).days


@dataclass
class Subscription:
    user: str
    plan: str
    date_range: DateRange
    is_active: bool = field(init=False)

    def __post_init__(self):
        # Валидация вложенного объекта
        if self.date_range.start < datetime.now():
            raise ValueError("Дата начала подписки в прошлом")

        # Проверка бизнес-правил
        valid_plans = {"basic", "premium", "enterprise"}
        if self.plan not in valid_plans:
            raise ValueError(
                f"Недопустимый план: {self.plan}. Допустимые: {valid_plans}"
            )

        # Вычисляемое поле
        self.is_active = self.date_range.end > datetime.now()


# Использование:
dr = DateRange(
    start=datetime(2025, 1, 1),
    end=datetime(2025, 12, 31),
)
sub = Subscription(
    user="alice",
    plan="premium",
    date_range=dr,
)
print(sub.is_active)  # True
print(sub.date_range.duration_days)  # 364
```

### 3. Наследование dataclasses

```python
from dataclasses import dataclass, field


@dataclass
class Animal:
    name: str
    age: int = 0

    def make_sound(self) -> str:
        return "неизвестный звук"


@dataclass
class Dog(Animal):
    breed: str = "дворняга"
    trained: bool = False

    def make_sound(self) -> str:
        return "Гав!"


@dataclass
class Cat(Animal):
    indoor: bool = True
    favorite_toy: str = field(default="мышка")

    def make_sound(self) -> str:
        return "Мяу!"


d = Dog(name="Рекс", age=3, breed="овчарка", trained=True)
c = Cat(name="Мурка", age=2)

print(d)  # Dog(name='Рекс', age=3, breed='овчарка', trained=True)
print(c)  # Cat(name='Мурка', age=2, indoor=True, favorite_toy='мышка')

# Порядок полей в __init__: сначала поля родителя, потом свои
# Dog.__init__(self, name: str, age: int = 0, breed: str = "дворняга", trained: bool = False)
```

#### Правила наследования

```python
from dataclasses import dataclass


@dataclass
class Base:
    a: int
    b: int = 10


@dataclass
class Child(Base):
    # ❌ Ошибка: поле без значения по умолчанию после поля с default
    # c: int   # TypeError: non-default argument 'c' follows default argument

    # ✅ Правильно: у c тоже есть default
    c: int = 20

    def __post_init__(self):
        # super().__post_init__() вызывается автоматически, если определён
        # в родителе. Но лучше вызывать явно для ясности:
        super().__post_init__()
        # Дополнительная валидация
        if self.c < 0:
            raise ValueError("c должен быть >= 0")
```

#### Множественное наследование

```python
from dataclasses import dataclass


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Size:
    width: float
    height: float


@dataclass
class Rect(Position, Size):
    """Прямоугольник: наследует позицию и размер."""

    def area(self):
        return self.width * self.height


r = Rect(x=10, y=20, width=100, height=200)
print(r)           # Rect(x=10, y=20, width=100, height=200)
print(r.area())    # 20000
```

### 4. Frozen Dataclasses — иммутабельные объекты

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float

    def __add__(self, other):
        """Создаёт новый экземпляр вместо изменения существующего."""
        if isinstance(other, ImmutablePoint):
            return ImmutablePoint(self.x + other.x, self.y + other.y)
        return NotImplemented


p1 = ImmutablePoint(1, 2)
p2 = ImmutablePoint(3, 4)

# p1.x = 10  # FrozenInstanceError: cannot assign to field 'x'

p3 = p1 + p2
print(p3)  # ImmutablePoint(x=4, y=6)

# Хеширование — frozen dataclasses хешируемы по умолчанию
points = {p1: "точка 1", p2: "точка 2"}
print(points[p1])  # точка 1
```

#### Frozen + `__post_init__` — обходное изменение

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CachedData:
    """Иммутабельный класс с кешируемым полем."""

    data: list
    _cached_length: int = field(init=False, repr=False)

    def __post_init__(self):
        # В frozen dataclass можно использовать object.__setattr__
        # для установки значений в __post_init__
        object.__setattr__(self, "_cached_length", len(self.data))

    @property
    def length(self):
        return self._cached_length


cd = CachedData([1, 2, 3, 4, 5])
print(cd.length)  # 5
# cd.data = []  # FrozenInstanceError
```

### 5. `KW_ONLY` и `slots` (Python 3.10+)

```python
from dataclasses import dataclass, field, KW_ONLY


@dataclass
class Config:
    """Конфигурация с обязательными и опциональными полями."""

    # Позиционные аргументы
    host: str
    port: int

    # Всё после KW_ONLY — только keyword-only
    _: KW_ONLY
    debug: bool = False
    timeout: float = field(default=30.0, metadata={"unit": "seconds"})
    max_connections: int = 100


# cfg = Config("localhost", 8080, True)  # Ошибка: слишком много позиционных аргументов
cfg = Config("localhost", 8080, debug=True, timeout=60.0)
print(cfg)  # Config(host='localhost', port=8080, debug=True, timeout=60.0, max_connections=100)
```

#### `slots=True` — компактные dataclasses (Python 3.10+)

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class CompactRecord:
    """Dataclass со слотами — экономит память (как __slots__)."""

    id: int
    name: str
    value: float
    tags: list = field(default_factory=list)


r = CompactRecord(1, "record", 3.14)
print(r.name)  # record

# r.extra = 42  # AttributeError: 'CompactRecord' object has no attribute 'extra'
# Нет __dict__ — экономия памяти, но нет динамических атрибутов
```

### 6. Dataclass vs NamedTuple vs TypedDict vs Pydantic

Выбор правильного инструмента для моделирования данных критически важен:

| Характеристика | `@dataclass` | `NamedTuple` | `TypedDict` | Pydantic `BaseModel` |
|---|---|---|---|---|
| **Изменяемость** | Да (frozen=False) / Нет (frozen=True) | Нет (всегда иммутабельно) | Да (всегда словарь) | Да |
| **Наследование** | Да | Да | Да | Да |
| **Методы** | Да | Да | Нет | Да |
| **Валидация** | Вручную (`__post_init__`) | Нет | Нет (только mypy) | Встроенная |
| **Сериализация** | `dataclasses.asdict()` | `._asdict()` | Это и есть dict | `.model_dump()` |
| **Производительность** | Средняя (со слотами — высокая) | Высокая (C-расширение) | Высокая (это dict) | Низкая (много проверок) |
| **Зависимости** | stdlib | stdlib | stdlib (+ mypy) | pydantic (сторонняя) |
| **JSON Schema** | Нет | Нет | Нет | Да |

#### Сравнение кода

```python
# === Dataclass ===
from dataclasses import dataclass

@dataclass
class UserDC:
    name: str
    age: int

u = UserDC("Alice", 30)
u.age = 31  # Изменяемо
print(u)    # UserDC(name='Alice', age=31)


# === NamedTuple ===
from typing import NamedTuple

class UserNT(NamedTuple):
    name: str
    age: int

u = UserNT("Alice", 30)
# u.age = 31  # AttributeError: can't set attribute
print(u.name, u.age)  # Alice 30
print(u._asdict())    # {'name': 'Alice', 'age': 30}


# === TypedDict ===
from typing import TypedDict

class UserTD(TypedDict):
    name: str
    age: int

u: UserTD = {"name": "Alice", "age": 30}
u["age"] = 31
print(u)  # {'name': 'Alice', 'age': 31}


# === Pydantic ===
from pydantic import BaseModel, Field

class UserPD(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)

u = UserPD(name="Alice", age=30)
# u.age = -1  # ValidationError
print(u.model_dump())  # {'name': 'Alice', 'age': 30}
```

#### Когда что выбирать

```python
# ✅ Dataclass — когда нужны методы и изменяемость
@dataclass
class ShoppingCart:
    items: list = field(default_factory=list)

    def add(self, item):
        self.items.append(item)

    def total(self):
        return sum(item.price for item in self.items)

# ✅ NamedTuple — лёгкие иммутабельные данные
from typing import NamedTuple
Point = NamedTuple("Point", [("x", float), ("y", float)])
p = Point(1.0, 2.0)

# ✅ TypedDict — когда вы работаете с JSON / dict
from typing import TypedDict
class APIResponse(TypedDict):
    status: int
    data: dict

# ✅ Pydantic — когда нужна строгая валидация и JSON Schema
from pydantic import BaseModel
class Config(BaseModel):
    host: str
    port: int = 8080
```

### 7. Сравнение с Java Records, Kotlin Data Classes, C# Records

| Аспект | Python `@dataclass` | Kotlin `data class` | Java `record` (14+) | C# `record` (9+) |
|---|---|---|---|---|
| **Появление** | Python 3.7 (2018) | Kotlin 1.0 (2016) | Java 14 (2020) | C# 9 (2020) |
| **Иммутабельность** | Опционально (frozen) | По умолчанию (val) / var | По умолчанию | По умолчанию (позиционные) |
| **Наследование** | Да | Да | Нет (final) | Да |
| **Методы** | Да | Да | Да (ограниченно) | Да |
| **Сериализация** | `asdict()` / `astuple()` | `copy()` | Нет встроенной | `with` expressions |
| **Генерация кода** | Декоратор (runtime) | Компилятор | Компилятор | Компилятор |

#### Kotlin: data class

```kotlin
// Kotlin: data class — лаконично, но жёстко
data class User(val name: String, val age: Int)
// Автоматически: equals(), hashCode(), toString(), copy(), componentN()
```

#### Java: record

```java
// Java: record — лаконично, но иммутабельно и без наследования
public record User(String name, int age) { }
// Автоматически: equals(), hashCode(), toString(), accessor methods
```

#### Python: dataclass

```python
# Python: dataclass — гибко, но требуется ручная валидация
@dataclass
class User:
    name: str
    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Возраст не может быть отрицательным")
```

**Ключевое преимущество Python:** гибкость. Вы можете сделать dataclass изменяемым или иммутабельным (`frozen`), добавить слоты для экономии памяти, включить или исключить любое поле из `__init__`/`__repr__`/`__eq__`. Java records и Kotlin data classes более жёсткие, но за это дают гарантии на уровне компилятора.

### 8. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
# ✅ default_factory для изменяемых типов
@dataclass
class Team:
    members: list = field(default_factory=list)

# ✅ __post_init__ для валидации
@dataclass
class Email:
    address: str

    def __post_init__(self):
        if "@" not in self.address:
            raise ValueError(f"Некорректный email: {self.address}")

# ✅ Frozen для иммутабельных данных
@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lon: float

# ✅ slots=True для миллионов экземпляров
@dataclass(slots=True)
class SensorReading:
    timestamp: float
    sensor_id: str
    value: float

# ✅ KW_ONLY для читаемости
@dataclass
class DatabaseConfig:
    host: str
    port: int
    _: KW_ONLY
    pool_size: int = 10
    timeout: float = 30.0
```

#### ❌ Анти-паттерны

```python
# ❌ Изменяемое значение по умолчанию
@dataclass
class Bad:
    items: list = []  # Общий список для всех экземпляров!

# ❌ Сложная логика в __init__ (dataclass генерирует __init__)
@dataclass
class Bad:
    def __init__(self):  # Переопределяет сгенерированный __init__!
        pass  # Теряется весь смысл dataclass

# ❌ Поле init=False без установки в __post_init__
@dataclass
class Bad:
    computed: int = field(init=False)
    # Забыли __post_init__ — computed всегда будет отсутствовать

# ❌ Смешивание dataclass и ORM-модели без понимания
# (dataclass не предназначен для ORM — используйте SQLAlchemy attrs или Pydantic)

# ❌ Изменение frozen dataclass через object.__setattr__ вне __post_init__
@dataclass(frozen=True)
class Bad:
    value: int

    def sneaky_update(self, new_value):
        object.__setattr__(self, "value", new_value)  # Нарушает контракт frozen!
```

---

## Практическое задание

### Задача: Система управления конфигурациями

Создайте модуль `config_system.py` с иерархией dataclasses для конфигурации приложения:

1. **`BaseConfig`** — базовый dataclass с общими полями:
   - `app_name: str`
   - `version: str`
   - `debug: bool = False`
   - Метод `to_dict() -> dict` (используйте `dataclasses.asdict`)
   - Метод `to_json() -> str`

2. **`DatabaseConfig(BaseConfig)`** — конфигурация базы данных:
   - `host: str`
   - `port: int = 5432`
   - `database: str`
   - `user: str = field(repr=False)` — не показывать в repr
   - `password: str = field(repr=False, default="")` — не показывать
   - `pool_size: int = field(default=10, metadata={"min": 1, "max": 100})`
   - `__post_init__` проверяет: порт в диапазоне 1-65535, pool_size из metadata

3. **`CacheConfig(BaseConfig)`** — конфигурация кеша:
   - `backend: str = "redis"`
   - `ttl_seconds: int = 300`
   - `max_entries: int = 1000`

4. **`AppConfig`** — композитная конфигурация всего приложения (не наследует BaseConfig):
   - `database: DatabaseConfig`
   - `cache: CacheConfig`
   - `features: dict = field(default_factory=dict)`
   - `__post_init__` проверяет, что все вложенные конфигурации валидны

5. **`ConfigLoader`** — загрузчик конфигурации:
   - `from_json(path: str) -> AppConfig`
   - `from_env() -> AppConfig` (загружает из переменных окружения)

**Требования:**

- Используйте `field()` с `metadata` для дополнительной информации о полях
- Используйте `KW_ONLY` для необязательных параметров
- Реализуйте `__post_init__` для валидации
- Используйте `frozen=True` для `BaseConfig` и его потомков
- Включите docstrings и аннотации типов
- Продемонстрируйте сохранение и загрузку конфигурации

**Пример использования:**

```python
config = ConfigLoader.from_json("config.json")
print(config.to_json())
print(config.database.host)
print(config.cache.ttl_seconds)

# Проверка валидации
try:
    bad = DatabaseConfig(
        app_name="test", version="1.0",
        host="localhost", port=99999, database="test"
    )
except ValueError as e:
    print(e)  # Порт должен быть в диапазоне 1-65535
```

**Критерии оценки:**

- Корректное использование наследования dataclasses
- Правильная валидация в `__post_init__`
- Использование `field()` с `metadata`, `repr=False`, `init=False`
- Чистота и читаемость кода
- Работа с вложенными dataclasses

---

## Дополнительные материалы

- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [PEP 681 — Data Class Transforms](https://peps.python.org/pep-0681/)
- [Real Python: Data Classes in Python](https://realpython.com/python-data-classes/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [attrs Documentation](https://www.attrs.org/) — предшественник dataclasses
- [Raymond Hettinger: "Dataclasses: The code generator to end all code generators" (PyCon 2018)](https://www.youtube.com/watch?v=T-TwcmT6Rcw)
- [Python docs: `typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
- [Python docs: `typing.TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict)