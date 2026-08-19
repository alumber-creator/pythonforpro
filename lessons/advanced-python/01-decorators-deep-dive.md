---
title: "Декораторы: глубокое погружение"
order: 1
tags: ["декораторы", "метапрограммирование", "wraps", "классы-декораторы"]
prerequisites: "Функции, замыкания, базовое понимание декораторов"
objective: "Освоить продвинутые паттерны декораторов: классы-декораторы, декораторы с состоянием, вложенные декораторы"
---

## Введение

Декораторы — одна из самых выразительных возможностей Python. На первый взгляд это просто синтаксический сахар: `@decorator` над функцией. Но за этим скрывается мощный механизм метапрограммирования, позволяющий изменять поведение функций и классов без изменения их исходного кода.

В этом уроке мы выйдем за рамки базового `@my_decorator` и исследуем внутреннее устройство декораторов, научимся создавать классы-декораторы, декораторы с состоянием и разберём стековое наложение декораторов. Вы узнаете, как работает `functools.wraps`, почему `@lru_cache` — это не просто кеш, и как `@singledispatch` реализует полиморфизм на уровне функций.

### 🎯 Цель урока

К концу этого урока вы сможете:

- Объяснить, как именно декоратор преобразует функцию на уровне байт-кода
- Создавать классы-декораторы, сохраняющие состояние между вызовами
- Строить цепочки из нескольких декораторов и предсказывать порядок их выполнения
- Применять стандартные декораторы из `functools` в реальных проектах
- Отличать идиоматичные паттерны от анти-паттернов

### 📋 Предпосылки

Вы должны уверенно владеть функциями высшего порядка, понимать механизм замыканий и иметь опыт написания простых декораторов вроде `@staticmethod` или самодельного `@timer`.

---

## Основная часть

### 1. Как декоратор работает на самом деле

Синтаксис `@decorator` — это всего лишь удобная запись для:

```python
@decorator
def func():
    pass

# Эквивалентно:
def func():
    pass
func = decorator(func)
```

Декоратор — это вызываемый объект, который принимает один вызываемый объект и возвращает другой (или тот же) вызываемый объект. Ключевой вывод: **декоратор применяется один раз, в момент определения функции, а не при каждом её вызове**.

```python
def log_call(func):
    """Простой декоратор: логирует каждый вызов функции."""
    def wrapper(*args, **kwargs):
        print(f"[LOG] Вызов {func.__name__} с args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} вернула {result!r}")
        return result
    return wrapper

@log_call
def add(a, b):
    return a + b

# Декорирование произошло во время определения add.
# Теперь add — это на самом деле wrapper.
print(add.__name__)  # wrapper — проблема!
```

#### Проблема: потеря метаданных

Когда декоратор возвращает `wrapper`, теряются `__name__`, `__doc__`, `__module__` и другие метаданные исходной функции. `functools.wraps` решает эту проблему, копируя атрибуты:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Вызов {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    """Складывает два числа."""
    return a + b

print(add.__name__)  # add
print(add.__doc__)   # Складывает два числа.
```

#### Что именно делает `@wraps`?

`wraps` — это тоже декоратор, который копирует `__module__`, `__name__`, `__qualname__`, `__annotations__`, `__doc__` и `__dict__` из `func` в `wrapper`, а также устанавливает `wrapper.__wrapped__ = func` для доступа к исходной функции.

```python
# Пример: ручная реализация упрощённого wraps
def my_wraps(original):
    def decorator(wrapper):
        wrapper.__name__ = original.__name__
        wrapper.__doc__ = original.__doc__
        wrapper.__module__ = original.__module__
        wrapper.__wrapped__ = original
        return wrapper
    return decorator
```

### 2. Декораторы с состоянием

Часто требуется, чтобы декоратор запоминал данные между вызовами. Есть два подхода: замыкание и класс.

#### Подход через замыкание (фабрика декораторов)

```python
def count_calls(func):
    """Считает количество вызовов декорированной функции."""
    calls = 0  # Состояние в замыкании

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal calls
        calls += 1
        print(f"[COUNT] {func.__name__} вызвана {calls} раз(а)")
        return func(*args, **kwargs)

    return wrapper

@count_calls
def greet(name):
    return f"Привет, {name}!"

greet("Анна")  # [COUNT] greet вызвана 1 раз(а)
greet("Борис") # [COUNT] greet вызвана 2 раз(а)
```

#### Продвинутый пример: декоратор `@retry` с настраиваемыми параметрами

```python
import time
import random
from functools import wraps

def retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    """
    Повторяет вызов функции при возникновении исключения.

    Параметры:
        max_attempts: максимальное число попыток
        delay: начальная задержка между попытками (секунды)
        backoff: множитель задержки (экспоненциальный рост)
        exceptions: кортеж исключений, которые нужно перехватывать
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            f"{func.__name__} не выполнена после {max_attempts} попыток"
                        ) from e
                    print(
                        f"[RETRY] {func.__name__}: попытка {attempt}/{max_attempts} "
                        f"неудачна ({e}). Повтор через {current_delay:.1f}с..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5, backoff=1.5, exceptions=(ConnectionError, TimeoutError))
def fetch_data(url):
    if random.random() < 0.7:
        raise ConnectionError("Сеть недоступна")
    return f"Данные с {url}"

# fetch_data теперь автоматически повторяет попытки при сбоях сети
```

### 3. Классы-декораторы

Класс может быть декоратором, если он реализует метод `__call__`. Это удобно, когда нужно хранить сложное состояние.

#### Простой класс-декоратор

```python
class CountCalls:
    """Декоратор-класс: считает вызовы функции."""

    def __init__(self, func):
        wraps(func)(self)       # Копируем метаданные
        self._func = func
        self._calls = 0

    def __call__(self, *args, **kwargs):
        self._calls += 1
        print(f"[COUNT] {self._func.__name__}: вызов #{self._calls}")
        return self._func(*args, **kwargs)

@CountCalls
def multiply(x, y):
    return x * y

multiply(2, 3)  # [COUNT] multiply: вызов #1
multiply(4, 5)  # [COUNT] multiply: вызов #2
```

#### Класс-декоратор с параметрами

```python
class Throttle:
    """
    Ограничивает частоту вызовов функции.

    Параметры:
        min_interval: минимальный интервал между вызовами (секунды)
    """

    def __init__(self, min_interval: float):
        self._min_interval = min_interval
        self._last_call = 0.0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                wait = self._min_interval - elapsed
                print(f"[THROTTLE] Ожидание {wait:.2f}с...")
                time.sleep(wait)
            result = func(*args, **kwargs)
            self._last_call = time.monotonic()
            return result
        return wrapper

@Throttle(min_interval=2.0)
def limited_api_call(endpoint):
    return f"Ответ от {endpoint}"

# Вызовы limited_api_call будут происходить не чаще чем раз в 2 секунды
```

### 4. Стекирование декораторов: порядок имеет значение

Когда на функцию навешивается несколько декораторов, порядок их применения критичен:

```python
@decorator_a   # применяется третьим (самым внешним)
@decorator_b   # применяется вторым
@decorator_c   # применяется первым (самым внутренним)
def func():
    pass

# Эквивалентно:
# func = decorator_a(decorator_b(decorator_c(func)))
```

#### Наглядная демонстрация порядка

```python
def add_tag(tag):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return f"<{tag}>{func(*args, **kwargs)}</{tag}>"
        return wrapper
    return decorator

@add_tag("div")   # Внешний: оборачивает результат в <div>
@add_tag("span")  # Внутренний: оборачивает результат в <span>
def content():
    return "Hello"

print(content())  # <div><span>Hello</span></div>
```

**Правило: внутренний декоратор выполняется первым.** В приведённом примере сначала `content()` оборачивается в `<span>`, затем результат — в `<div>`.

#### Практический пример: аутентификация + логирование

```python
def authenticate(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not getattr(user, "is_authenticated", False):
            raise PermissionError("Пользователь не аутентифицирован")
        return func(user, *args, **kwargs)
    return wrapper

def log_action(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        print(f"[AUDIT] Пользователь {user.name} выполняет {func.__name__}")
        return func(user, *args, **kwargs)
    return wrapper

class User:
    def __init__(self, name, is_authenticated=True):
        self.name = name
        self.is_authenticated = is_authenticated

@authenticate   # сначала проверка прав
@log_action     # потом логирование
def delete_account(user):
    return f"Аккаунт {user.name} удалён"

user = User("alice")
print(delete_account(user))
# [AUDIT] Пользователь alice выполняет delete_account
# Аккаунт alice удалён

# Если бы порядок был обратным, логирование сработало бы
# даже для неаутентифицированного пользователя — утечка информации!
```

### 5. Декорирование классов

Декораторы можно применять не только к функциям, но и к целым классам. Это мощный приём метапрограммирования.

```python
def add_repr(cls):
    """Автоматически добавляет метод __repr__ на основе полей __init__."""
    # Получаем имена параметров из __init__
    import inspect
    sig = inspect.signature(cls.__init__)
    params = list(sig.parameters.keys())[1:]  # Пропускаем 'self'

    def __repr__(self):
        attrs = ", ".join(f"{p}={getattr(self, p, None)!r}" for p in params)
        return f"{cls.__name__}({attrs})"

    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p)  # Point(x=1, y=2)

@add_repr
class Rectangle:
    def __init__(self, width, height, color="black"):
        self.width = width
        self.height = height
        self.color = color

r = Rectangle(10, 20, color="red")
print(r)  # Rectangle(width=10, height=20, color='red')
```

#### Декоратор `@singleton`

```python
def singleton(cls):
    """Делает класс синглтоном: только один экземпляр."""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url="localhost:5432"):
        self.url = url
        print(f"Создано подключение к {url}")

db1 = DatabaseConnection("prod:5432")
db2 = DatabaseConnection("staging:5432")  # Вернёт тот же экземпляр
print(db1 is db2)                         # True
print(db1.url)                            # prod:5432 — второй вызов проигнорирован
```

### 6. Стандартные декораторы из `functools`

#### `@lru_cache` — мемоизация с вытеснением

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Вычисляет n-е число Фибоначчи рекурсивно."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Без кеша: O(2^n). С кешем: O(n) — каждое значение вычисляется один раз.
print(fibonacci(100))  # 354224848179261915075 — мгновенно!

# Инспекция кеша
print(fibonacci.cache_info())
# CacheInfo(hits=98, misses=101, maxsize=128, currsize=101)
```

#### `@total_ordering` — все операторы сравнения из двух

```python
from functools import total_ordering

@total_ordering
class Version:
    """Версия в формате major.minor.patch."""

    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    def _as_tuple(self):
        return (self.major, self.minor, self.patch)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() < other._as_tuple()

    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

# __le__, __gt__, __ge__ сгенерированы автоматически!
v1 = Version(1, 0, 0)
v2 = Version(2, 0, 0)
print(v1 <= v2)  # True
print(v1 >= v2)  # False
```

#### `@singledispatch` — полиморфизм на функциях

```python
from functools import singledispatch
from html import escape as html_escape

@singledispatch
def to_html(obj) -> str:
    """Преобразует объект в HTML-строку."""
    return html_escape(str(obj))

@to_html.register
def _(obj: int) -> str:
    return f'<span class="number">{obj}</span>'

@to_html.register
def _(obj: list) -> str:
    items = "".join(f"<li>{to_html(item)}</li>" for item in obj)
    return f"<ul>{items}</ul>"

@to_html.register
def _(obj: dict) -> str:
    rows = "".join(
        f"<tr><td>{to_html(k)}</td><td>{to_html(v)}</td></tr>"
        for k, v in obj.items()
    )
    return f"<table>{rows}</table>"

print(to_html(42))
# <span class="number">42</span>

print(to_html(["a", 1, {"key": "value"}]))
# <ul><li>a</li><li><span class="number">1</span></li>
#  <li><table><tr><td>key</td><td>value</td></tr></table></li></ul>
```

### 7. Сравнение декораторов с аналогами в других языках

| Возможность | Python | Java | C++ | JavaScript |
|---|---|---|---|---|
| **Синтаксис** | `@decorator` | `@Annotation` | Нет прямого аналога | `@decorator` (Stage 3) |
| **Изменяет поведение?** | Да, произвольно | Нет, только метаданные | — | Да |
| **Время применения** | Определение функции | Сохраняется в байт-коде | — | Определение |
| **Можно применить к классу** | Да | Да | — | Да |
| **Состояние** | Через замыкание / класс | Только константы | — | Через замыкание |
| **Стандартная библиотека** | Богатая (functools) | Ограниченная | — | Пока нет |

**Ключевое отличие Python:** декораторы в Python — это **исполняемый код**, который трансформирует функцию или класс **во время импорта**. Java-аннотации — это пассивные метаданные, которые читаются фреймворками через рефлексию. C++ не имеет синтаксиса декораторов; ближайший аналог — шаблоны и макросы. JavaScript-декораторы (TC39 Stage 3) ближе всего к Python, но с другим синтаксисом и ограничениями.

#### Java-аннотации (только метаданные)

```java
// Java: аннотация — это просто метка, она НЕ выполняет код
@Retention(RetentionPolicy.RUNTIME)
@interface Log { }

class Service {
    @Log  // Ничего не делает! Нужен фреймворк (Spring, AspectJ)
    public void doWork() { }
}
```

#### Python-декоратор (активное поведение)

```python
# Python: декоратор реально изменяет функцию
def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызов {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class Service:
    @log  # Функция уже изменена — работает без фреймворка!
    def do_work(self):
        pass
```

### 8. Идиоматичный код и анти-паттерны

#### ✅ Идиоматично

```python
from functools import wraps

def validate_positive(func):
    """Проверяет, что все аргументы положительны."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for arg in args:
            if isinstance(arg, (int, float)) and arg < 0:
                raise ValueError(f"Отрицательный аргумент: {arg}")
        for val in kwargs.values():
            if isinstance(val, (int, float)) and val < 0:
                raise ValueError(f"Отрицательный аргумент: {val}")
        return func(*args, **kwargs)
    return wrapper

@validate_positive
def sqrt(x):
    return x ** 0.5
```

#### ❌ Анти-паттерны

```python
# ❌ Забыли @wraps — теряются метаданные
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper  # wrapper.__name__ != func.__name__

# ❌ Изменение сигнатуры функции
def bad_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.extra_attr = "сюрприз!"  # Неожиданно для вызывающего
    return wrapper

# ❌ Побочные эффекты при импорте
def bad_side_effect(func):
    print(f"Импортируется {func.__name__}")  # Выполняется при импорте!
    import requests  # Импорт внутри декоратора — медленно
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

# ❌ Мутация аргументов
def bad_mutate(func):
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        data = data.copy()  # Создаём копию — ожидаемо
        data["_extra"] = "sneaky"  # Но всё равно неожиданно
        return func(data, *args, **kwargs)
    return wrapper
```

### 9. Продвинутый пример: композитный декоратор `@ensure`

```python
from functools import wraps

def ensure(*, result_type=None, min_value=None, max_value=None):
    """
    Универсальный декоратор для проверки результата функции.

    Проверяет тип, минимальное и максимальное значение результата.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if result_type is not None and not isinstance(result, result_type):
                raise TypeError(
                    f"{func.__name__} должна вернуть {result_type.__name__}, "
                    f"получен {type(result).__name__}"
                )

            if min_value is not None and result < min_value:
                raise ValueError(
                    f"{func.__name__}: результат {result} < {min_value}"
                )

            if max_value is not None and result > max_value:
                raise ValueError(
                    f"{func.__name__}: результат {result} > {max_value}"
                )

            return result
        return wrapper
    return decorator

@ensure(result_type=int, min_value=0, max_value=100)
def calculate_percentage(part, total):
    return int((part / total) * 100)

print(calculate_percentage(30, 100))  # 30 — ОК
# calculate_percentage(30, 10)  # ValueError: 300 > 100
```

---

## Практическое задание

### Задача: Реализовать систему декораторов для API-клиента

Создайте модуль `api_decorators.py` со следующими декораторами:

1. **`@timeout(seconds)`** — выбрасывает `TimeoutError`, если функция выполняется дольше указанного времени. Используйте `signal.alarm` (Unix) или `threading.Timer` (кроссплатформенно).

2. **`@cache_with_ttl(ttl_seconds)`** — кеширует результат функции на заданное время. После истечения TTL кеш инвалидируется. Реализуйте как класс-декоратор.

3. **`@rate_limit(calls_per_second)`** — ограничивает частоту вызовов: если вызывается чаще, чем разрешено, выбрасывает `RateLimitError`.

4. **`@api_endpoint`** — композитный декоратор, который применяет к функции все три предыдущих декоратора. Должен принимать параметры для каждого из них.

**Требования:**

- Все декораторы должны использовать `@wraps` для сохранения метаданных
- `cache_with_ttl` должен быть классом-декоратором с методом `cache_clear()` для ручной инвалидации
- Включите docstrings и аннотации типов
- Напишите фиктивный API-клиент и продемонстрируйте работу всех декораторов

**Критерии оценки:**

- Корректная работа декораторов при конкурентных вызовах
- Сохранение метаданных функций
- Чистота и читаемость кода (PEP 8)
- Наличие комментариев к сложным участкам

---

## Дополнительные материалы

- [PEP 318 — Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 3129 — Class Decorators](https://peps.python.org/pep-3129/)
- [Python docs: functools — Higher-order functions](https://docs.python.org/3/library/functools.html)
- [Real Python: Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
- [Awesome Python Decorators](https://github.com/lord63/awesome-python-decorator)
- Graham Dumpleton: "How you implemented your Python decorator is wrong" — серия статей о тонкостях `@wraps` и `wrapt`
- [TC39 Proposal: Decorators for JavaScript](https://github.com/tc39/proposal-decorators)