---
title: "Дескрипторы: магия доступа к атрибутам"
order: 2
tags: ["дескрипторы", "property", "атрибуты", "__get__", "__set__"]
prerequisites: "Классы, декораторы, понимание __dict__"
objective: "Понять протокол дескрипторов и научиться создавать управляемые атрибуты"
---

## Введение

Дескрипторы — это фундаментальный механизм Python, лежащий в основе многих возможностей языка, которые мы воспринимаем как должное. `@property`, `@staticmethod`, `@classmethod`, `__slots__` — всё это построено на протоколе дескрипторов. Понимание дескрипторов открывает дверь к созданию собственных управляемых атрибутов: ленивая загрузка, кеширование, валидация и многое другое.

Дескриптор — это объект, который определяет, как атрибут извлекается, устанавливается и удаляется. Это не просто синтаксический сахар; это архитектурная основа объектной модели Python.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Объяснить протокол дескрипторов и разницу между data- и non-data дескрипторами
- Реализовать собственные дескрипторы для валидации, ленивой загрузки и кеширования
- Понимать, как устроены `@property`, `@staticmethod` и `@classmethod` изнутри
- Объяснить порядок разрешения атрибутов в цепочке `__dict__` → дескрипторы → `__getattr__`

### 📋 Предпосылки

Вы должны понимать, как работают классы в Python, как устроен `__dict__` экземпляра и класса, а также иметь опыт использования `@property`.

---

## Основная часть

### 1. Протокол дескрипторов

Дескриптор — это любой объект, который определяет хотя бы один из методов:

| Метод | Сигнатура | Назначение |
|---|---|---|
| `__get__` | `(self, instance, owner=None)` | Чтение атрибута |
| `__set__` | `(self, instance, value)` | Запись атрибута |
| `__delete__` | `(self, instance)` | Удаление атрибута |
| `__set_name__` | `(self, owner, name)` | Узнаёт имя атрибута (Python 3.6+) |

**Data-дескриптор** определяет `__set__` (или `__delete__`) — имеет приоритет над `__dict__` экземпляра.

**Non-data-дескриптор** определяет только `__get__` — уступает `__dict__` экземпляра, если атрибут уже там есть.

#### Простейший non-data дескриптор

```python
class LoudAttribute:
    """Громко сообщает о каждом обращении к атрибуту."""

    def __get__(self, instance, owner=None):
        if instance is None:
            return self  # Доступ через класс, а не экземпляр
        print(f"  [GET] Кто-то читает атрибут!")
        return instance.__dict__.get(self._name, None)

    def __set_name__(self, owner, name):
        self._name = name  # Python 3.6+ автоматически вызывает этот метод

class Person:
    name = LoudAttribute()  # Дескриптор на уровне класса

    def __init__(self, name):
        self.__dict__["name"] = name  # Кладём напрямую в __dict__

p = Person("Анна")
print(p.name)  # [GET] Кто-то читает атрибут! → Анна
```

#### Ключевое правило: `__set_name__`

Начиная с Python 3.6, когда класс создаётся, для каждого дескриптора в теле класса вызывается `__set_name__(self, owner, name)`. Это позволяет дескриптору узнать имя атрибута, под которым он был объявлен:

```python
class Validator:
    def __set_name__(self, owner, name):
        self._name = name
        self._private_name = f"_{name}"  # Приватное хранилище

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self._private_name, None)

    def __set__(self, instance, value):
        setattr(instance, self._private_name, value)
```

### 2. Data-дескрипторы: приоритет над `__dict__`

Data-дескриптор имеет приоритет над `__dict__` экземпляра. Это ключевое свойство, которое делает `@property` возможным.

```python
class DataDescriptor:
    """Data-дескриптор: определяет __set__."""

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        print(f"  [DATA GET] Доступ к {self._name}")
        return instance.__dict__.get(f"_{self._name}", None)

    def __set__(self, instance, value):
        print(f"  [DATA SET] Запись {self._name} = {value!r}")
        instance.__dict__[f"_{self._name}"] = value

    def __delete__(self, instance):
        print(f"  [DATA DEL] Удаление {self._name}")
        instance.__dict__.pop(f"_{self._name}", None)

    def __set_name__(self, owner, name):
        self._name = name


class NonDataDescriptor:
    """Non-data дескриптор: только __get__."""

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        print(f"  [NON-DATA GET] Вычисляю значение для {self._name}")
        return f"вычисленное_{self._name}"

    def __set_name__(self, owner, name):
        self._name = name


class Demo:
    data_attr = DataDescriptor()
    nondata_attr = NonDataDescriptor()

    def __init__(self):
        self.data_attr = "из __init__"       # ← Попадёт в DataDescriptor.__set__
        self.nondata_attr = "из __init__"    # ← Попадёт в __dict__, обойдя дескриптор

d = Demo()
# [DATA SET] Запись data_attr = 'из __init__'

print(d.data_attr)     # [DATA GET] Доступ к data_attr → из __init__
print(d.nondata_attr)  # "из __init__" — из __dict__, дескриптор обойдён!
```

**Правило приоритета:**

1. Data-дескриптор в классе → всегда вызывается (даже если атрибут есть в `__dict__`)
2. Атрибут в `__dict__` экземпляра → перекрывает non-data дескриптор
3. Non-data дескриптор в классе → вызывается, если атрибута нет в `__dict__`
4. Атрибут в `__dict__` класса → обычное значение
5. `__getattr__` → вызывается, если ничего не найдено

### 3. Как работает `@property`

`property` — это встроенный data-дескриптор. Его реализация на чистом Python выглядит так:

```python
class Property:
    """Упрощённая реализация property как дескриптора."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc
        self._name = ""

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError(f"Невозможно прочитать атрибут '{self._name}'")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError(f"Невозможно установить атрибут '{self._name}'")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError(f"Невозможно удалить атрибут '{self._name}'")
        self.fdel(instance)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

# Использование:
class Circle:
    def __init__(self, radius):
        self._radius = radius

    def get_radius(self):
        return self._radius

    def set_radius(self, value):
        if value < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self._radius = value

    radius = Property(get_radius, set_radius)
```

#### Как `@staticmethod` и `@classmethod` реализованы через дескрипторы

```python
class StaticMethod:
    """Упрощённая реализация staticmethod."""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner=None):
        return self.func  # Просто возвращает функцию, не привязывая


class ClassMethod:
    """Упрощённая реализация classmethod."""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)

        def bound(*args, **kwargs):
            return self.func(owner, *args, **kwargs)

        return bound


class Demo:
    @StaticMethod
    def static_example():
        return "static"

    @ClassMethod
    def class_example(cls):
        return f"class of {cls.__name__}"
```

### 4. Практические дескрипторы

#### Дескриптор-валидатор

```python
class Validated:
    """Дескриптор, проверяющий значение по заданному предикату."""

    def __init__(self, *, validator=None, coercer=None, error_message=None):
        self._validator = validator
        self._coercer = coercer
        self._error_message = error_message

    def __set_name__(self, owner, name):
        self._name = name
        self._storage = f"_{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self._storage, None)

    def __set__(self, instance, value):
        if self._coercer is not None:
            try:
                value = self._coercer(value)
            except (TypeError, ValueError) as e:
                raise TypeError(
                    f"'{self._name}' не может быть приведён: {e}"
                ) from e

        if self._validator is not None and not self._validator(value):
            msg = self._error_message or f"'{self._name}' = {value!r} не прошёл валидацию"
            raise ValueError(msg)

        instance.__dict__[self._storage] = value


class Product:
    name = Validated(
        validator=lambda v: isinstance(v, str) and len(v) > 0,
        error_message="Название товара не может быть пустым"
    )
    price = Validated(
        coercer=float,
        validator=lambda v: v > 0,
        error_message="Цена должна быть положительным числом"
    )
    discount = Validated(
        coercer=float,
        validator=lambda v: 0 <= v <= 100,
        error_message="Скидка должна быть в диапазоне 0–100"
    )

    def __init__(self, name, price, discount=0):
        self.name = name
        self.price = price
        self.discount = discount

    def final_price(self):
        return self.price * (1 - self.discount / 100)

# Использование:
p = Product("Ноутбук", 1000, discount=10)
print(p.final_price())  # 900.0
# p.price = -500  # ValueError: Цена должна быть положительным числом
```

#### Дескриптор ленивой загрузки (LazyProperty)

```python
class LazyProperty:
    """
    Дескриптор, вычисляющий значение один раз и кеширующий его.

    После первого обращения значение сохраняется в __dict__
    экземпляра, и дескриптор больше не вызывается (non-data).
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        # Вычисляем значение
        value = self.func(instance)
        # Кладём в __dict__ — теперь дескриптор больше не будет вызван
        instance.__dict__[self._name] = value
        return value


class DataSet:
    def __init__(self, filename):
        self.filename = filename

    @LazyProperty
    def data(self):
        """Загружает данные из файла (тяжёлая операция)."""
        print(f"  [LAZY] Загружаю {self.filename}...")
        # Имитация дорогостоящей загрузки
        import time
        time.sleep(0.1)
        return [f"строка_{i}" for i in range(1000)]

    @LazyProperty
    def stats(self):
        """Вычисляет статистику по данным (тоже дорого)."""
        print(f"  [LAZY] Вычисляю статистику...")
        return {
            "count": len(self.data),
            "first": self.data[0],
            "last": self.data[-1],
        }


ds = DataSet("huge_file.csv")
print("DataSet создан, данные ещё не загружены")
print(ds.data[:3])   # [LAZY] Загружаю... → ['строка_0', 'строка_1', 'строка_2']
print(ds.data[:3])   # Без загрузки — кешировано!
print(ds.stats)       # [LAZY] Вычисляю... → {'count': 1000, ...}
```

#### Дескриптор для кеширования с инвалидацией

```python
from datetime import datetime, timedelta

class CachedProperty:
    """
    Кеширует значение с TTL (time-to-live).

    В отличие от простого LazyProperty, значение периодически
    перевычисляется, когда истекает срок жизни кеша.
    """

    def __init__(self, func=None, *, ttl_seconds=60):
        self.func = func
        self.ttl = timedelta(seconds=ttl_seconds)

    def __set_name__(self, owner, name):
        self._name = name
        self._cache_name = f"_cached_{name}"
        self._time_name = f"_cached_{name}_time"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        now = datetime.now()
        cached_time = instance.__dict__.get(self._time_name)

        if cached_time is not None and (now - cached_time) < self.ttl:
            return instance.__dict__[self._cache_name]

        # Кеш устарел или отсутствует — перевычисляем
        value = self.func(instance)
        instance.__dict__[self._cache_name] = value
        instance.__dict__[self._time_name] = now
        return value

    def __delete__(self, instance):
        """Ручная инвалидация кеша."""
        instance.__dict__.pop(self._cache_name, None)
        instance.__dict__.pop(self._time_name, None)


class WeatherService:
    def __init__(self, city):
        self.city = city

    @CachedProperty(ttl_seconds=30)
    def temperature(self):
        """Запрашивает температуру у внешнего API (медленно)."""
        print(f"  [API] Запрос погоды для {self.city}...")
        import random
        return round(random.uniform(-10, 35), 1)

ws = WeatherService("Москва")
print(ws.temperature)  # [API] Запрос... → 12.4
print(ws.temperature)  # Из кеша → 12.4
# Через 30 секунд — снова запрос к API
```

### 5. Сравнение с аналогами в других языках

| Аспект | Python (дескрипторы) | Java (геттеры/сеттеры) | C# (свойства) | JavaScript (get/set) |
|---|---|---|---|---|
| **Уровень** | Протокол (можно реализовать что угодно) | Соглашение (`getX`/`setX`) | Синтаксис языка | Синтаксис языка |
| **Повторное использование** | Дескриптор — переиспользуемый класс | Нет, методы пишутся для каждого поля | Нет, пишутся для каждого поля | Нет, пишутся для каждого поля |
| **Приоритет над прямым доступом** | Data-дескриптор — да | Нет (можно обойти) | Да (синтаксис скрывает поле) | Да |
| **Узнаёт имя атрибута** | `__set_name__` (Python 3.6+) | Нет | `nameof()` в C# 6+ | Нет |
| **Основа для** | `@property`, `@staticmethod`, `__slots__` | Нет | Нет | Нет |

**Ключевое отличие Python:** дескриптор — это не просто синтаксис для геттеров/сеттеров. Это **протокол**, который можно реализовать в многократно используемом классе. Один класс `Validated` может обслуживать десятки атрибутов в разных классах. В Java или C# вам пришлось бы писать геттер/сеттер для каждого поля отдельно.

#### Java: геттеры и сеттеры (много шаблонного кода)

```java
// Java: каждый атрибут требует ручного написания методов
public class Product {
    private String name;
    private double price;

    public String getName() { return name; }
    public void setName(String name) {
        if (name == null || name.isEmpty()) throw new IllegalArgumentException();
        this.name = name;
    }
    public double getPrice() { return price; }
    public void setPrice(double price) {
        if (price <= 0) throw new IllegalArgumentException();
        this.price = price;
    }
    // 10+ строк на каждый атрибут...
}
```

#### Python: дескриптор (переиспользование)

```python
# Python: один класс Validated обслуживает все атрибуты
class Product:
    name = Validated(validator=lambda v: isinstance(v, str) and len(v) > 0)
    price = Validated(validator=lambda v: v > 0, coercer=float)
    # 2 строки на атрибут
```

### 6. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
# ✅ Использование @property для вычисляемых атрибутов
class Thermometer:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self._celsius = (value - 32) * 5 / 9

# ✅ Дескриптор для переиспользуемой валидации
class Positive:
    def __set_name__(self, owner, name):
        self._name = name
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(f"_{self._name}", 0)
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f"{self._name} должен быть >= 0")
        instance.__dict__[f"_{self._name}"] = value

class BankAccount:
    balance = Positive()

# ✅ Явное хранение в __dict__ для data-дескрипторов
```

#### ❌ Анти-паттерны

```python
# ❌ Сложная логика в геттере, которая меняет состояние
class Bad:
    @property
    def items(self):
        self._counter += 1  # Побочный эффект при чтении!
        return self._items

# ❌ Дорогостоящие вычисления в @property без кеширования
class Bad:
    @property
    def report(self):
        # Выполняется при каждом обращении — лучше использовать LazyProperty
        return self._generate_huge_report()

# ❌ Дескриптор, который хранит данные в себе (разделит состояние между экземплярами)
class SharedStateDescriptor:
    def __init__(self):
        self._value = None  # ❌ Общее для всех экземпляров!
    def __get__(self, instance, owner=None):
        return self._value
    def __set__(self, instance, value):
        self._value = value

class A:
    x = SharedStateDescriptor()
class B:
    x = SharedStateDescriptor()

a1, a2 = A(), A()
a1.x = 10
print(a2.x)  # 10 — утечка между экземплярами!

# ❌ Изменение __dict__ напрямую в обход дескриптора
class Bad:
    def __init__(self):
        self.__dict__["name"] = "bad"  # Обходит дескриптор name
```

---

## Практическое задание

### Задача: Библиотека управляемых атрибутов для ORM

Создайте модуль `field_descriptors.py` с дескрипторами для простой ORM-подобной системы:

1. **`Field`** — базовый дескриптор поля. Хранит имя поля, тип, значение по умолчанию. При установке значения проверяет тип.

2. **`CharField(Field)`** — строковое поле. Дополнительно проверяет `max_length` и `min_length`.

3. **`IntegerField(Field)`** — целочисленное поле. Принимает `min_value` и `max_value`.

4. **`ForeignKey(Field)`** — поле внешнего ключа. Принимает ссылку на класс модели. При установке проверяет, что переданный объект — экземпляр правильного класса.

5. **`ModelMeta`** — метакласс, который собирает все поля-дескрипторы в `_fields` словарь.

6. **`Model`** — базовый класс с методами `save()` и `to_dict()`.

**Требования:**

- Все дескрипторы должны быть data-дескрипторами
- Использовать `__set_name__` для автоматического получения имени
- Типы проверяются и при установке значения, и при инициализации
- Значения хранятся в `__dict__` экземпляра с префиксом `_`
- Включите docstrings и аннотации типов
- Продемонстрируйте работу на примере моделей `User` и `Post` с внешним ключом

**Пример использования:**

```python
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField(min_value=0, max_value=150)

class Post(Model):
    title = CharField(max_length=200)
    author = ForeignKey(User)

user = User(name="Анна", age=30)
user.save()  # Фиктивное сохранение

post = Post(title="Мой первый пост", author=user)
post.save()
print(post.to_dict())  # {'title': 'Мой первый пост', 'author': <User object>}
```

---

## Дополнительные материалы

- [Python Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html) — официальное руководство
- [PEP 487 — Simpler customisation of class creation](https://peps.python.org/pep-0487/) — введение `__set_name__`
- [PEP 252 — Making Types Look More Like Classes](https://peps.python.org/pep-0252/) — исторический PEP о дескрипторах
- [David Beazley: "Python Descriptors" (PyCon 2013)](https://www.youtube.com/watch?v=ZJS3zF5cQKY)
- [Simeon Franklin: "Descriptor Tutorial"](https://simeonfranklin.com/blog/2016/jul/30/python-descriptors/)
- [Python 3 Patterns: Descriptors](https://python-3-patterns-idioms-test.readthedocs.io/en/latest/PythonDecorators.html#descriptors)