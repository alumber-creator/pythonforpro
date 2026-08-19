---
title: "Метаклассы: когда классы — это объекты"
order: 3
tags: ["метаклассы", "type", "__new__", "__init_subclass__"]
prerequisites: "Классы, наследование, дескрипторы"
objective: "Понять, как создаются классы в Python, и научиться использовать метаклассы"
---

## Введение

В Python всё является объектом — включая сами классы. Если `int` — это объект типа `type`, то кто создаёт классы? Ответ: **метакласс**. Метакласс для класса — это то же, что класс для экземпляра: он определяет, как класс создаётся, инициализируется и ведёт себя.

Метаклассы — одна из самых глубоких тем Python, и их часто называют «магией». Но за этой магией стоит простой принцип: `type` — это обычный класс, который создаёт другие классы, и мы можем его наследовать.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Объяснить, как `type()` создаёт классы во время исполнения
- Использовать `__init_subclass__` для лёгкой настройки наследования
- Писать собственные метаклассы для решения реальных задач
- Понимать, когда метаклассы действительно нужны, а когда — избыточны

### 📋 Предпосылки

Вы должны уверенно владеть классами и наследованием, понимать `__new__` и `__init__`, а также иметь базовое представление о дескрипторах.

---

## Основная часть

### 1. Всё есть объект — включая классы

```python
class Person:
    pass

p = Person()

# Класс — это объект
print(type(p))        # <class '__main__.Person'>
print(type(Person))   # <class 'type'>  ← Класс Person создан метаклассом type

# Класс — это экземпляр метакласса
print(isinstance(p, Person))       # True
print(isinstance(Person, type))    # True
print(isinstance(type, type))      # True — type является экземпляром самого себя

# type — это метакласс по умолчанию для всех классов
print(type(int))      # <class 'type'>
print(type(dict))     # <class 'type'>
print(type(object))   # <class 'type'> — даже object создан через type
```

#### Создание класса через `type()` (альтернатива `class`)

```python
# Классический синтаксис
class Dog:
    species = "Canis familiaris"

    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} говорит: Гав!"

# Тот же класс, созданный через type()
Dog = type("Dog",                       # Имя класса
           (object,),                   # Кортеж базовых классов
           {                            # Словарь атрибутов
               "species": "Canis familiaris",
               "__init__": lambda self, name: setattr(self, "name", name),
               "bark": lambda self: f"{self.name} говорит: Гав!",
           })

rex = Dog("Рекс")
print(rex.bark())  # Рекс говорит: Гав!
```

**Сигнатура `type()`:**
```python
type(name, bases, namespace) -> новый класс
```

Метакласс — это просто подкласс `type`, который переопределяет этот процесс создания.

### 2. `__init_subclass__` — лёгкая альтернатива метаклассам

Прежде чем писать метакласс, спросите себя: можно ли решить задачу через `__init_subclass__`? Этот метод вызывается **автоматически** при создании подкласса:

```python
class PluginBase:
    """Базовый класс для плагинов. Автоматически регистрирует подклассы."""
    _registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ in PluginBase._registry:
            raise NameError(f"Плагин {cls.__name__} уже зарегистрирован")
        PluginBase._registry[cls.__name__] = cls
        print(f"Зарегистрирован плагин: {cls.__name__}")

    def run(self):
        raise NotImplementedError


class EmailPlugin(PluginBase):
    # Автоматически регистрируется при создании!
    def run(self):
        return "Отправляю email..."

class SMSPlugin(PluginBase):
    def run(self):
        return "Отправляю SMS..."

print(PluginBase._registry)
# {'EmailPlugin': <class 'EmailPlugin'>, 'SMSPlugin': <class 'SMSPlugin'>}
```

#### `__init_subclass__` с параметрами

```python
class Serializable:
    """Базовый класс с настраиваемой сериализацией."""

    def __init_subclass__(cls, *, format="json", exclude=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._serialize_format = format
        cls._exclude_fields = exclude or set()

    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
            if k not in self._exclude_fields
        }

class User(Serializable, format="yaml", exclude={"password"}):
    def __init__(self, name, password):
        self.name = name
        self.password = password

u = User("alice", "secret")
print(u.to_dict())  # {'name': 'alice'}  — password исключён
print(User._serialize_format)  # yaml
```

### 3. Написание метакласса: `__new__` и `__init__`

Метакласс переопределяет создание класса. Аналогия:

| Обычный класс | Метакласс |
|---|---|
| `MyClass()` → `__new__` → `__init__` → экземпляр | `MetaClass(name, bases, ns)` → `__new__` → `__init__` → класс |
| `obj = MyClass()` | `cls = MetaClass(name, bases, ns)` |

```python
class LoggingMeta(type):
    """Метакласс, который логирует создание каждого класса."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        print(f"[META] Создаю класс: {name}")
        print(f"       Базовые классы: {[b.__name__ for b in bases]}")
        print(f"       Атрибуты: {[k for k in namespace if not k.startswith('_')]}")

        # Создаём класс через type.__new__
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        return cls

    def __init__(cls, name, bases, namespace, **kwargs):
        print(f"[META] Инициализирую класс: {name}")
        cls._created_at = "2024-01-01"  # Добавляем атрибут классу
        super().__init__(name, bases, namespace, **kwargs)


class Animal(metaclass=LoggingMeta):
    kingdom = "Animalia"

class Mammal(Animal):
    warm_blooded = True

class Dog(Mammal):
    def bark(self):
        return "Гав!"

# Вывод:
# [META] Создаю класс: Animal
#        Базовые классы: ['object']
#        Атрибуты: ['kingdom']
# [META] Инициализирую класс: Animal
# [META] Создаю класс: Mammal
#        Базовые классы: ['Animal']
#        Атрибуты: ['warm_blooded']
# [META] Инициализирую класс: Mammal
# [META] Создаю класс: Dog
#        Базовые классы: ['Mammal']
#        Атрибуты: ['bark']
# [META] Инициализирую класс: Dog

print(Dog._created_at)  # 2024-01-01 — добавлено метаклассом
```

### 4. Реальные применения метаклассов

#### 4.1. Реестр классов (как Django ORM)

```python
class RegistryMeta(type):
    """Метакласс, автоматически регистрирующий все подклассы."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Не регистрируем базовый класс
        if name != "Model":
            if not hasattr(mcs, "_registry"):
                mcs._registry = {}
            mcs._registry[name.lower()] = cls

        return cls


class Model(metaclass=RegistryMeta):
    """Базовый класс для всех моделей."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_registry(cls):
        return RegistryMeta._registry


class User(Model):
    table = "users"

class Product(Model):
    table = "products"

class Order(Model):
    table = "orders"

print(Model.get_registry())
# {'user': <class 'User'>, 'product': <class 'Product'>, 'order': <class 'Order'>}
```

#### 4.2. Синглтон через метакласс

```python
class SingletonMeta(type):
    """Метакласс, гарантирующий единственный экземпляр класса."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        print(f"Создано подключение к {connection_string}")

    def query(self, sql):
        return f"Выполняю: {sql}"


db1 = Database("postgres://localhost:5432/mydb")
db2 = Database("mysql://localhost:3306/other")  # Игнорируется
print(db1 is db2)  # True
print(db1.connection_string)  # postgres://localhost:5432/mydb
```

#### 4.3. Автоматическая проверка реализации абстрактных методов

```python
class StrictABCMeta(type):
    """
    Метакласс, который запрещает создание экземпляра, если
    не все abstractmethod реализованы.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # Собираем все абстрактные методы
        abstract_methods = set()
        for base in bases:
            for attr_name in dir(base):
                attr = getattr(base, attr_name, None)
                if getattr(attr, "__is_abstract__", False):
                    abstract_methods.add(attr_name)

        # Проверяем, что все они переопределены
        for method_name in abstract_methods:
            method = namespace.get(method_name)
            if method is None or getattr(method, "__is_abstract__", False):
                continue  # Всё ещё абстрактный
            # Проверяем, что переопределён
            if not callable(method):
                raise TypeError(f"{method_name} должен быть вызываемым")

        return cls


def abstractmethod(func):
    """Маркер абстрактного метода."""
    func.__is_abstract__ = True
    return func


class Storage(metaclass=StrictABCMeta):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self, key):
        pass


class FileStorage(Storage):
    def save(self, data):
        print(f"Сохраняю {data} в файл")

    def load(self, key):
        return f"Данные для {key}"
```

#### 4.4. Автоматическое логирование методов

```python
import functools

class AutoLogMeta(type):
    """Метакласс, который оборачивает все публичные методы в логирование."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                namespace[attr_name] = mcs._wrap_with_logging(
                    attr_name, attr_value
                )
        return super().__new__(mcs, name, bases, namespace, **kwargs)

    @staticmethod
    def _wrap_with_logging(method_name, method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            print(f"[LOG] Вызов {self.__class__.__name__}.{method_name}")
            result = method(self, *args, **kwargs)
            print(f"[LOG] {self.__class__.__name__}.{method_name} → {result!r}")
            return result
        return wrapper


class Calculator(metaclass=AutoLogMeta):
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

    def _helper(self):  # Не логируется (начинается с _)
        return "private"


calc = Calculator()
print(calc.add(3, 4))
# [LOG] Вызов Calculator.add
# [LOG] Calculator.add → 7
# 7
```

### 5. Когда НЕ использовать метаклассы

Метаклассы — мощный инструмент, но с большой силой приходит большая ответственность. Вот признаки, что метакласс не нужен:

1. **Задачу можно решить через `__init_subclass__`** — это всегда предпочтительнее
2. **Задачу можно решить через декоратор класса** — `@decorator` проще понять
3. **Задачу можно решить через наследование** — просто создайте базовый класс
4. **Метакласс делает что-то «неожиданное»** — код должен быть очевиден

```python
# ❌ Метакласс для того, что можно сделать через __init_subclass__
class BadMeta(type):
    def __init__(cls, name, bases, ns):
        cls._registry = {}
        super().__init__(name, bases, ns)

# ✅ То же самое через __init_subclass__
class Base:
    _registry = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Base._registry[cls.__name__] = cls

# ❌ Метакласс для того, что можно сделать декоратором
class AddMethodMeta(type):
    def __new__(mcs, name, bases, ns):
        ns["greet"] = lambda self: "Hello"
        return super().__new__(mcs, name, bases, ns)

# ✅ То же самое через декоратор класса
def add_greet(cls):
    cls.greet = lambda self: "Hello"
    return cls

@add_greet
class MyClass:
    pass
```

### 6. Сравнение с аналогами в других языках

| Аспект | Python (метаклассы) | Java (рефлексия) | C++ (шаблоны) | JavaScript (prototype) |
|---|---|---|---|---|
| **Время работы** | Время создания класса (импорт) | Время выполнения | Время компиляции | Время выполнения |
| **Изменяет класс** | Да, полностью | Только через рефлексию (ограниченно) | Генерирует код на этапе компиляции | Да, прототип можно менять |
| **Синтаксис** | `metaclass=Meta` | `java.lang.reflect` | `template<typename T>` | `Object.setPrototypeOf` |
| **Типобезопасность** | Динамическая | Статическая | Статическая | Динамическая |
| **Основное применение** | ORM, регистрация, API | Аннотации, прокси | Обобщённое программирование | Миксины, прототипы |

**Ключевое отличие Python:** в Python классы создаются **во время выполнения**, и метакласс может изменить всё: имя, базовые классы, пространство имён. В C++ шаблоны работают на этапе компиляции и генерируют код, но не могут изменить уже существующий класс. В Java рефлексия позволяет инспектировать классы, но не переопределять их создание.

#### Java: рефлексия (только инспекция)

```java
// Java: рефлексия позволяет читать метаданные, но не менять класс
Class<?> cls = User.class;
for (Field field : cls.getDeclaredFields()) {
    System.out.println(field.getName());
}
// Нельзя автоматически добавить метод или изменить поведение создания
```

#### Python: метакласс (полный контроль)

```python
# Python: метакласс может добавить методы, изменить атрибуты,
# зарегистрировать класс — всё во время импорта
class AutoTableNameMeta(type):
    def __new__(mcs, name, bases, ns):
        if "table" not in ns:
            ns["table"] = name.lower() + "s"
        return super().__new__(mcs, name, bases, ns)
```

### 7. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
# ✅ Метакласс для ORM (как Django)
class ModelBase(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs, **kwargs)

        # Собираем поля из всех базовых классов
        fields = {}
        for base in bases:
            if hasattr(base, "_fields"):
                fields.update(base._fields)

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                fields[attr_name] = attr_value

        attrs["_fields"] = fields
        return super().__new__(mcs, name, bases, attrs, **kwargs)

# ✅ __init_subclass__ для регистрации плагинов
class Plugin:
    plugins = []
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.plugins.append(cls)
```

#### ❌ Анти-паттерны

```python
# ❌ Изменение семантики языка
class ConfusingMeta(type):
    def __new__(mcs, name, bases, ns):
        # Переворачивает все строки в классе — КОШМАР!
        for key, val in ns.items():
            if isinstance(val, str):
                ns[key] = val[::-1]
        return super().__new__(mcs, name, bases, ns)

# ❌ Скрытые побочные эффекты
class EvilMeta(type):
    def __new__(mcs, name, bases, ns):
        import os
        os.system(f"echo 'Класс {name} создан'")  # Побочный эффект при импорте!
        return super().__new__(mcs, name, bases, ns)

# ❌ Смешивание метаклассов без учёта конфликтов
class MetaA(type):
    pass
class MetaB(type):
    pass

# class Foo(metaclass=MetaA): pass
# class Bar(Foo, metaclass=MetaB): pass  # TypeError: метаклассы конфликтуют!

# ❌ Метакласс только ради метакласса
class UselessMeta(type):
    pass  # Ничего не делает — зачем?

class MyClass(metaclass=UselessMeta):
    pass
```

---

## Практическое задание

### Задача: Фреймворк для валидации данных

Создайте модуль `validator_framework.py` с системой классов на основе метаклассов:

1. **`ValidatorMeta`** — метакласс, который:
   - Собирает все методы, имена которых начинаются с `validate_`, в словарь `_validators`
   - Автоматически украшает их `@staticmethod` (если они не принимают `self`)
   - Добавляет классовый метод `validate(data)`, который последовательно вызывает все валидаторы

2. **`BaseValidator`** — базовый класс с метаклассом `ValidatorMeta`:
   - Метод `validate(data)` проходит по `_validators` и собирает ошибки
   - Возвращает словарь `{"valid": bool, "errors": [str, ...]}`

3. **`UserValidator(BaseValidator)`** — пример использования:
   - `validate_name(name)` — проверяет, что имя не пустое и состоит из букв
   - `validate_email(email)` — проверяет формат email через regex
   - `validate_age(age)` — проверяет, что возраст в диапазоне 18-120

4. **`ProductValidator(BaseValidator)`** — ещё один пример:
   - Свои валидаторы для товара (название, цена, количество)

**Требования:**

- `ValidatorMeta` должен корректно обрабатывать наследование (валидаторы родителя + свои)
- Ошибки собираются из всех валидаторов, а не прерываются на первом же
- Включите docstrings и аннотации типов
- Продемонстрируйте работу на нескольких примерах данных

**Критерии оценки:**

- Корректная работа метакласса при наследовании
- Чистота кода метакласса (понятные имена, комментарии)
- Отсутствие хрупких решений (например, разбор строкового представления)
- Использование `super().__new__` и `super().__init_subclass__`

---

## Дополнительные материалы

- [Python docs: Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses)
- [PEP 3115 — Metaclasses in Python 3000](https://peps.python.org/pep-3115/)
- [PEP 487 — Simpler customisation of class creation](https://peps.python.org/pep-0487/)
- [David Beazley: "Python Metaclasses" (PyCon 2013)](https://www.youtube.com/watch?v=sPiWg5jSoZI)
- [Tim Peters: "Metaclasses" (The Best of both Worlds)](https://www.python.org/doc/essays/metaclasses/)
- [Real Python: Metaclasses in Python](https://realpython.com/python-metaclasses/)
- [Stack Overflow: What are metaclasses in Python?](https://stackoverflow.com/questions/100003/what-are-metaclasses-in-python) — легендарный ответ e-satis