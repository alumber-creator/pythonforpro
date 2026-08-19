---
title: "Распаковка, *args, **kwargs и продвинутая работа с аргументами"
order: 6
tags:
  - распаковка
  - args
  - kwargs
  - tuple
  - dict
prerequisites: "Функции, списки, словари"
objective: "Освоить все формы распаковки и гибкую работу с аргументами функций"
---

# Распаковка, `*args`, `**kwargs` и продвинутая работа с аргументами

## 🎯 Цель урока

Освоить все формы распаковки (tuple unpacking, extended unpacking, `*` и `**`), синтаксис `*args`/`**kwargs`, keyword-only и positional-only аргументы, идиоматическое слияние словарей и практическое применение walrus operator.

## 📋 Предпосылки

Вы уверенно работаете с функциями, списками, кортежами и словарями. Понимаете разницу между позиционными и именованными аргументами.

---

## Введение

Python обладает одним из самых гибких механизмов работы с аргументами функций среди мейнстрим-языков. Распаковка (unpacking) пронизывает весь язык: от присваивания переменных до передачи аргументов. В этом уроке мы пройдём от простого tuple unpacking до продвинутых техник вроде keyword-only аргументов и оператора walrus, которые делают Python-код одновременно лаконичным и выразительным.

---

## Основная часть

### 1. Tuple Unpacking — базовая распаковка

Распаковка кортежа — это присваивание элементов кортежа отдельным переменным:

```python
# Базовая распаковка
point = (10, 20)
x, y = point
print(x)  # 10
print(y)  # 20

# Работает с любыми итерируемыми объектами
a, b, c = [1, 2, 3]
first, second = "XY"
```

#### Обмен значений без временной переменной

Это одна из самых известных идиом Python:

```python
# ❌ С временной переменной (как в Java/C++)
temp = a
a = b
b = temp

# ✅ Идиоматичный Python
a, b = b, a
```

Справа создаётся кортеж `(b, a)`, который немедленно распаковывается в `a, b`. Элегантно и атомарно.

#### Распаковка в циклах

```python
# Распаковка при итерации по парам
pairs = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
for name, score in pairs:
    print(f"{name}: {score}")

# enumerate — классический пример
for i, item in enumerate(items):
    print(f"{i}: {item}")

# .items() у словаря
for key, value in config.items():
    print(f"{key} = {value}")
```

### 2. Extended Unpacking — расширенная распаковка (`*rest`)

С Python 3 можно использовать `*` для захвата «остатка»:

```python
# Первый и остальные
first, *rest = [1, 2, 3, 4, 5]
print(first)  # 1
print(rest)   # [2, 3, 4, 5]

# Последний и остальные
*rest, last = [1, 2, 3, 4, 5]
print(rest)  # [1, 2, 3, 4]
print(last)  # 5

# Первый, последний и всё между ними
first, *middle, last = [1, 2, 3, 4, 5]
print(first)   # 1
print(middle)  # [2, 3, 4]
print(last)    # 5
```

#### Практическое применение: разделение строки

```python
# Разделить строку на первую часть и остаток
line = "ERROR: Connection timeout in module X"
level, *message_parts = line.split(": ")
message = ": ".join(message_parts)
print(level)    # ERROR
print(message)  # Connection timeout in module X
```

#### Игнорирование ненужных значений

```python
# _ по соглашению означает «мне это не нужно»
name, _, score = ("Alice", "ignored_field", 85)

# *_ — игнорировать всё остальное
first, *_ = range(100)
print(first)  # 0
```

### 3. Оператор `*` для распаковки итераторов

`*` распаковывает любой итератор в позиционные аргументы:

```python
def add(a, b, c):
    return a + b + c


numbers = [1, 2, 3]
result = add(*numbers)  # add(1, 2, 3)
print(result)  # 6
```

#### Объединение коллекций

```python
# Объединение списков
list1 = [1, 2]
list2 = [3, 4]
combined = [*list1, *list2]  # [1, 2, 3, 4]

# Создание списка с дополнительными элементами
extended = [0, *list1, 99]  # [0, 1, 2, 99]

# Объединение множеств
set1 = {1, 2}
set2 = {2, 3}
union = {*set1, *set2}  # {1, 2, 3}

# Объединение кортежей
t1 = (1, 2)
t2 = (3, 4)
combined_tuple = (*t1, *t2)  # (1, 2, 3, 4)
```

### 4. Оператор `**` для распаковки словарей

`**` распаковывает словарь в именованные аргументы:

```python
def create_user(name, age, email):
    return f"{name} ({age}) <{email}>"


data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
result = create_user(**data)  # create_user(name="Alice", age=30, email="alice@example.com")
print(result)  # Alice (30) <alice@example.com>
```

#### Слияние словарей (Python 3.5+)

```python
defaults = {"host": "localhost", "port": 5432, "timeout": 30}
user_config = {"host": "db.example.com", "timeout": 60}

# Слияние: правый словарь переопределяет левый
config = {**defaults, **user_config}
# {'host': 'db.example.com', 'port': 5432, 'timeout': 60}
```

С Python 3.9 появился ещё более лаконичный оператор `|`:

```python
# Python 3.9+
config = defaults | user_config
# {'host': 'db.example.com', 'port': 5432, 'timeout': 60}
```

#### Создание словаря с дополнительными ключами

```python
base = {"x": 1, "y": 2}
extended = {**base, "z": 3, "label": "point"}
# {'x': 1, 'y': 2, 'z': 3, 'label': 'point'}
```

### 5. `*args` и `**kwargs` в определении функций

#### `*args` — переменное число позиционных аргументов

```python
def sum_all(*args):
    """Принимает любое количество позиционных аргументов."""
    return sum(args)


print(sum_all(1, 2, 3))        # 6
print(sum_all(10, 20, 30, 40))  # 100
```

Внутри функции `args` — это кортеж.

#### `**kwargs` — переменное число именованных аргументов

```python
def print_config(**kwargs):
    """Принимает любое количество именованных аргументов."""
    for key, value in kwargs.items():
        print(f"{key}: {value}")


print_config(host="localhost", port=5432, debug=True)
# host: localhost
# port: 5432
# debug: True
```

Внутри функции `kwargs` — это словарь.

#### `*args` и `**kwargs` вместе

```python
def log_event(event_type: str, *args, **kwargs):
    """Универсальная функция логирования."""
    print(f"[{event_type}]", end=" ")
    if args:
        print("args:", args, end=" ")
    if kwargs:
        print("kwargs:", kwargs, end=" ")
    print()


log_event("USER_LOGIN", "alice", ip="192.168.1.1", browser="Chrome")
# [USER_LOGIN] args: ('alice',) kwargs: {'ip': '192.168.1.1', 'browser': 'Chrome'}
```

#### Проброс аргументов (делегирование)

Одно из главных применений `*args`/`**kwargs` — проброс аргументов в обёрнутый вызов:

```python
def wrapper(*args, **kwargs):
    # Предобработка...
    result = original_function(*args, **kwargs)
    # Постобработка...
    return result
```

Это необходимый паттерн при написании декораторов (см. урок 5).

### 6. Keyword-only аргументы (после `*`)

С Python 3 можно требовать, чтобы определённые аргументы передавались ТОЛЬКО по имени:

```python
def configure(host, port, *, timeout=30, retries=3, ssl=True):
    """
    host и port — позиционные
    timeout, retries, ssl — ТОЛЬКО по имени (keyword-only)
    """
    ...


# ✅ Правильно
configure("localhost", 5432, timeout=60, retries=5)
configure("localhost", 5432, timeout=60, ssl=False)

# ❌ Ошибка — keyword-only аргументы переданы как позиционные
configure("localhost", 5432, 60, 5)
# TypeError: configure() takes 2 positional arguments but 4 were given
```

Это мощный инструмент для создания читаемых API. Аргументы, смысл которых неочевиден из позиции, должны быть keyword-only.

#### Когда `*args` уже есть

Если функция уже принимает `*args`, всё что после него — автоматически keyword-only:

```python
def process(*items, separator=", ", sort=False):
    ...
```

### 7. Positional-only аргументы (до `/`)

С Python 3.8 можно требовать, чтобы аргументы передавались ТОЛЬКО позиционно:

```python
def greet(name, /, greeting="Hello"):
    """name — только позиционно, greeting — по имени или позиционно."""
    return f"{greeting}, {name}!"


print(greet("Alice"))                      # Hello, Alice!
print(greet("Bob", greeting="Hi"))         # Hi, Bob!

# ❌ Ошибка
print(greet(name="Charlie"))
# TypeError: greet() got some positional-only arguments passed as keyword arguments
```

Positional-only аргументы полезны когда:
- Имя параметра не имеет значения (например, `len(obj)`, а не `len(object=obj)`)
- Параметр может конфликтовать с keyword-аргументами

### 8. Полная сигнатура функции

Комбинируя всё вместе, получаем полный синтаксис:

```python
def function(
    pos_only,           # Positional-only (до /)
    /,                  # Разделитель
    pos_or_kw,          # Позиционный или по имени
    *,                  # Разделитель: всё что после — keyword-only
    kw_only,            # Только по имени
    **kwargs,           # Прочие именованные
):
    pass
```

Реальный пример из стандартной библиотеки:

```python
# Сигнатура sorted()
def sorted(iterable, /, *, key=None, reverse=False):
    ...

# iterable — только позиционно (бессмысленно писать sorted(iterable=data))
# key и reverse — только по имени (их смысл неочевиден из позиции)
```

### 9. Walrus Operator `:=` (Python 3.8+)

Оператор присваивания в выражении (walrus operator) позволяет присвоить значение переменной прямо внутри выражения:

```python
# ❌ Без walrus: вычисляем len() дважды или создаём лишнюю переменную
data = get_data()
if len(data) > 0:
    print(f"Данные: {len(data)} элементов")

# ✅ С walrus: вычисляем один раз, используем в условии и в теле
if (n := len(data)) > 0:
    print(f"Данные: {n} элементов")
```

#### Типичные применения

**В циклах while:**

```python
# ❌ Без walrus: читаем дважды
line = file.readline()
while line:
    process(line)
    line = file.readline()

# ✅ С walrus: читаем один раз в условии
while line := file.readline():
    process(line)
```

**В comprehensions:**

```python
# Вычисляем дорогую функцию один раз
results = [result for x in data if (result := expensive_func(x)) > 0]
```

**В условиях:**

```python
# Сопоставление с регулярным выражением и извлечение групп
import re

pattern = re.compile(r"User: (\w+), Age: (\d+)")
if match := pattern.search(text):
    name = match.group(1)
    age = int(match.group(2))
    print(f"{name} is {age} years old")
```

#### Когда НЕ использовать walrus

```python
# ❌ Злоупотребление — присваивание, которое не используется в условии
if (x := f()):
    pass  # Используем x, но это неочевидно

# ✅ Лучше — явное присваивание
x = f()
if x:
    pass
```

### 10. Сравнение с другими языками

#### Java varargs

Java поддерживает переменное число аргументов через `...`:

```java
// Java — varargs (только один, только в конце)
public static int sum(int... numbers) {
    int total = 0;
    for (int n : numbers) total += n;
    return total;
}
```

```python
# Python — *args + **kwargs, оба могут сосуществовать
def sum_all(*args):
    return sum(args)

def configure(*args, **kwargs):
    ...
```

Python позволяет одновременно принимать и позиционные (`*args`), и именованные (`**kwargs`) переменные аргументы, что невозможно в Java.

#### C++ variadic templates

C++11 variadic templates — мощный, но синтаксически сложный механизм:

```cpp
// C++ — variadic templates (сложный синтаксис)
template<typename... Args>
auto sum(Args... args) {
    return (args + ...);  // Fold expression (C++17)
}
```

Python не требует шаблонов — динамическая типизация делает `*args` тривиально простым.

#### JavaScript spread/rest

JavaScript использует `...` для rest и spread:

```javascript
// JavaScript — rest параметры
function sum(...numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

// JavaScript — spread
const arr1 = [1, 2];
const arr2 = [3, 4];
const combined = [...arr1, ...arr2];  // [1, 2, 3, 4]

const obj1 = {a: 1, b: 2};
const obj2 = {b: 3, c: 4};
const merged = {...obj1, ...obj2};  // {a: 1, b: 3, c: 4}
```

Синтаксис близок к Python, но:
- Python разделяет `*` (позиционное) и `**` (именованное)
- JavaScript использует `...` для всего
- Python не имеет прямого аналога spread для объектов (только `**` для словарей)

---

## Практическое задание

### Задание 1: Универсальный логирующий декоратор

Напишите декоратор `log_calls`, который принимает функцию и логирует все её вызовы, корректно пробрасывая `*args` и `**kwargs`:

```python
import functools


def log_calls(func):
    """Логирует вызовы функции с полной информацией об аргументах."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Ваш код: логируйте имя функции, позиционные и именованные аргументы
        # Затем вызовите func(*args, **kwargs) и логируйте результат
        pass

    return wrapper


@log_calls
def calculate(a, b, *, operation="add"):
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    raise ValueError(f"Unknown operation: {operation}")


calculate(10, 20, operation="multiply")
# Должно вывести что-то вроде:
# Вызов calculate: args=(10, 20), kwargs={'operation': 'multiply'}
# Результат: 200
```

### Задание 2: Конфигурация с приоритетами

Напишите функцию `merge_configs(*configs)`, которая принимает произвольное число словарей и объединяет их: каждый следующий словарь переопределяет ключи предыдущего. Используйте идиоматический синтаксис распаковки.

```python
def merge_configs(*configs):
    """Объединяет конфигурации с нарастающим приоритетом."""
    # Ваш код
    pass


defaults = {"host": "localhost", "port": 5432, "debug": False}
file_config = {"host": "db.local", "timeout": 30}
env_config = {"port": 9999, "debug": True}

final = merge_configs(defaults, file_config, env_config)
print(final)
# {'host': 'db.local', 'port': 9999, 'debug': True, 'timeout': 30}
```

### Задание 3: Рефакторинг с walrus operator

Перепишите следующий код с использованием walrus operator, где это уместно:

```python
# A. Чтение файла
line = f.readline()
while line:
    line = line.strip()
    if line:
        process(line)
    line = f.readline()

# B. Проверка и использование
data = get_data()
if data is not None:
    n = len(data)
    if n > 0:
        print(f"Получено {n} записей")

# C. Регулярное выражение
pattern = re.compile(r"(\w+)=(\w+)")
match = pattern.search(text)
if match:
    key = match.group(1)
    value = match.group(2)
    print(f"{key} -> {value}")
```

---

## Дополнительные материалы

### Документация

- [PEP 3132 — Extended Iterable Unpacking](https://peps.python.org/pep-3132/)
- [PEP 3102 — Keyword-Only Arguments](https://peps.python.org/pep-3102/)
- [PEP 570 — Python Positional-Only Parameters](https://peps.python.org/pep-0570/)
- [PEP 572 — Assignment Expressions (`:=`)](https://peps.python.org/pep-0572/)
- [PEP 448 — Additional Unpacking Generalizations](https://peps.python.org/pep-0448/)
- [PEP 584 — Add Union Operators To dict (`|`)](https://peps.python.org/pep-0584/)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 5 (функции как объекты первого класса).
- **«Effective Python»**, Бретт Слаткин — совет 21: «Используйте keyword-only аргументы для ясности», совет 18: «Используйте *args и **kwargs».

### Статьи

- [Real Python: Python args and kwargs](https://realpython.com/python-kwargs-and-args/)
- [Real Python: Assignment Expressions (Walrus Operator)](https://realpython.com/python-walrus-operator/)

### Видео

- **«Python's Class Development Toolkit»**, Реймонд Хеттингер — о правильном использовании `*args`/`**kwargs`.
- **«PEP 572: The Walrus Operator»**, Дэвид Бизли — история и мотивация оператора `:=`.