---
title: "__slots__ и управление памятью объектов"
order: 4
tags: ["__slots__", "память", "оптимизация", "__dict__"]
prerequisites: "Классы, дескрипторы"
objective: "Понять модель памяти объектов Python и научиться оптимизировать её с помощью __slots__"
---

## Введение

По умолчанию каждый экземпляр класса в Python хранит свои атрибуты в словаре `__dict__`. Это даёт невероятную гибкость — можно добавлять и удалять атрибуты на лету. Но за эту гибкость приходится платить: каждый `__dict__` — это полноценная хеш-таблица, которая потребляет значительный объём памяти.

Когда вы создаёте миллионы объектов, накладные расходы `__dict__` становятся критическими. Именно здесь на сцену выходит `__slots__` — механизм, позволяющий заменить динамический словарь на фиксированный массив атрибутов, радикально сокращая потребление памяти.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Объяснить, как `__dict__` устроен внутри и почему он «дорогой»
- Использовать `__slots__` для оптимизации памяти в классах с множеством экземпляров
- Понимать ограничения `__slots__` и знать, когда их применять, а когда — нет
- Количественно оценивать экономию памяти с помощью `sys.getsizeof` и `pympler`

### 📋 Предпосылки

Вы должны понимать, как устроены классы в Python, знать, что такое `__dict__` экземпляра и класса, и иметь базовое представление о дескрипторах (так как `__slots__` реализованы через дескрипторы).

---

## Основная часть

### 1. Как `__dict__` работает внутри

Каждый экземпляр класса без `__slots__` имеет словарь `__dict__`:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.__dict__)  # {'x': 1, 'y': 2}

# Можно добавлять атрибуты динамически — это и есть гибкость
p.z = 3
p.color = "red"
print(p.__dict__)  # {'x': 1, 'y': 2, 'z': 3, 'color': 'red'}
```

#### Что скрывается за `__dict__`?

Словарь Python — это хеш-таблица. Даже пустой словарь занимает минимум 64 байта (в CPython 3.11 — 64 байта для самого объекта dict, а также память под хеш-таблицу). Каждая запись требует дополнительной памяти для ключа, значения и хеша.

```python
import sys

class Empty:
    pass

class WithDict:
    def __init__(self):
        self.x = 1

e = Empty()
print(sys.getsizeof(e))       # 56 байт (базовый объект)

print(sys.getsizeof(e.__dict__))  # 64 байта (пустой словарь!)

d = WithDict()
print(sys.getsizeof(d))       # 56 байт (сам объект)
print(sys.getsizeof(d.__dict__))  # 168 байт (словарь с одной записью)
```

**Структура памяти объекта Python (упрощённо):**

```
+------------------+
| PyObject_HEAD    |  ← Счётчик ссылок, указатель на тип (16 байт)
+------------------+
| __dict__*        |  ← Указатель на словарь (8 байт)
+------------------+
| __weakref__*     |  ← Указатель на слабые ссылки (8 байт, может отсутствовать)
+------------------+
     ↓
+------------------+
| PyDictObject     |  ← Сам словарь (минимум 64 байта)
|   хеш-таблица    |
|   ключи/значения |
+------------------+
```

### 2. `__slots__`: замена `__dict__` на фиксированный массив

```python
class PointSlotted:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

ps = PointSlotted(1, 2)

# __dict__ больше нет!
# print(ps.__dict__)  # AttributeError: 'PointSlotted' object has no attribute '__dict__'

# Динамическое добавление атрибутов невозможно
# ps.z = 3  # AttributeError: 'PointSlotted' object has no attribute 'z'

print(ps.x, ps.y)  # 1 2 — работает как обычно
```

#### Как `__slots__` работают внутри

`__slots__` — это не просто список строк. Для каждого имени в `__slots__` Python создаёт **дескриптор** (data-дескриптор), который хранит значение атрибута в фиксированном слоте памяти объекта, а не в словаре. Это полностью устраняет накладные расходы `__dict__`.

```python
import sys

class Regular:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Slotted:
    __slots__ = ("x", "y", "z")
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

r = Regular(1, 2, 3)
s = Slotted(1, 2, 3)

print(f"Regular: {sys.getsizeof(r)} байт + __dict__: {sys.getsizeof(r.__dict__)} байт")
print(f"Slotted: {sys.getsizeof(s)} байт")  # Без __dict__!

# Типичный результат:
# Regular: 56 байт + __dict__: 200 байт = 256 байт
# Slotted: 80 байт (всего!)
```

### 3. Количественная оценка экономии памяти

Создадим миллион объектов и сравним:

```python
import sys
import tracemalloc
from itertools import islice


class RecordRegular:
    def __init__(self, id_, name, value):
        self.id = id_
        self.name = name
        self.value = value


class RecordSlotted:
    __slots__ = ("id", "name", "value")

    def __init__(self, id_, name, value):
        self.id = id_
        self.name = name
        self.value = value


def measure_memory(cls, n=100_000):
    """Измеряет память, занимаемую n экземплярами класса."""
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    objects = [cls(i, f"item_{i}", float(i)) for i in range(n)]

    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    stats = snapshot_after.compare_to(snapshot_before, "lineno")
    total_kb = sum(stat.size_diff for stat in stats) / 1024
    per_object = total_kb * 1024 / n
    return total_kb, per_object


# Примерные результаты (могут варьироваться):
# Regular: ~15 000 KB (~154 байта/объект)
# Slotted:  ~5 000 KB (~51 байт/объект)
# Экономия: ~3x!

# Сравнение размера отдельных объектов
r = RecordRegular(1, "test", 1.0)
s = RecordSlotted(1, "test", 1.0)

print(f"Regular: {sys.getsizeof(r)} + {sys.getsizeof(r.__dict__)} = "
      f"{sys.getsizeof(r) + sys.getsizeof(r.__dict__)} байт")
print(f"Slotted: {sys.getsizeof(s)} байт")
```

#### Таблица: сравнение памяти для объекта с 3 атрибутами

| Класс | `sys.getsizeof(obj)` | `sys.getsizeof(__dict__)` | **Итого** | Экономия |
|---|---|---|---|---|
| `Regular` | 56 байт | ~200 байт | **~256 байт** | — |
| `Slotted` | 80 байт | — | **~80 байт** | **~3.2x** |
| `Slotted` (6 атрибутов) | 104 байта | — | **~104 байта** | **~4x** |

### 4. Наследование с `__slots__`

```python
class Base:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Derived(Base):
    # Если не указать __slots__, у Derived появится __dict__!
    pass

d = Derived(1, 2)
d.z = 3  # Работает — у Derived есть __dict__!
print(d.__dict__)  # {'z': 3}


class DerivedSlotted(Base):
    __slots__ = ("z",)  # Добавляем свой слот

    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

ds = DerivedSlotted(1, 2, 3)
# ds.w = 4  # AttributeError — нет __dict__
print(ds.x, ds.y, ds.z)  # 1 2 3
```

#### Множественное наследование со слотами

```python
class A:
    __slots__ = ("a",)

class B:
    __slots__ = ("b",)

class C(A, B):
    __slots__ = ("c",)

c = C()
c.a = 1
c.b = 2
c.c = 3
# c.d = 4  # AttributeError

# Важно: если хотя бы один родитель без __slots__, у наследника будет __dict__
class D:
    pass  # Без __slots__

class E(D):
    __slots__ = ("e",)

e = E()
e.f = 42  # Работает — есть __dict__ от D
print(e.__dict__)  # {'f': 42}
```

### 5. `__weakref__` и `__slots__`

По умолчанию объекты Python поддерживают слабые ссылки (weak references) через атрибут `__weakref__`. Если вы используете `__slots__`, нужно явно указать `__weakref__` в кортеже:

```python
import weakref

class WithoutWeakref:
    __slots__ = ("x",)

class WithWeakref:
    __slots__ = ("x", "__weakref__")

obj = WithoutWeakref()
obj.x = 42
# weakref.ref(obj)  # TypeError: cannot create weak reference

obj2 = WithWeakref()
obj2.x = 42
ref = weakref.ref(obj2)  # OK
print(ref())  # <__main__.WithWeakref object at ...>
```

### 6. Когда использовать `__slots__`

| Ситуация | Использовать `__slots__`? |
|---|---|
| Миллионы экземпляров (точки, векторы, записи данных) | ✅ Да — экономия памяти критична |
| Класс-конфигурация, создаётся один раз | ❌ Нет — экономия незначительна |
| Нужна динамическая природа (добавление атрибутов на лету) | ❌ Нет — `__slots__` запрещает это |
| Класс активно сериализуется (pickle, JSON) | ⚠️ Осторожно — некоторые библиотеки ожидают `__dict__` |
| Библиотека / фреймворк, ожидающий `__dict__` | ❌ Нет — сломается совместимость |
| Data-класс с фиксированной схемой | ✅ Да — идеальный кандидат |

### 7. Ограничения `__slots__`

1. **Нет `__dict__`** — нельзя добавлять атрибуты динамически
2. **Нельзя миксовать с `__dict__`** (если только не указать `__dict__` явно в `__slots__`)
3. **Нет множественного наследования от классов с разными `__slots__`** (без пустых слотов)
4. **Сериализация:** `pickle` и `json` могут ожидать `__dict__`
5. **Дескрипторы:** если в классе-родителе есть data-дескриптор с именем из `__slots__`, слот не будет создан

```python
# Ограничение: конфликт с data-дескриптором
class DescriptorParent:
    @property
    def x(self):
        return 42

# class Child(DescriptorParent):
#     __slots__ = ("x",)  # ValueError: 'x' in __slots__ conflicts with class variable
```

### 8. `__slots__` с `__dict__` (гибридный подход)

Иногда нужно и экономить память, и сохранить гибкость для отдельных атрибутов:

```python
class FlexibleSlots:
    __slots__ = ("id", "name", "__dict__")  # __dict__ в слотах!

    def __init__(self, id_, name):
        self.id = id_
        self.name = name

fs = FlexibleSlots(1, "Alice")
# Фиксированные атрибуты — в слотах
fs.id = 2
fs.name = "Bob"

# Динамические атрибуты — в __dict__
fs.temp_field = "временный"
fs.another = 42

print(fs.__dict__)  # {'temp_field': 'временный', 'another': 42}
print(fs.id, fs.name)  # 2 Bob — в слотах, не в __dict__
```

### 9. Сравнение с C++, Java и JavaScript

| Аспект | Python (default) | Python (`__slots__`) | C++ | Java | JavaScript |
|---|---|---|---|---|---|
| **Хранение атрибутов** | `__dict__` (хеш-таблица) | Фиксированный массив | Фиксированный layout (compile-time) | Фиксированный layout | Скрытая форма (shape) |
| **Динамические атрибуты** | Да | Нет (если не указан `__dict__`) | Нет | Нет | Да |
| **Память на объект** | ~56 + dict | ~56 + 8 × N слотов | sizeof(поля) | sizeof(поля) + заголовок | ~объект + скрытая карта |
| **Скорость доступа** | O(1) средняя, но с оверхедом | Быстрее (прямой доступ) | Максимальная | Максимальная | Как у Python |
| **Гибкость** | Максимальная | Минимальная | Минимальная | Минимальная | Высокая |

**Ключевое отличие Python:** в C++ и Java объекты по умолчанию имеют фиксированный макет памяти — это норма. В Python же фиксированный макет достигается через `__slots__`, и это осознанный компромисс между гибкостью и производительностью. Python по умолчанию выбирает гибкость; C++ и Java по умолчанию выбирают производительность.

#### C++: фиксированный макет по умолчанию

```cpp
// C++: размер объекта известен на этапе компиляции
struct Point {
    double x;
    double y;
};
// sizeof(Point) == 16 байт (два double)
// Нельзя добавить поле z во время выполнения
```

#### Python: гибкость по умолчанию, фиксация через `__slots__`

```python
# Python: по умолчанию — гибкость
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
# Можно добавить p.z = 3 в любой момент
# Цена: ~256 байт на объект

# Python: со __slots__ — фиксация
class PointSlotted:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y
# Нельзя добавить p.z = 3
# Цена: ~80 байт на объект
```

### 10. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
# ✅ Класс для миллионов экземпляров — со __slots__
class DataPoint:
    __slots__ = ("timestamp", "value", "sensor_id", "__weakref__")

    def __init__(self, timestamp, value, sensor_id):
        self.timestamp = timestamp
        self.value = value
        self.sensor_id = sensor_id

# ✅ Наследование со слотами: явно указываем слоты в потомках
class NamedPoint(DataPoint):
    __slots__ = ("name",)

    def __init__(self, timestamp, value, sensor_id, name):
        super().__init__(timestamp, value, sensor_id)
        self.name = name

# ✅ Явное указание __dict__ для гибридного класса
class SemiFlexible:
    __slots__ = ("id", "name", "__dict__")

# ✅ Использование dataclass со слотами (Python 3.10+)
from dataclasses import dataclass

@dataclass(slots=True)
class Product:
    name: str
    price: float
    quantity: int
```

#### ❌ Анти-паттерны

```python
# ❌ __slots__ в классе, который создаётся один раз
class AppConfig:
    __slots__ = ("debug", "database_url", "secret_key")  # Бессмысленно
    def __init__(self, debug, database_url, secret_key):
        self.debug = debug
        self.database_url = database_url
        self.secret_key = secret_key

# ❌ Динамическое создание __slots__ (работает, но ужасно)
class Bad:
    pass

Bad.__slots__ = ("x",)  # Не сработает — __slots__ должен быть в теле класса

# ❌ Добавление __dict__ в __slots__ без необходимости
class Pointless:
    __slots__ = ("x", "y", "__dict__")  # Теряет весь смысл __slots__!

# ❌ Неправильное наследование
class Parent:
    pass  # Нет __slots__

class Child(Parent):
    __slots__ = ("a", "b")  # У Child всё равно будет __dict__ из-за Parent!

# ❌ Изменение __slots__ после создания класса
class MyClass:
    __slots__ = ("a",)

# MyClass.__slots__ = ("a", "b")  # Не добавляет слот — уже поздно!
```

---

## Практическое задание

### Задача: Высокопроизводительная система хранения событий

Создайте модуль `event_store.py` с оптимизированной по памяти системой для хранения миллионов событий:

1. **`Event`** — базовый класс события с `__slots__`:
   - Поля: `timestamp` (float), `event_type` (str), `source` (str)
   - Метод `__repr__`

2. **`SensorEvent(Event)`** — событие датчика:
   - Дополнительные поля: `sensor_id` (str), `value` (float), `unit` (str)
   - Собственные `__slots__`

3. **`ErrorEvent(Event)`** — событие ошибки:
   - Дополнительные поля: `error_code` (int), `message` (str), `severity` (str)
   - Собственные `__slots__`

4. **`EventStore`** — хранилище событий:
   - Хранит события в `list`
   - Метод `add(event)` — добавляет событие
   - Метод `query(event_type=None, source=None, time_from=None, time_to=None)` — фильтрует события
   - Метод `memory_usage()` — возвращает оценку используемой памяти
   - Метод `stats()` — возвращает статистику (количество событий каждого типа, распределение по источникам)

5. **Сравнительный анализ**:
   - Создайте аналогичные классы **без** `__slots__`
   - Сравните потребление памяти для 100 000 событий каждого типа
   - Выведите результаты в виде таблицы

**Требования:**

- Все классы событий должны использовать `__slots__`
- Правильное наследование слотов
- Включите `__weakref__` в базовый класс
- Используйте `tracemalloc` или `sys.getsizeof` для измерения памяти
- Включите docstrings и аннотации типов

**Пример использования:**

```python
store = EventStore()
store.add(SensorEvent(time.time(), "temperature", "sensor-01", "T1", 23.5, "C"))
store.add(ErrorEvent(time.time(), "error", "system", 500, "Timeout", "HIGH"))

print(store.stats())
print(f"Память: {store.memory_usage():.2f} MB")

# Сравнение с версией без __slots__
print(compare_memory(100_000))
```

---

## Дополнительные материалы

- [Python docs: `__slots__`](https://docs.python.org/3/reference/datamodel.html#slots)
- [PEP 307 — Extensions to the pickle protocol](https://peps.python.org/pep-0307/) — `__slots__` и pickle
- [Stack Overflow: Usage of `__slots__`?](https://stackoverflow.com/questions/472000/usage-of-slots)
- [Guido van Rossum: "The History of Python — `__slots__`"](http://python-history.blogspot.com/2010/06/inside-story-on-new-style-classes.html)
- [PyMpler: `asizeof` — точное измерение памяти](https://pythonhosted.org/Pympler/asizeof.html)
- [Python Memory Management — глубокое погружение](https://realpython.com/python-memory-management/)
- [Aaron Hall: "`__slots__` Magic"](https://stackoverflow.com/a/28059785/7483211)