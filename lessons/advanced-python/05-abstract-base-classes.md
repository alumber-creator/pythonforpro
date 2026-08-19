---
title: "Абстрактные базовые классы и интерфейсы в Python"
order: 5
tags: ["ABC", "abc", "интерфейсы", "abstractmethod", "collections"]
prerequisites: "Классы, наследование, декораторы"
objective: "Освоить ABC для определения интерфейсов и создания надёжных иерархий классов"
---

## Введение

Python — язык с динамической типизацией и утиной типизацией: «если что-то крякает как утка — значит, это утка». Но в больших проектах одной утиной типизации недостаточно. Нужны гарантии, что класс реализует определённый набор методов. Именно для этого существуют **Абстрактные Базовые Классы (ABC)**.

Модуль `abc` предоставляет инструменты для определения интерфейсов в Python: `ABC`, `@abstractmethod`, `@abstractproperty`, а также механизм виртуальных подклассов через `register()`. С появлением `typing.Protocol` (PEP 544) Python обогатился ещё и структурной типизацией, позволяя определять интерфейсы без явного наследования.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Определять абстрактные базовые классы и обеспечивать реализацию методов в подклассах
- Использовать `collections.abc` для проверки соответствия стандартным интерфейсам
- Регистрировать виртуальные подклассы для интеграции стороннего кода
- Выбирать между ABC, `typing.Protocol` и утиной типизацией в зависимости от задачи

### 📋 Предпосылки

Вы должны понимать наследование классов, знать, как работают декораторы, и иметь опыт работы с `isinstance` и `issubclass`.

---

## Основная часть

### 1. Основы: `ABC` и `@abstractmethod`

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    """Абстрактный базовый класс для всех геометрических фигур."""

    @abstractmethod
    def area(self) -> float:
        """Вычисляет площадь фигуры."""
        ...

    @abstractmethod
    def perimeter(self) -> float:
        """Вычисляет периметр фигуры."""
        ...

    def describe(self) -> str:
        """Конкретный метод — доступен всем подклассам."""
        return f"Фигура с площадью {self.area():.2f} и периметром {self.perimeter():.2f}"


# s = Shape()  # TypeError: Can't instantiate abstract class Shape


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


c = Circle(5)
r = Rectangle(4, 6)

print(c.describe())  # Фигура с площадью 78.54 и периметром 31.42
print(r.describe())  # Фигура с площадью 24.00 и периметром 20.00

# Проверка типа:
print(isinstance(c, Shape))   # True
print(issubclass(Circle, Shape))  # True
```

#### Частичная реализация — класс остаётся абстрактным

```python
class IncompleteShape(Shape):
    def area(self) -> float:
        return 0.0
    # perimeter() не реализован

# obj = IncompleteShape()  # TypeError: Can't instantiate abstract class
```

### 2. `@abstractclassmethod`, `@abstractstaticmethod`, `@abstractproperty`

```python
from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty


class Configurable(ABC):
    """Абстрактный класс с разными типами абстрактных членов."""

    @abstractclassmethod
    def from_config(cls, config: dict):
        """Фабричный метод: создаёт экземпляр из конфигурации."""
        ...

    @abstractproperty
    def version(self) -> str:
        """Версия конфигурации."""
        ...

    @abstractstaticmethod
    def validate_config(config: dict) -> bool:
        """Проверяет корректность конфигурации."""
        ...


class DatabaseConfig(Configurable):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    @classmethod
    def from_config(cls, config: dict):
        return cls(config["host"], config["port"])

    @property
    def version(self) -> str:
        return "1.0.0"

    @staticmethod
    def validate_config(config: dict) -> bool:
        return "host" in config and "port" in config


cfg = DatabaseConfig.from_config({"host": "localhost", "port": 5432})
print(cfg.host, cfg.port)  # localhost 5432
print(cfg.version)         # 1.0.0
print(DatabaseConfig.validate_config({"host": "x"}))  # False
```

### 3. Виртуальные подклассы: `register()`

Иногда класс, который вы хотите использовать как подкласс ABC, уже написан и не может быть изменён. `register()` позволяет зарегистрировать его как виртуальный подкласс — без изменения исходного кода и даже без реализации всех абстрактных методов:

```python
from abc import ABC, abstractmethod


class Drawable(ABC):
    """Интерфейс для объектов, которые можно нарисовать."""

    @abstractmethod
    def draw(self, canvas) -> None:
        ...

    @abstractmethod
    def get_bounds(self) -> tuple:
        ...


# Сторонний класс, который мы не можем изменить
class ThirdPartyImage:
    def __init__(self, path):
        self.path = path

    def render(self, canvas):
        print(f"Рисую {self.path} на {canvas}")

    def dimensions(self):
        return (800, 600)


# Регистрируем как виртуальный подкласс
Drawable.register(ThirdPartyImage)

img = ThirdPartyImage("photo.png")
print(issubclass(ThirdPartyImage, Drawable))  # True
print(isinstance(img, Drawable))              # True

# Важно: ABC не проверяет, что виртуальный подкласс
# действительно реализует все абстрактные методы!
# Эта ответственность лежит на программисте.
```

#### Практический пример: интеграция с ORM

```python
from abc import ABC, abstractmethod


class Serializable(ABC):
    """Интерфейс для сериализуемых объектов."""

    @abstractmethod
    def to_dict(self) -> dict:
        ...

    @abstractmethod
    def to_json(self) -> str:
        ...


# Django модель — мы не можем её изменить
# (имитация)
class DjangoModel:
    def __init__(self, **fields):
        self._fields = fields

    def serialize(self):
        import json
        return json.dumps(self._fields)


# Регистрируем как виртуальный подкласс
Serializable.register(DjangoModel)

# Проверка в коде
def save_to_file(obj: Serializable, filename: str):
    if not isinstance(obj, Serializable):
        raise TypeError("Объект должен быть Serializable")
    # ... сохранение
```

### 4. `collections.abc` — стандартные интерфейсы Python

Модуль `collections.abc` предоставляет готовые ABC для стандартных структур данных:

| ABC | Описание | Ключевые методы |
|---|---|---|
| `Iterable` | Можно итерировать | `__iter__` |
| `Iterator` | Итератор | `__next__`, `__iter__` |
| `Sequence` | Индексируемая последовательность | `__getitem__`, `__len__` |
| `MutableSequence` | Изменяемая последовательность | `__setitem__`, `__delitem__`, `insert` |
| `Mapping` | Отображение (ключ → значение) | `__getitem__`, `__len__`, `__iter__` |
| `MutableMapping` | Изменяемое отображение | `__setitem__`, `__delitem__` |
| `Set` | Множество | `__contains__`, `__iter__`, `__len__` |
| `Callable` | Можно вызвать как функцию | `__call__` |
| `Hashable` | Можно использовать как ключ dict | `__hash__` |
| `Sized` | Имеет длину | `__len__` |
| `Container` | Поддерживает `in` | `__contains__` |
| `Collection` | Sized + Iterable + Container | Все три |

#### Проверка типов с `collections.abc`

```python
from collections.abc import Sequence, Mapping, Iterable, Callable

def process_data(data):
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        print(f"Обрабатываю последовательность из {len(data)} элементов")
        return [item * 2 for item in data]
    elif isinstance(data, Mapping):
        print(f"Обрабатываю отображение с ключами: {list(data.keys())}")
        return {k: v * 2 for k, v in data.items()}
    else:
        raise TypeError(f"Неподдерживаемый тип: {type(data)}")

print(process_data([1, 2, 3]))          # Обрабатываю последовательность...
print(process_data({"a": 1, "b": 2}))   # Обрабатываю отображение...
# process_data("строка")  # Не попадёт в Sequence (str исключён)
```

#### Создание собственного Sequence-совместимого класса

```python
from collections.abc import Sequence

class RingBuffer(Sequence):
    """Кольцевой буфер, совместимый с Sequence."""

    def __init__(self, max_size: int):
        self._max_size = max_size
        self._buffer = []

    def __getitem__(self, index):
        return self._buffer[index]

    def __len__(self):
        return len(self._buffer)

    def append(self, item):
        if len(self._buffer) >= self._max_size:
            self._buffer.pop(0)
        self._buffer.append(item)

    def __repr__(self):
        return f"RingBuffer({self._buffer!r})"


buf = RingBuffer(3)
buf.append(1)
buf.append(2)
buf.append(3)
buf.append(4)  # Вытесняет 1

print(buf)             # RingBuffer([2, 3, 4])
print(len(buf))        # 3
print(buf[0], buf[-1]) # 2 4
print(isinstance(buf, Sequence))  # True
```

### 5. Duck Typing vs ABC vs Protocol

| Подход | Проверка | Когда | Пример |
|---|---|---|---|
| **Duck Typing** | Нет проверки (доверяем) | Маленькие скрипты, прототипы | `obj.quack()` — если сломается, получим `AttributeError` |
| **ABC** | `isinstance(obj, MyABC)` — жёсткая | Большие проекты, публичные API | `isinstance(obj, Drawable)` |
| **Protocol** | `isinstance(obj, MyProtocol)` — структурная | Статическая типизация (mypy) | `def draw(obj: DrawableProtocol)` |

#### Duck Typing: просто и опасно

```python
def draw_all(objects):
    for obj in objects:
        obj.draw()  # Если у объекта нет draw() — ошибка в рантайме

# Работает с любым объектом, у которого есть draw()
# Никаких гарантий до момента выполнения
```

#### ABC: явные гарантии

```python
def draw_all(objects: list[Drawable]):
    for obj in objects:
        if not isinstance(obj, Drawable):
            raise TypeError(...)
        obj.draw()

# Гарантия на этапе проверки isinstance
```

#### Protocol: структурная типизация (PEP 544)

```python
from typing import Protocol


class DrawableProtocol(Protocol):
    """Структурный интерфейс: любой объект с методом draw()."""

    def draw(self, canvas) -> None:
        ...


class Circle:
    def draw(self, canvas):
        print(f"Рисую круг на {canvas}")

class Square:
    def draw(self, canvas):
        print(f"Рисую квадрат на {canvas}")

# Не нужно наследоваться от DrawableProtocol!
# mypy проверит структурное соответствие на этапе анализа

def render(obj: DrawableProtocol, canvas) -> None:
    obj.draw(canvas)

render(Circle(), "холст")  # OK — у Circle есть draw()
render(Square(), "холст")  # OK — у Square есть draw()
```

### 6. Сравнение с Java, C++, Go

| Аспект | Python (ABC) | Python (Protocol) | Java (interface) | C++ (pure virtual) | Go (interface) |
|---|---|---|---|---|---|
| **Тип** | Номинальный | Структурный | Номинальный | Номинальный | Структурный |
| **Наследование** | Явное (`class X(ABC)`) | Неявное (есть метод — подходит) | Явное (`implements`) | Явное (`: public IFoo`) | Неявное (есть метод — подходит) |
| **Проверка** | `isinstance` | `isinstance` + mypy | Компилятор | Компилятор | Компилятор |
| **Множественное** | Да | Да | Да (интерфейсы) | Да (множественное) | Да |
| **Виртуальные подклассы** | `register()` | Не нужно | Нет | Нет | Не нужно |

**Ключевая сила Python:** наличие **обоих** подходов — номинального (ABC) и структурного (Protocol). Вы можете выбрать жёсткие гарантии через ABC для публичного API или гибкость Protocol для внутреннего кода, проверяемого mypy.

#### Java: интерфейсы (номинальная типизация)

```java
// Java: интерфейс должен быть явно реализован
interface Drawable {
    void draw(Canvas canvas);
    Rect getBounds();
}

class Circle implements Drawable {  // Явное объявление
    public void draw(Canvas canvas) { ... }
    public Rect getBounds() { ... }
}
```

#### Go: интерфейсы (структурная типизация)

```go
// Go: интерфейс реализуется неявно
type Drawable interface {
    Draw(canvas Canvas)
    Bounds() Rect
}

type Circle struct { ... }
func (c Circle) Draw(canvas Canvas) { ... }
func (c Circle) Bounds() Rect { ... }
// Circle автоматически реализует Drawable — без объявления!
```

#### Python: и то, и другое

```python
# Python: ABC — номинальный подход
class Drawable(ABC):
    @abstractmethod
    def draw(self, canvas): ...

class Circle(Drawable):  # Явное наследование
    def draw(self, canvas): ...

# Python: Protocol — структурный подход
class DrawableProtocol(Protocol):
    def draw(self, canvas): ...

class Circle:  # Без наследования!
    def draw(self, canvas): ...
# isinstance(Circle(), DrawableProtocol) → True (во время выполнения)
```

### 7. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
# ✅ ABC для публичного API библиотеки
class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None: ...
    @abstractmethod
    def load(self, key: str) -> bytes: ...

class S3Storage(StorageBackend):
    def save(self, key, data):
        # Реальная реализация для S3
        pass
    def load(self, key):
        pass

# ✅ Protocol для внутреннего кода с mypy
from typing import Protocol

class SupportsRead(Protocol):
    def read(self, size: int) -> str: ...

def process(reader: SupportsRead):
    return reader.read(1024)

# ✅ collections.abc для проверки стандартных типов
from collections.abc import Sequence
if isinstance(obj, Sequence):
    print(f"Длина: {len(obj)}")

# ✅ Виртуальные подклассы для интеграции
from collections.abc import Mapping
Mapping.register(SomeCustomClass)  # Интегрируем сторонний класс
```

#### ❌ Анти-паттерны

```python
# ❌ ABC без абстрактных методов — просто класс
class UselessABC(ABC):
    def method(self):
        pass  # Не абстрактный — зачем ABC?

# ❌ Проверка isinstance вместо утиной типизации в простых случаях
def add(a, b):
    if not isinstance(a, (int, float)):
        raise TypeError(...)  # Излишне для простого кода
    return a + b

# ❌ Виртуальный подкласс, который не реализует интерфейс
class MyOrderedDict(dict):
    pass
# MyOrderedDict не реализует __reversed__, но...
# collections.abc.Reversible.register(MyOrderedDict)  # Обман!

# ❌ Смешивание ABC и Protocol без понимания различий
class Confusing(ABC, Protocol):  # Что это? Номинальный или структурный?
    @abstractmethod
    def method(self): ...

# ❌ ABC с конкретными атрибутами (не методами)
class BadABC(ABC):
    name = "default"  # Конкретный атрибут в ABC — сбивает с толку
```

---

## Практическое задание

### Задача: Система плагинов с строгой типизацией

Создайте модуль `plugin_system.py` с системой загрузки плагинов:

1. **`PluginBase(ABC)`** — абстрактный базовый класс для всех плагинов:
   - `@abstractmethod` `name` (property) — имя плагина
   - `@abstractmethod` `version` (property) — версия
   - `@abstractmethod` `initialize(config: dict) -> bool` — инициализация
   - `@abstractmethod` `execute(*args, **kwargs) -> dict` — выполнение
   - `@abstractmethod` `shutdown() -> None` — завершение
   - Конкретный метод `is_healthy() -> bool` — проверка состояния (по умолчанию True)

2. **`PluginRegistry`** — реестр плагинов:
   - Регистрирует плагины по имени (через `__init_subclass__` или метакласс)
   - `get(name)` — возвращает плагин по имени
   - `list_all()` — возвращает список всех зарегистрированных плагинов
   - `validate_all()` — проверяет, что все зарегистрированные классы наследуют `PluginBase`

3. **`DataProcessor(PluginBase)`** — плагин для обработки данных:
   - Реализует все абстрактные методы
   - Добавляет метод `process_batch(data: list) -> list`

4. **`Notifier(PluginBase)`** — плагин для уведомлений:
   - Реализует все абстрактные методы
   - Добавляет метод `send(message: str, recipient: str) -> bool`

5. **`ExternalPlugin`** — сторонний класс (не наследующий `PluginBase`):
   - Имеет методы `name`, `version`, `initialize`, `execute`, `shutdown`
   - Зарегистрируйте его как **виртуальный подкласс** `PluginBase`

**Требования:**

- Используйте `@abstractmethod`, `@abstractproperty` где уместно
- `PluginRegistry` должен проверять, что классы реализуют все абстрактные методы
- Продемонстрируйте `isinstance` проверки
- Включите docstrings и аннотации типов
- Покажите разницу между обычным и виртуальным подклассом

**Критерии оценки:**

- Корректное использование ABC и абстрактных методов
- Правильная регистрация виртуального подкласса
- Понятный API реестра плагинов
- Полнота проверок (нельзя зарегистрировать неполный плагин)

---

## Дополнительные материалы

- [Python docs: `abc` — Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [Python docs: `collections.abc`](https://docs.python.org/3/library/collections.abc.html)
- [PEP 3119 — Introducing Abstract Base Classes](https://peps.python.org/pep-3119/)
- [PEP 544 — Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [Real Python: Python Interfaces](https://realpython.com/python-interface/)
- [Mypy docs: Protocols](https://mypy.readthedocs.io/en/stable/protocols.html)
- [Brandon Rhodes: "The Clean Architecture in Python" (PyCon 2015)](https://www.youtube.com/watch?v=DJtef410XaM)