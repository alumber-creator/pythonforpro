---
title: "Строки и форматирование: от f-строк до регулярных выражений"
order: 7
tags:
  - строки
  - f-strings
  - форматирование
  - regex
prerequisites: "Базовый синтаксис"
objective: "Освоить все способы работы со строками в Python, включая современные f-строки"
---

# Строки и форматирование: от f-строк до регулярных выражений

## 🎯 Цель урока

Освоить все инструменты работы со строками в Python: f-строки, методы строк, эффективную конкатенацию, регулярные выражения и обработку Unicode. Научиться выбирать правильный инструмент для каждой задачи.

## 📋 Предпосылки

Вы знаете базовый синтаксис Python и умеете создавать строки. Опыт работы с регулярными выражениями не требуется.

---

## Введение

Работа со строками — это 80% повседневного программирования: парсинг логов, форматирование вывода, валидация ввода, генерация отчётов, работа с API. Python предлагает богатейший арсенал строковых инструментов, и умение выбрать правильный — маркер опытного разработчика.

В этом уроке мы пройдём путь от базовых операций до продвинутых техник: f-строки с форматированием и отладкой, эффективная конкатенация, сырые строки для регулярных выражений и корректная работа с Unicode.

---

## Основная часть

### 1. f-строки — современный стандарт (Python 3.6+)

f-строки (formatted string literals) — самый читаемый и быстрый способ форматирования строк. Они заменяют все предыдущие способы (`%`-форматирование, `str.format()`).

```python
name = "Alice"
age = 30

# f-строка: выражения прямо в {}
greeting = f"Hello, {name}! You are {age} years old."
print(greeting)  # Hello, Alice! You are 30 years old.
```

#### Выражения внутри f-строк

Внутри `{}` можно использовать любые выражения Python:

```python
# Арифметика
price = 49.99
quantity = 3
print(f"Total: ${price * quantity:.2f}")  # Total: $149.97

# Вызовы функций и методов
text = "hello world"
print(f"Uppercase: {text.upper()}")        # Uppercase: HELLO WORLD
print(f"Words: {len(text.split())}")       # Words: 2

# Доступ к элементам коллекций
user = {"name": "Bob", "age": 25}
print(f"User: {user['name']}, age: {user['age']}")

# Тернарный оператор
status = "active"
print(f"Status: {'✓' if status == 'active' else '✗'}")

# Даже comprehensions (но осторожно с читаемостью!)
numbers = [1, 2, 3, 4, 5]
print(f"Squares: {[x**2 for x in numbers]}")
```

#### Форматирование чисел

```python
import math

pi = math.pi

# Количество знаков после запятой
print(f"Pi: {pi:.2f}")    # Pi: 3.14
print(f"Pi: {pi:.6f}")    # Pi: 3.141593

# Научная нотация
print(f"Avogadro: {6.022e23:.2e}")  # Avogadro: 6.02e+23

# Проценты
ratio = 0.8523
print(f"Progress: {ratio:.1%}")      # Progress: 85.2%

# Разделители тысяч
large = 1234567890
print(f"Budget: ${large:,}")         # Budget: $1,234,567,890

# Шестнадцатеричное, двоичное, восьмеричное
value = 255
print(f"Hex: {value:#x}")   # Hex: 0xff
print(f"Bin: {value:#b}")   # Bin: 0b11111111
print(f"Oct: {value:#o}")   # Oct: 0o377
```

#### Выравнивание и ширина поля

```python
# Выравнивание: < (влево), > (вправо), ^ (по центру)
print(f"|{'left':<10}|{'center':^10}|{'right':>10}|")
# |left      |  center  |     right|

# С заполнителем
print(f"|{'left':-<10}|{'center':*^10}|{'right':.>10}|")
# |left------|**center**|.....right|

# Табличный вывод
data = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
for name, score in data:
    print(f"{name:<15} {score:>5}")
# Alice              85
# Bob                92
# Charlie            78
```

#### Форматирование дат

```python
from datetime import datetime

now = datetime.now()

print(f"Date: {now:%Y-%m-%d}")              # Date: 2024-01-15
print(f"Time: {now:%H:%M:%S}")              # Time: 14:30:00
print(f"Full: {now:%Y-%m-%d %H:%M:%S}")     # Full: 2024-01-15 14:30:00
print(f"ISO: {now:%Y-%m-%dT%H:%M:%S}")      # ISO: 2024-01-15T14:30:00
```

#### Отладка с `=` (Python 3.8+)

Символ `=` после выражения выводит и выражение, и его значение:

```python
x = 42
y = 10
print(f"{x + y = }")        # x + y = 52
print(f"{x = }, {y = }")    # x = 42, y = 10
print(f"{x / y = :.2f}")   # x / y = 4.20

# Особенно полезно при отладке
name = "Alice"
items = [1, 2, 3]
print(f"{name = }, {len(items) = }")
# name = 'Alice', len(items) = 3
```

### 2. Сравнение способов форматирования

| Способ | Пример | Плюсы | Минусы |
|--------|--------|-------|--------|
| `%`-форматирование | `"Hello %s" % name` | Работает везде | Нечитаемо, ограничено |
| `str.format()` | `"Hello {}".format(name)` | Гибко, позиционные/именованные аргументы | Многословно |
| f-строки | `f"Hello {name}"` | Быстро, читаемо, выражения | Только Python 3.6+ |

**Правило: используйте f-строки всегда, когда это возможно.**
Если шаблон хранится отдельно (в файле, в БД) — используйте `str.format()`.

### 3. Методы строк — полный арсенал

Python strings — это богатый API из 40+ методов. Вот самые важные, сгруппированные по назначению:

#### Проверка содержимого

```python
s = "Hello123"

# Проверки (возвращают bool)
s.isalpha()      # False — только буквы
s.isalnum()      # True  — буквы и цифры
s.isdigit()      # False — только цифры
s.islower()      # False — все ли в нижнем регистре
s.isupper()      # False — все ли в верхнем
s.isspace()      # False — только пробельные символы
s.startswith("He")  # True
s.endswith("123")   # True
```

#### Поиск и замена

```python
text = "Python is great. Python is fun."

# Поиск
text.find("Python")       # 0 — индекс первого вхождения
text.find("Java")         # -1 — не найдено
text.rfind("Python")      # 18 — поиск справа
text.count("Python")      # 2 — количество вхождений
"Python" in text          # True — самый идиоматичный способ проверить наличие

# Замена
text.replace("Python", "Kotlin")    # Заменяет все вхождения
text.replace("Python", "Kotlin", 1) # Заменяет только первое
```

#### Трансформация регистра

```python
s = "hello WORLD"

s.upper()       # "HELLO WORLD"
s.lower()       # "hello world"
s.capitalize()  # "Hello world" — первый символ заглавный, остальные строчные
s.title()       # "Hello World" — каждое слово с заглавной
s.swapcase()    # "HELLO world" — инвертирует регистр
```

#### Удаление пробельных символов

```python
s = "  hello  \n"

s.strip()       # "hello" — удаляет с обеих сторон
s.lstrip()      # "hello  \n" — удаляет слева
s.rstrip()      # "  hello" — удаляет справа

# Можно указать свои символы
url = "https://example.com/"
url.strip("/")  # "https://example.com"
```

#### Разделение и объединение

```python
# split — разделение строки
"a,b,c".split(",")           # ['a', 'b', 'c']
"one two three".split()      # ['one', 'two', 'three'] — по пробелам
"a,b,c".split(",", maxsplit=1)  # ['a', 'b,c'] — только 1 разделение

# rsplit — разделение справа
"file.tar.gz".rsplit(".", maxsplit=1)  # ['file.tar', 'gz']

# splitlines — разделение по строкам
"line1\nline2\r\nline3".splitlines()     # ['line1', 'line2', 'line3']
"line1\nline2\r\nline3".splitlines(keepends=True)  # С символами переноса

# join — объединение (идиоматичный способ!)
items = ["apple", "banana", "cherry"]
", ".join(items)  # "apple, banana, cherry"
"".join(items)    # "applebananacherry"
```

### 4. Конкатенация строк: join() vs `+` vs `+=`

Это одна из самых частых ошибок новичков:

**❌ `+` в цикле (квадратичная сложность):**

```python
# Каждый + создаёт новую строку — O(n²)!
result = ""
for item in large_list:
    result += item + ", "
```

**✅ `join()` (линейная сложность):**

```python
# join() выделяет память один раз — O(n)
result = ", ".join(large_list)
```

#### Почему `+` в цикле — это плохо

Строки в Python неизменяемы (immutable). Каждый `+=` создаёт новую строку, копируя всё предыдущее содержимое. Для списка из 100 000 элементов это ~5 миллиардов операций копирования символов.

```python
# Демонстрация через timeit
import timeit

# join — быстро
t1 = timeit.timeit(
    lambda: "".join(str(i) for i in range(10000)),
    number=1000,
)

# += в цикле — медленно
def concat_loop():
    result = ""
    for i in range(10000):
        result += str(i)
    return result


t2 = timeit.timeit(concat_loop, number=1000)

print(f"join: {t1:.3f}s")
print(f"+=:   {t2:.3f}s")
print(f"join быстрее в {t2 / t1:.1f}x")
```

#### Когда `+` уместен

`+` для конкатенации нескольких литералов — ок:

```python
# OK — константное количество строк
message = "Hello, " + name + "! Welcome to " + site + "."

# Ho f-строки всё равно лучше
message = f"Hello, {name}! Welcome to {site}."
```

### 5. Raw Strings (сырые строки)

Сырые строки (`r"..."`) не интерпретируют escape-последовательности:

```python
# Обычная строка: \\ — это экранированный бэкслеш
path = "C:\\Users\\Admin\\Desktop"

# Сырая строка: бэкслеши — это просто бэкслеши
path = r"C:\Users\Admin\Desktop"

# Регулярные выражения без сырых строк — ад
import re

# ❌ Без сырой строки: двойное экранирование
pattern = re.compile("\\d+\\.\\d+")

# ✅ С сырой строкой: пишем сам regex, а не escape-квест
pattern = re.compile(r"\d+\.\d+")
```

### 6. Регулярные выражения с `re`

Регулярные выражения в Python — это модуль `re`. Вот минимальный, но полный набор для повседневной работы:

#### Поиск и сопоставление

```python
import re

text = "Contact: alice@example.com, bob@company.org"

# search — первое совпадение
match = re.search(r"(\w+)@(\w+\.\w+)", text)
if match:
    print(match.group(0))  # alice@example.com — всё совпадение
    print(match.group(1))  # alice — первая группа
    print(match.group(2))  # example.com — вторая группа

# findall — все совпадения
emails = re.findall(r"\w+@\w+\.\w+", text)
print(emails)  # ['alice@example.com', 'bob@company.org']

# finditer — итератор по совпадениям (ленивый)
for match in re.finditer(r"\w+@\w+\.\w+", text):
    print(match.group())
```

#### Замена

```python
# sub — замена по шаблону
text = "Order #12345, Order #67890"
masked = re.sub(r"#(\d{5})", r"#***\1", text)
print(masked)  # Order #***12345, Order #***67890

# subn — замена + количество замен
result, count = re.subn(r"#\d{5}", "#XXXXX", text)
print(result)  # Order #XXXXX, Order #XXXXX
print(count)   # 2
```

#### Компиляция и флаги

```python
# Компиляция для многократного использования
pattern = re.compile(
    r"^(?P<name>\w+)\s+(?P<age>\d+)$",
    re.IGNORECASE | re.MULTILINE,
)

text = "Alice 30\nBob 25\nCharlie 35"
for match in pattern.finditer(text):
    print(f"{match.group('name')} is {match.group('age')}")
# Alice is 30
# Bob is 25
# Charlie is 35
```

#### Основные спецсимволы

| Символ | Значение | Пример |
|--------|----------|--------|
| `.` | Любой символ кроме `\n` | `a.b` → `"acb"`, `"a b"` |
| `\d` | Цифра | `\d+` → `"123"` |
| `\w` | Буква, цифра, `_` | `\w+` → `"hello_123"` |
| `\s` | Пробельный символ | `\s+` → `"  \t\n"` |
| `*` | 0 или более | `a*` → `""`, `"aaa"` |
| `+` | 1 или более | `a+` → `"a"`, `"aaa"` |
| `?` | 0 или 1 | `a?` → `""`, `"a"` |
| `{n}` | Ровно n раз | `\d{3}` → `"123"` |
| `{n,m}` | От n до m раз | `\d{2,4}` → `"12"`, `"1234"` |
| `^` | Начало строки | `^Hello` |
| `$` | Конец строки | `world$` |
| `[]` | Набор символов | `[aeiou]` |
| `[^]` | Кроме символов | `[^0-9]` |
| `()` | Группа | `(ab)+` → `"abab"` |
| `|` | ИЛИ | `cat|dog` |

### 7. Unicode в Python 3

Python 3 хранит строки как Unicode. Это решает большинство проблем, но есть нюансы:

```python
# Python 3: строки — это Unicode
s = "Привет, мир! 🐍"
print(len(s))  # 14 (4 символа теряются из-за эмодзи)
print(s[0])    # П

# Эмодзи — это суррогатные пары
emoji = "🐍"
print(len(emoji))  # 1 (Python 3.12+ корректно считает графемные кластеры)

# Кодирование/декодирование
encoded = "Привет".encode("utf-8")
print(encoded)  # b'\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82'
decoded = encoded.decode("utf-8")
print(decoded)  # Привет
```

#### Правило работы с Unicode

1. **Внутри программы — всегда `str` (Unicode).**
2. **На границах системы (файлы, сеть, БД) — кодируйте/декодируйте явно.**
3. **Всегда указывайте `encoding="utf-8"` при открытии файлов.**

```python
# ❌ Опасно — полагаемся на системную кодировку
with open("data.txt") as f:
    content = f.read()

# ✅ Явно указываем UTF-8
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
```

### 8. Сравнение с другими языками

#### Java String.format

Java использует `String.format()` с printf-стилем:

```java
// Java — printf-стиль, типы указываются явно
String name = "Alice";
int age = 30;
String result = String.format("Hello, %s! You are %d years old.", name, age);
```

```python
# Python f-string — типы выводятся автоматически, компактнее
name = "Alice"
age = 30
result = f"Hello, {name}! You are {age} years old."
```

#### C++ std::format (C++20)

C++20 добавил `std::format`, синтаксически похожий на Python:

```cpp
// C++20 — похоже на Python f-строки
auto result = std::format("Hello, {}! You are {} years old.", name, age);
```

Но Python f-строки всё ещё лаконичнее за счёт отсутствия необходимости в `std::format()` и прямого доступа к переменным без передачи аргументов.

#### JavaScript template literals

JavaScript template literals (backtick strings) — это ближайший аналог f-строк:

```javascript
// JavaScript — template literals
const name = "Alice";
const age = 30;
const result = `Hello, ${name}! You are ${age} years old.`;
```

Синтаксис идентичен по духу, но Python f-строки имеют преимущество:
- Встроенные спецификаторы форматирования (`:.2f`, `:>10`, `:%Y-%m-%d`)
- Отладочный `=` (Python 3.8+)
- Более строгая обработка типов

---

## Практическое задание

### Задание 1: Форматирование отчёта

Напишите функцию `format_report(data)`, которая принимает список словарей с данными о продажах и возвращает форматированную строку-таблицу:

```python
def format_report(data: list[dict]) -> str:
    """Форматирует данные о продажах в таблицу."""
    # Ваш код
    pass


# Входные данные
sales = [
    {"product": "Widget A", "quantity": 150, "price": 9.99},
    {"product": "Gadget B", "quantity": 42, "price": 24.50},
    {"product": "Doohickey C", "quantity": 1000, "price": 1.25},
]

# Ожидаемый вывод:
# Product          Qty       Price     Total
# Widget A          150     $9.99  $1,498.50
# Gadget B           42    $24.50  $1,029.00
# Doohickey C      1000     $1.25  $1,250.00
# ─────────────────────────────────────────
# TOTAL:                                 $3,777.50

print(format_report(sales))
```

### Задание 2: Парсинг логов с регулярными выражениями

Напишите функцию `parse_logs(text)`, которая извлекает из логов информацию об ошибках:

```python
import re


def parse_logs(text: str) -> list[dict]:
    """
    Извлекает ошибки из логов.

    Формат строки лога:
    [2024-01-15 14:30:00] ERROR: Connection timeout (module=network, retry=3)

    Функция должна вернуть список словарей с ключами:
    datetime, level, message, module, retry
    """
    # Ваш код
    pass


logs = """
[2024-01-15 14:30:00] INFO: Server started (module=main)
[2024-01-15 14:30:05] ERROR: Connection timeout (module=network, retry=3)
[2024-01-15 14:31:00] WARNING: High memory usage (module=memory, usage=85%)
[2024-01-15 14:32:00] ERROR: Permission denied (module=auth, user=alice)
"""

errors = parse_logs(logs)
for error in errors:
    print(error)
# {'datetime': '2024-01-15 14:30:05', 'level': 'ERROR',
#  'message': 'Connection timeout', 'module': 'network', 'retry': '3'}
# ...
```

### Задание 3: Конкатенация на скорость

Проведите бенчмарк: сравните 3 способа построения длинной строки (100 000 элементов) и объясните результаты:

1. `+=` в цикле
2. `"".join()` с генератором
3. `"".join()` со списковым comprehension

```python
import timeit


def concat_plus_equals(n):
    """Строка через +=."""
    # Ваш код
    pass


def concat_join_generator(n):
    """Строка через join() + генератор."""
    # Ваш код
    pass


def concat_join_list(n):
    """Строка через join() + list comprehension."""
    # Ваш код
    pass


# Ваш бенчмарк здесь
```

---

## Дополнительные материалы

### Документация

- [PEP 498 — Literal String Interpolation (f-strings)](https://peps.python.org/pep-0498/)
- [PEP 701 — Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)
- [Python String Methods](https://docs.python.org/3/library/stdtypes.html#string-methods)
- [re module documentation](https://docs.python.org/3/library/re.html)
- [Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 4 (текст и байты).
- **«Effective Python»**, Бретт Слаткин — совет 9: «Избегайте использования %-форматирования», совет 10: «Используйте f-строки».

### Статьи

- [Real Python: Python f-strings](https://realpython.com/python-f-strings/)
- [Real Python: Regular Expressions in Python](https://realpython.com/regex-python/)
- [Python String Formatting Best Practices](https://realpython.com/python-string-formatting/)

### Инструменты

- [regex101.com](https://regex101.com/) — онлайн-песочница для отладки регулярных выражений (выберите Python flavour).
- [Pythex](https://pythex.org/) — ещё один отладчик regex с подсветкой Python-синтаксиса.