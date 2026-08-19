---
title: "Функции как объекты первого класса"
order: 4
tags: ["функции", "lambda", "замыкания", "аргументы"]
prerequisites: "Урок 3"
objective: "Освоить продвинутые возможности функций: *args, **kwargs, lambda, замыкания"
---

## Введение

В Python функции — это **объекты первого класса** (first-class objects). Это значит, что вы можете:
- Передавать функцию как аргумент другой функции
- Возвращать функцию из функции
- Присваивать функцию переменной
- Хранить функцию в структуре данных

Если вы пришли из Java (до Java 8), это может быть радикальным сдвигом в мышлении. В C++ похожие возможности есть через указатели на функции и `std::function`, но синтаксис тяжеловесен. JavaScript-разработчикам будет знакомо — но Python идёт дальше в выразительности.

Этот урок охватывает продвинутые возможности функций: `*args` и `**kwargs`, lambda-выражения, замыкания, а также сопоставление `map`/`filter` с comprehensions.

### 🎯 Цель урока

Освоить продвинутые возможности функций: `*args`, `**kwargs`, lambda, замыкания. После этого урока вы сможете писать гибкие функции, использовать функции высшего порядка и выбирать между lambda и comprehension.

### 📋 Предпосылки

Вы уверенно владеете базовым синтаксисом (Урок 2) и структурами данных (Урок 3).

---

## Основная часть

### 1. Функции как объекты первого класса

В Python всё является объектом — включая функции. Это фундаментальное свойство языка.

```python
def greet(name):
    return f"Hello, {name}!"

# Функция — это объект
print(type(greet))       # <class 'function'>
print(greet.__name__)    # greet
print(greet.__doc__)     # None (если нет docstring)

# Присваивание функции переменной
say_hello = greet
print(say_hello("Alice"))  # Hello, Alice!

# Передача функции как аргумента
def apply(func, value):
    return func(value)

def double(x):
    return x * 2

def square(x):
    return x ** 2

print(apply(double, 5))  # 10
print(apply(square, 5))  # 25

# Хранение функций в структурах данных
operations = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "div": lambda a, b: a / b,
}

op = operations["mul"]
print(op(6, 7))  # 42
```

**Сравнение с другими языками:**

```python
# Python: функция — объект, передаётся напрямую
def apply(func, x):
    return func(x)

result = apply(str.upper, "hello")
```

```java
// Java (до 8): нужно объявить интерфейс
interface Function<T, R> {
    R apply(T t);
}
// ... и передавать анонимный класс
```

```java
// Java 8+: функциональные интерфейсы + лямбды
Function<String, String> upper = String::toUpperCase;
// или
apply(s -> s.toUpperCase(), "hello");
```

```cpp
// C++: std::function (C++11) или указатели на функции
#include <functional>
std::string apply(std::function<std::string(std::string)> func, std::string x) {
    return func(x);
}
```

```javascript
// JavaScript: функции — объекты первого класса (как в Python)
const apply = (func, x) => func(x);
apply(str => str.toUpperCase(), "hello");
```

JavaScript наиболее близок к Python в этом отношении, но Python добавляет выразительные возможности через `*args`/`**kwargs` и декораторы.

### 2. *args и **kwargs: гибкие аргументы

#### *args: произвольное количество позиционных аргументов

```python
# *args собирает все позиционные аргументы в кортеж
def sum_all(*args):
    """Суммирует любое количество аргументов."""
    print(f"args = {args}, type = {type(args)}")
    return sum(args)

print(sum_all(1, 2))           # args = (1, 2), type = <class 'tuple'> → 3
print(sum_all(1, 2, 3, 4, 5))  # → 15
print(sum_all())                # → 0

# *args — это просто имя; можно использовать любое (но args — конвенция)
def multiply_all(*numbers):
    result = 1
    for n in numbers:
        result *= n
    return result

print(multiply_all(2, 3, 4))  # 24
```

#### **kwargs: произвольное количество именованных аргументов

```python
# **kwargs собирает все keyword-аргументы в словарь
def print_info(**kwargs):
    """Принимает любое количество именованных аргументов."""
    print(f"kwargs = {kwargs}, type = {type(kwargs)}")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

print_info(name="Alice", age=30, city="NYC")
# kwargs = {'name': 'Alice', 'age': 30, 'city': 'NYC'}, type = <class 'dict'>
#   name: Alice
#   age: 30
#   city: NYC
```

#### Комбинирование обычных, *args и **kwargs

Порядок имеет значение: `def func(normal, *args, default=val, **kwargs)`.

```python
def create_user(name, *roles, active=True, **metadata):
    """Создаёт пользователя с ролями и метаданными."""
    return {
        "name": name,
        "roles": list(roles),
        "active": active,
        "metadata": metadata,
    }

# Вызовы
user1 = create_user("Alice")
# {'name': 'Alice', 'roles': [], 'active': True, 'metadata': {}}

user2 = create_user("Bob", "admin", "editor", active=False)
# {'name': 'Bob', 'roles': ['admin', 'editor'], 'active': False, 'metadata': {}}

user3 = create_user("Charlie", "viewer", department="IT", floor=3)
# {'name': 'Charlie', 'roles': ['viewer'], 'active': True, 'metadata': {'department': 'IT', 'floor': 3}}
```

**Таблица: порядок параметров функции**

| Позиция | Тип параметра | Пример | Описание |
|---------|--------------|--------|----------|
| 1 | Позиционные (обязательные) | `name, age` | Должны быть переданы |
| 2 | `*args` | `*roles` | Собирает лишние позиционные |
| 3 | Keyword-only (с default) | `active=True` | Только по имени; после `*args` все параметры — keyword-only |
| 4 | `**kwargs` | `**metadata` | Собирает лишние keyword |

#### Keyword-only аргументы (Python 3+)

```python
# Всё после * — keyword-only аргументы
def configure(host, port, *, timeout=30, ssl=False):
    """host и port — позиционные, timeout и ssl — keyword-only."""
    return f"Connecting to {host}:{port} (timeout={timeout}, ssl={ssl})"

# ✅ Правильно
print(configure("localhost", 8080, timeout=60, ssl=True))

# ❌ Ошибка: keyword-only аргументы нельзя передать позиционно
# print(configure("localhost", 8080, 60, True))  # TypeError!
```

### 3. Распаковка аргументов: * и ** при вызове

Операторы `*` и `**` работают в обе стороны: при определении функции они «собирают» аргументы, а при вызове — «распаковывают».

```python
# Распаковка списка/кортежа в позиционные аргументы
def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
print(add(*numbers))  # add(1, 2, 3) → 6

# Распаковка словаря в keyword-аргументы
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

params = {"name": "Alice", "greeting": "Hi"}
print(greet(**params))  # greet(name="Alice", greeting="Hi") → "Hi, Alice!"

# Комбинирование
def full_greet(greeting, name, punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

args = ["Hello", "World"]
kwargs = {"punctuation": "?"}
print(full_greet(*args, **kwargs))  # full_greet("Hello", "World", punctuation="?")
```

**Сравнение: распаковка в Python vs spread в JavaScript**

```python
# Python
args = [1, 2, 3]
result = func(*args)

kwargs = {"key": "value"}
result = func(**kwargs)
```

```javascript
// JavaScript
const args = [1, 2, 3];
result = func(...args);  // Spread operator

const obj = {key: "value"};
result = func({...obj});  // Spread, но не для именованных параметров
```

### 4. Lambda-выражения: анонимные функции

Lambda в Python — это анонимная функция, которая может содержать **ровно одно выражение** (не может содержать statements: `if`, `for`, `return`, `=`).

```python
# Синтаксис: lambda аргументы: выражение

# Простая lambda
square = lambda x: x ** 2
print(square(5))  # 25

# Lambda с несколькими аргументами
add = lambda a, b: a + b
print(add(3, 4))  # 7

# Lambda с условным выражением (тернарный оператор)
is_even = lambda x: "even" if x % 2 == 0 else "odd"
print(is_even(7))  # odd

# Lambda как аргумент (сортировка по ключу)
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]
sorted_users = sorted(users, key=lambda user: user["age"])
print([u["name"] for u in sorted_users])  # ['Bob', 'Alice', 'Charlie']
```

**Сравнение lambda в разных языках:**

```python
# Python: lambda
lambda x: x * 2
```

```java
// Java: lambda (Java 8+)
x -> x * 2
```

```cpp
// C++: lambda (C++11+)
[](int x) { return x * 2; }
// или с автовыводом типа:
[](auto x) { return x * 2; }
```

```javascript
// JavaScript: arrow function
x => x * 2
```

**Ограничения Python lambda:**
- Только одно выражение — нет `return`, `if` (кроме тернарного), `for`, присваиваний
- Нет docstring
- Нет аннотаций типов

```python
# ❌ Нельзя в lambda
# lambda x: x = x + 1          # Присваивание
# lambda x: return x * 2        # Statement return
# lambda x: for i in x: print(i) # Цикл

# ✅ Если нужно что-то сложнее — используйте обычную def
def complex_operation(x):
    result = x * 2
    if result > 10:
        return result
    return result + 1
```

### 5. Map, Filter, Reduce vs Comprehensions

Python предоставляет функции `map()`, `filter()`, `reduce()` (из `functools`), но в большинстве случаев comprehensions предпочтительнее.

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# map: преобразование каждого элемента
# ❌ С map + lambda
doubled = list(map(lambda x: x * 2, numbers))

# ✅ С list comprehension
doubled = [x * 2 for x in numbers]

# filter: отбор по условию
# ❌ С filter + lambda
evens = list(filter(lambda x: x % 2 == 0, numbers))

# ✅ С list comprehension
evens = [x for x in numbers if x % 2 == 0]

# map + filter вместе
# ❌ С map + filter + lambda
result = list(map(lambda x: x * 2, filter(lambda x: x > 5, numbers)))

# ✅ С list comprehension
result = [x * 2 for x in numbers if x > 5]

# reduce: свёртка
# reduce — единственный случай, где нет простой замены на comprehension
total = reduce(lambda a, b: a + b, numbers)  # 55
# Но даже здесь есть альтернативы:
total = sum(numbers)  # 55 — для суммы используйте sum!
```

**Правило выбора: Map/Filter vs Comprehension**

| Ситуация | Рекомендация |
|----------|-------------|
| Преобразование списка | `[expr for x in iterable]` |
| Фильтрация списка | `[x for x in iterable if cond]` |
| Преобразование + фильтрация | `[expr for x in iterable if cond]` |
| Функция уже существует (например, `str.upper`) | `map(str.upper, names)` — допустимо |
| Сложная логика, не влезающая в comprehension | Обычный цикл `for` |
| Свёртка (reduce) | `sum()`, `min()`, `max()`, `any()`, `all()`, `reduce()` |

**Сравнение с Java Streams:**

```python
# Python: list comprehension
result = [x * 2 for x in numbers if x > 5]
```

```java
// Java: Stream API
var result = numbers.stream()
    .filter(x -> x > 5)
    .map(x -> x * 2)
    .collect(Collectors.toList());
```

Python-версия компактнее, но Java-версия явно показывает последовательность операций (filter → map → collect). Для сложных цепочек Python предлагает выражение-генератор (generator expression):

```python
# Python: generator expression + пайплайн
result = list(
    x * 2
    for x in numbers
    if x > 5
)
```

### 6. Замыкания (closures)

Замыкание — это функция, которая **«запоминает»** значения из охватывающей области видимости, даже когда эта область уже не активна.

```python
def make_multiplier(factor):
    """Возвращает функцию, которая умножает на factor."""
    def multiplier(x):
        return x * factor  # factor — из охватывающей области
    return multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10  (factor = 2 запомнен)
print(triple(5))  # 15  (factor = 3 запомнен)

# Проверка: factor действительно «замкнут»
print(double.__closure__)           # (<cell at ...: int object at ...>,)
print(double.__closure__[0].cell_contents)  # 2
```

**Практический пример: конфигурируемая функция логирования**

```python
def create_logger(prefix, level="INFO"):
    """Создаёт функцию логирования с заданным префиксом."""
    def log(message):
        print(f"[{level}] {prefix}: {message}")
    return log

app_log = create_logger("MyApp", "DEBUG")
db_log = create_logger("Database", "WARN")

app_log("Application started")  # [DEBUG] MyApp: Application started
db_log("Connection timeout")    # [WARN] Database: Connection timeout
```

**Сравнение с другими языками:**

```python
# Python: замыкание
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter
```

```java
// Java: замыкание (Java 8+), но переменная должна быть effectively final
// Для мутабельного состояния нужен AtomicInteger или массив
import java.util.concurrent.atomic.AtomicInteger;
Supplier<Integer> makeCounter() {
    AtomicInteger count = new AtomicInteger(0);
    return () -> count.incrementAndGet();
}
```

```cpp
// C++: замыкание через lambda capture
auto make_counter() {
    int count = 0;
    return [count]() mutable { return ++count; };
}
```

```javascript
// JavaScript: замыкание (классический паттерн)
function makeCounter() {
    let count = 0;
    return () => ++count;
}
```

**Важный нюанс: `nonlocal`**

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count  # Без nonlocal — UnboundLocalError!
        count += 1
        return count
    return counter

# Без nonlocal:
def make_counter_broken():
    count = 0
    def counter():
        # count += 1  # ❌ UnboundLocalError: count не определён локально
        return count  # ✅ чтение работает (захват из closure)
    return counter
```

**Правило `nonlocal` vs `global`:**

| Ключевое слово | Что делает | Область поиска |
|---------------|-----------|---------------|
| (нет) | Читает из охватывающей области | Local → Enclosing → Global → Built-in (LEGB) |
| `nonlocal` | Присваивает в ближайшую охватывающую (не глобальную) область | Enclosing (первая не-local) |
| `global` | Присваивает в глобальную область модуля | Global |

### 7. Декораторы: краткое введение

Декоратор — это функция, которая принимает функцию и возвращает новую, «оборачивая» исходную. Это естественное следствие того, что функции — объекты первого класса.

```python
# Простейший декоратор
def uppercase_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper

@uppercase_decorator
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # HELLO, ALICE!

# То же самое без @-синтаксиса:
# greet = uppercase_decorator(greet)
```

**Практический пример: измерение времени выполнения**

```python
import time
import functools

def timer(func):
    """Декоратор, измеряющий время выполнения функции."""
    @functools.wraps(func)  # Сохраняет __name__ и __doc__ исходной функции
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} executed in {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.5)
    return "Done"

slow_function()  # slow_function executed in 0.5001s
```

### 8. Выражения-генераторы (generator expressions)

Выражение-генератор похоже на list comprehension, но возвращает **ленивый итератор**, а не список.

```python
# List comprehension: создаёт список В ПАМЯТИ сразу
squares_list = [x**2 for x in range(1_000_000)]  # 1 млн элементов в памяти!

# Generator expression: создаёт итератор (лениво)
squares_gen = (x**2 for x in range(1_000_000))    # Почти не занимает памяти!

print(type(squares_gen))  # <class 'generator'>

# Использование: по одному элементу
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1
print(next(squares_gen))  # 4

# Часто передаётся напрямую в функцию, ожидающую итератор
total = sum(x**2 for x in range(1_000_000))  # Без промежуточного списка!
```

**Когда использовать генератор:**
- Большие объёмы данных (файлы, потоки)
- Цепочки операций, где не нужен промежуточный результат
- Бесконечные последовательности

### 9. Анти-паттерны и идиоматический код

#### Анти-паттерн 1: Избыточные lambda

```python
# ❌ Плохо: lambda, которая просто вызывает функцию
sorted(items, key=lambda x: len(x))
map(lambda x: str.upper(x), names)

# ✅ Идиоматично: передача функции напрямую
sorted(items, key=len)
map(str.upper, names)
```

#### Анти-паттерн 2: map/filter там, где лучше comprehension

```python
# ❌ Плохо: map + filter + lambda
result = list(map(lambda x: x * 2, filter(lambda x: x > 0, numbers)))

# ✅ Идиоматично: list comprehension
result = [x * 2 for x in numbers if x > 0]
```

#### Анти-паттерн 3: Злоупотребление lambda

```python
# ❌ Плохо: lambda с if/else несколькими уровнями
process = lambda x: x * 2 if x > 0 else x * 3 if x < 0 else 0

# ✅ Идиоматично: обычная функция
def process(x):
    if x > 0:
        return x * 2
    elif x < 0:
        return x * 3
    else:
        return 0
```

#### Анти-паттерн 4: Присваивание lambda в переменную

```python
# ❌ Плохо: присваивание lambda (PEP 8 и Flake8 предупреждают)
square = lambda x: x ** 2

# ✅ Идиоматично: def
def square(x):
    return x ** 2
```

---

## Практическое задание

### Задание 1: Универсальный сортировщик

Напишите функцию `sort_by(data, key, reverse=False)`, которая принимает:
- `data` — список словарей
- `key` — строка с именем поля для сортировки
- `reverse` — направление сортировки

Используйте lambda для `key` в `sorted()`.

```python
data = [
    {"name": "Alice", "age": 30, "salary": 80000},
    {"name": "Bob", "age": 25, "salary": 65000},
    {"name": "Charlie", "age": 35, "salary": 95000},
    {"name": "Diana", "age": 28, "salary": 72000},
]

# Пример вызова:
# sort_by(data, "age") → сортировка по возрасту
# sort_by(data, "salary", reverse=True) → по зарплате по убыванию
```

### Задание 2: Создайте функцию-фабрику

Напишите функцию `make_formatter(format_string)`:

```python
bold = make_formatter("<b>{}</b>")
italic = make_formatter("<i>{}</i>")
code = make_formatter("<code>{}</code>")

print(bold("Hello"))   # <b>Hello</b>
print(italic("World")) # <i>World</i>
print(code("x = 1"))   # <code>x = 1</code>
```

Используйте замыкание. Проверьте, что `bold.__closure__` содержит переданную строку формата.

### Задание 3: Декоратор `retry`

Напишите декоратор `retry(max_attempts=3, delay=1)`:

```python
import random

@retry(max_attempts=3, delay=1)
def unstable_function():
    """Функция, которая падает в 50% случаев."""
    if random.random() < 0.5:
        raise ValueError("Temporary failure")
    return "Success"

# Декоратор должен:
# - Повторять вызов функции при исключении
# - Делать паузу delay секунд между попытками
# - После max_attempts попыток пробрасывать исключение
# - Использовать functools.wraps для сохранения метаданных
```

### Задание 4: Перепишите идиоматично

```python
# Фрагмент 1
def process_numbers(numbers):
    result = []
    for n in numbers:
        if n > 0:
            result.append(n * 2)
    return result

# Фрагмент 2
def get_emails(users):
    emails = []
    for user in users:
        if user.get("email"):
            emails.append(user["email"])
    return emails

# Фрагмент 3
sorted_by_name = sorted(users, key=lambda u: u["name"])

# Фрагмент 4
multiply_by_5 = lambda x: x * 5
```

---

## Дополнительные материалы

### 📖 Книги

- **«Fluent Python»** (главы 5, 7) — Luciano Ramalho. First-class functions, декораторы и замыкания.
- **«Effective Python»** (советы 21–26) — Brett Slatkin. Функции, замыкания и декораторы.
- **«Functional Programming in Python»** — David Mertz. Функциональный стиль в Python.

### 🎥 Видео

- **«The Mental Game of Python»** — Raymond Hettinger (PyCon 2019). Стратегии декомпозиции кода.
- **«Python Lambdas and Other Functional Programming Features»** — David Beazley (PyCon 2015).

### 🔗 Ссылки

- [PEP 8: Programming Recommendations (lambda)](https://peps.python.org/pep-0008/#programming-recommendations)
- [PEP 3107 — Function Annotations](https://peps.python.org/pep-3107/)
- [Python 3: functools — Higher-order functions](https://docs.python.org/3/library/functools.html)
- [Python 3: itertools — Functions creating iterators](https://docs.python.org/3/library/itertools.html)

### 💡 Интересные факты

- `lambda` в Python была добавлена по запросу пользователей, привыкших к функциональным языкам (Lisp, ML). Гвидо ван Россум долго сопротивлялся и даже предлагал удалить lambda в Python 3 — но сообщество отстояло.
- `functools.partial` — это «частичное применение» функции: `double = partial(mul, 2)` создаёт функцию, которая умножает на 2.
- `operator.itemgetter` — альтернатива lambda для доступа к элементам: `sorted(users, key=itemgetter("age"))` вместо `key=lambda u: u["age"]` — и быстрее, и читаемее.
- В Python 3.9 появился синтаксис `lambda x: (x := x + 1)` с walrus operator `:=`, но использование lambda с присваиванием всё ещё считается плохим стилем.