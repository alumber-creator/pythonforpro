---
title: "Декораторы: введение в метапрограммирование"
order: 5
tags:
  - декораторы
  - метапрограммирование
  - замыкания
  - wraps
prerequisites: "Функции, замыкания, *args/**kwargs"
objective: "Научиться создавать и применять декораторы для модификации поведения функций"
---

# Декораторы: введение в метапрограммирование

## 🎯 Цель урока

Освоить создание и применение декораторов — от простых (тайминг, логирование, кэширование) до декораторов с аргументами и классов-декораторов. Понять, как декораторы реализуют сквозную функциональность без дублирования кода.

## 📋 Предпосылки

Вы понимаете, что функции в Python — объекты первого класса, умеете создавать замыкания и работаете с `*args` и `**kwargs`.

---

## Введение

Декораторы — это, пожалуй, самая «питонячья» фича языка. Они позволяют модифицировать поведение функций и классов, не меняя их исходный код, и реализуют сквозную функциональность (cross-cutting concerns) — логирование, кэширование, проверку прав, тайминг — без дублирования.

В Java для этого нужны аннотации + AOP-фреймворки (AspectJ, Spring AOP). В C++ — шаблоны и макросы. В Python — просто функция, которая принимает функцию и возвращает функцию. Никакой магии: декоратор — это всего лишь синтаксический сахар для применения функции высшего порядка.

---

## Основная часть

### 1. Функции как объекты — повторение

Прежде чем писать декораторы, убедимся, что мы понимаем: функции в Python — это объекты.

```python
def greet(name):
    return f"Hello, {name}!"


# Функция — объект
print(type(greet))          # <class 'function'>
print(greet.__name__)       # greet

# Можно присвоить переменной
say_hello = greet
print(say_hello("Alice"))   # Hello, Alice!

# Можно передать как аргумент
def apply(func, arg):
    return func(arg)


print(apply(greet, "Bob"))  # Hello, Bob!

# Можно определить внутри другой функции
def make_multiplier(factor):
    def multiplier(x):
        return x * factor
    return multiplier  # Возвращаем функцию!


double = make_multiplier(2)
print(double(5))  # 10
```

Именно это свойство делает декораторы возможными.

### 2. Синтаксис декоратора

Декоратор — это функция, которая принимает функцию и возвращает (обычно) другую функцию:

```python
@decorator
def target():
    pass

# Эквивалентно:
def target():
    pass
target = decorator(target)
```

Символ `@` — синтаксический сахар. Никакой магии.

### 3. Первый декоратор: тайминг

```python
import time
import functools


def timer(func):
    """Декоратор: выводит время выполнения функции."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} выполнилась за {elapsed:.4f} сек")
        return result

    return wrapper


@timer
def slow_function():
    """Имитация медленной работы."""
    time.sleep(0.5)
    return "Готово"


result = slow_function()
# Выведет: slow_function выполнилась за 0.5XXX сек
print(result)  # Готово
print(slow_function.__name__)  # slow_function (благодаря @wraps)
print(slow_function.__doc__)   # Имитация медленной работы.
```

Разберём по шагам:
1. `timer` принимает функцию `func` и возвращает `wrapper`
2. `wrapper` оборачивает вызов `func`, добавляя замер времени
3. `@functools.wraps(func)` копирует метаданные (`__name__`, `__doc__`, etc.) из `func` в `wrapper`

### 4. `functools.wraps` — почему это важно

Без `@wraps` декоратор «теряет» метаданные оригинальной функции:

```python
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@bad_decorator
def greet(name):
    """Приветствует пользователя."""
    return f"Hello, {name}!"


print(greet.__name__)  # wrapper — а должно быть greet!
print(greet.__doc__)   # None — а должна быть документация!
help(greet)            # Показывает документацию wrapper, а не greet
```

**Всегда используйте `@functools.wraps(func)` при написании декораторов.**

### 5. Декоратор для логирования

```python
import functools
import logging


logger = logging.getLogger(__name__)


def log_call(func):
    """Логирует вызов функции: имя, аргументы, результат."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(
            "Вызов %s с args=%s, kwargs=%s",
            func.__name__,
            args,
            kwargs,
        )
        try:
            result = func(*args, **kwargs)
            logger.debug("%s вернула %s", func.__name__, result)
            return result
        except Exception as e:
            logger.exception("%s вызвала исключение: %s", func.__name__, e)
            raise

    return wrapper


@log_call
def divide(a, b):
    return a / b


divide(10, 2)  # Логирует: вызов divide, результат 5.0
```

### 6. Декоратор для кэширования (мемоизации)

```python
import functools


def memoize(func):
    """Кэширует результаты вызова функции."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


@memoize
def fibonacci(n):
    """Рекурсивное вычисление числа Фибоначчи с кэшированием."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Без кэширования — экспоненциальная сложность O(2^n)
# С кэшированием — O(n)
print(fibonacci(100))  # 354224848179261915075 — мгновенно!
```

В стандартной библиотеке есть более мощный аналог:

```python
from functools import lru_cache


@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

`lru_cache` автоматически вытесняет старые записи при превышении `maxsize` и работает с keyword-аргументами.

### 7. Декораторы с аргументами

Иногда декоратору нужны собственные параметры. Например, `@timer(threshold=0.1)` — выводить время только если оно больше 0.1 сек.

Для этого нужна «фабрика декораторов» — функция, которая возвращает декоратор:

```python
import functools
import time


def timer(threshold: float = 0.0):
    """Фабрика декораторов: создаёт декоратор с порогом."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > threshold:
                print(f"{func.__name__} — {elapsed:.4f} сек (порог: {threshold}s)")
            return result

        return wrapper

    return decorator


@timer(threshold=0.1)  # Вызываем timer(), получаем decorator, применяем к функции
def fast():
    return sum(range(1000))


@timer(threshold=0.0)  # Порог 0 — всегда выводить
def slow():
    time.sleep(0.5)
    return "done"


fast()   # Ничего не выводит (слишком быстро)
slow()   # Выводит: slow — 0.5XXX сек (порог: 0.0s)
```

Разбор:
1. `timer(threshold=0.1)` вызывается и возвращает `decorator`
2. `decorator(fast)` вызывается и возвращает `wrapper`
3. `wrapper` — это то, что теперь называется `fast`

То есть:

```python
@timer(threshold=0.1)
def fast():
    ...

# Эквивалентно:
fast = timer(threshold=0.1)(fast)
```

### 8. Несколько декораторов на одной функции

Декораторы применяются снизу вверх:

```python
@decorator_a
@decorator_b
@decorator_c
def func():
    pass

# Эквивалентно:
func = decorator_a(decorator_b(decorator_c(func)))
```

Практический пример:

```python
@timer(threshold=0.01)
@log_call
@memoize
def expensive_computation(x, y):
    """Дорогостоящее вычисление."""
    time.sleep(0.1)
    return x ** y + y ** x


# Вызов: memoize -> log_call -> timer -> expensive_computation
result = expensive_computation(3, 4)
```

### 9. Встроенные декораторы Python

#### `@staticmethod`

Метод, который не получает ни `self`, ни `cls`:

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b


MathUtils.add(1, 2)  # 3 — вызывается без экземпляра
```

#### `@classmethod`

Метод, который получает класс (`cls`) вместо экземпляра (`self`):

```python
class User:
    all_users = []

    def __init__(self, name):
        self.name = name
        self.all_users.append(self)

    @classmethod
    def from_json(cls, json_str):
        """Альтернативный конструктор."""
        import json

        data = json.loads(json_str)
        return cls(data["name"])

    @classmethod
    def count(cls):
        return len(cls.all_users)


user = User.from_json('{"name": "Alice"}')
print(User.count())  # 1
```

#### `@property`

Превращает метод в вычисляемое свойство (см. урок 1 для подробного примера):

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self._radius = value

    @property
    def area(self):
        """Площадь круга — вычисляемое свойство."""
        import math

        return math.pi * self._radius ** 2


c = Circle(5)
print(c.area)    # 78.539... — как атрибут, не c.area()
c.radius = 10    # Валидация через setter
```

### 10. Классы как декораторы

Декоратор не обязан быть функцией — класс тоже может быть декоратором, если реализует `__call__`:

```python
import functools


class CountCalls:
    """Декоратор-класс: считает количество вызовов функции."""

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Вызов #{self.count} функции {self.func.__name__}")
        return self.func(*args, **kwargs)


@CountCalls
def say_hello():
    print("Hello!")


say_hello()  # Вызов #1 функции say_hello \n Hello!
say_hello()  # Вызов #2 функции say_hello \n Hello!
say_hello()  # Вызов #3 функции say_hello \n Hello!
```

Класс-декоратор удобен, когда нужно хранить состояние между вызовами (счётчик, статистика, кэш).

### 11. Декораторы с сохранением состояния через замыкание

Альтернатива классу — замыкание с `nonlocal`:

```python
def count_calls(func):
    """Функциональный аналог CountCalls — использует замыкание."""
    calls = 0

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal calls
        calls += 1
        print(f"Вызов #{calls} функции {func.__name__}")
        return func(*args, **kwargs)

    return wrapper
```

### 12. Сравнение с другими языками

#### Java аннотации

Java-аннотации — это пассивные метаданные. Сами по себе они ничего не делают; нужен фреймворк (Spring, Hibernate), чтобы их обработать:

```java
// Java — аннотация + фреймворк для обработки
@Timed(name = "myMethod")
public String myMethod() {
    // ...
}
```

```python
# Python — декоратор сам содержит логику
@timer
def my_method():
    ...
```

Python-декораторы активны: они сразу меняют поведение функции, без внешнего фреймворка.

#### C# Attributes

Аналогично Java: атрибуты — это пассивные метаданные, требующие рефлексии для обработки. Python-декораторы — это исполняемый код.

#### JavaScript декораторы

JavaScript декораторы (Stage 3, TC39) похожи на Python, но применяются к классам и их членам:

```javascript
// JavaScript (TC39 proposal)
function log(target, name, descriptor) {
    const original = descriptor.value;
    descriptor.value = function (...args) {
        console.log(`Вызов ${name}`);
        return original.apply(this, args);
    };
    return descriptor;
}

class MyClass {
    @log
    method() {}
}
```

```python
# Python — декораторы применяются шире: к функциям, методам, классам
@log
def function():
    pass


@log
class MyClass:
    @log
    def method(self):
        pass
```

Python-декораторы более универсальны: они работают с любыми callable, включая standalone-функции и целые классы.

---

## Практическое задание

### Задание 1: Декоратор `retry`

Напишите декоратор `retry(max_attempts=3, delay=0)`, который:
- При исключении повторяет вызов функции до `max_attempts` раз
- Между попытками ждёт `delay` секунд
- Если все попытки исчерпаны — пробрасывает последнее исключение

```python
import functools
import time


def retry(max_attempts: int = 3, delay: float = 0.0):
    """Повторяет вызов функции при исключении."""
    # Ваш код
    pass


# Тест:
import random


@retry(max_attempts=5, delay=0.1)
def unreliable():
    if random.random() < 0.7:
        raise ConnectionError("Нет связи")
    return "Успех!"


print(unreliable())  # Пробует до 5 раз, потом сдаётся или возвращает "Успех!"
```

### Задание 2: Декоратор `validate`

Напишите декоратор `validate(**checks)`, который проверяет аргументы функции перед вызовом. Ключи — имена параметров, значения — функции-предикаты.

```python
def validate(**checks):
    """Проверяет аргументы функции перед вызовом."""
    # Ваш код
    pass


@validate(age=lambda x: x >= 0, name=lambda x: len(x) > 0)
def create_user(name: str, age: int):
    return {"name": name, "age": age}


create_user("Alice", 25)  # OK
create_user("", 25)       # ValueError: name failed validation
create_user("Bob", -5)    # ValueError: age failed validation
```

### Задание 3: Декоратор `singleton`

Напишите декоратор класса `singleton`, который гарантирует, что у класса может быть только один экземпляр:

```python
def singleton(cls):
    """Декоратор класса: паттерн Singleton."""
    # Ваш код
    pass


@singleton
class Database:
    def __init__(self):
        print("Инициализация соединения с БД")
        self.connected = True


db1 = Database()  # Выводит: Инициализация соединения с БД
db2 = Database()  # Ничего не выводит
print(db1 is db2)  # True — это один и тот же объект
```

---

## Дополнительные материалы

### Документация

- [PEP 318 — Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 3129 — Class Decorators](https://peps.python.org/pep-3129/)
- [functools documentation](https://docs.python.org/3/library/functools.html)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 9 (декораторы и замыкания).
- **«Effective Python»**, Бретт Слаткин — советы 22-26 о декораторах и замыканиях.

### Статьи

- [Real Python: Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Python Patterns: Decorators](https://python-patterns.guide/)

### Видео

- **«So you want to be a Python expert?»**, Джеймс Пауэлл (PyData 2017) — глубокое погружение в метапрограммирование.