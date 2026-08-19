---
title: "Comprehensions: списковые, словарные и множественные включения"
order: 2
tags:
  - comprehensions
  - list
  - dict
  - set
  - генераторы
prerequisites: "Базовый синтаксис Python, циклы for"
objective: "Научиться заменять циклы на comprehensions для более читаемого и быстрого кода"
---

# Comprehensions: списковые, словарные и множественные включения

## 🎯 Цель урока

Научиться использовать все виды comprehensions (list, dict, set) и генераторные выражения, понимать границы их применимости и писать код, который одновременно быстрее и читаемее.

## 📋 Предпосылки

Вы уверенно пишете циклы `for`, работаете со списками, словарями и множествами. Понимаете, что такое итерация и условные операторы.

---

## Введение

Comprehensions — одна из самых узнаваемых и любимых фич Python. Это синтаксический сахар, который позволяет создавать коллекции декларативно, в одну строку, вместо императивного цикла с мутацией. Идиоматический Python активно использует comprehensions вместо циклов `for` для операций фильтрации, трансформации и создания коллекций.

Но есть и обратная сторона: злоупотребление comprehensions порождает нечитаемый код. В этом уроке мы научимся балансировать между лаконичностью и читаемостью.

---

## Основная часть

### 1. List Comprehensions — списковые включения

Базовый синтаксис:

```python
[выражение for элемент in итератор if условие]
```

#### Простейший пример

**❌ Цикл с мутацией (неидиоматично):**

```python
squares = []
for x in range(10):
    squares.append(x ** 2)
```

**✅ List comprehension (идиоматично):**

```python
squares = [x ** 2 for x in range(10)]
```

Разница не только в компактности. List comprehension выполняется быстрее, потому что:
1. Цикл реализован на C внутри интерпретатора
2. `append` не ищется через словарь атрибутов на каждой итерации
3. Список сразу выделяется нужного размера (если возможно)

#### Фильтрация с условием

**❌ Цикл с условием:**

```python
evens = []
for x in range(20):
    if x % 2 == 0:
        evens.append(x)
```

**✅ Comprehension с фильтром:**

```python
evens = [x for x in range(20) if x % 2 == 0]
```

#### Трансформация + фильтрация

```python
# Квадраты чётных чисел
even_squares = [x ** 2 for x in range(20) if x % 2 == 0]
# [0, 4, 16, 36, 64, 100, 144, 196, 256, 324]
```

#### Условное выражение (if/else) в выражении

Обратите внимание: `if` в конце фильтрует элементы, а `if/else` в начале — это тернарный оператор для значения.

```python
# Заменить отрицательные на 0, оставить положительные
normalized = [x if x >= 0 else 0 for x in raw_values]

# Фильтрация + тернарный оператор вместе
processed = [x * 2 if x > 0 else x for x in values if x != 0]
```

Порядок: `выражение` -> `for` -> `if` (фильтр). Выражение может содержать `if/else`, но не `if` без `else`.

### 2. Dict Comprehensions — словарные включения

Синтаксис:

```python
{ключ: значение for элемент in итератор if условие}
```

#### Создание словаря из списка

**❌ Цикл:**

```python
squares = {}
for x in range(10):
    squares[x] = x ** 2
```

**✅ Dict comprehension:**

```python
squares = {x: x ** 2 for x in range(10)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81}
```

#### Инвертирование словаря

```python
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
# {1: 'a', 2: 'b', 3: 'c'}
```

#### Фильтрация словаря

```python
grades = {"Alice": 85, "Bob": 72, "Charlie": 90, "Diana": 65}

# Только те, кто сдал (>= 75)
passed = {name: grade for name, grade in grades.items() if grade >= 75}
# {'Alice': 85, 'Charlie': 90}
```

#### Трансформация ключей и значений

```python
# Привести имена к нижнему регистру и увеличить оценки на 5
adjusted = {name.lower(): grade + 5 for name, grade in grades.items()}
```

### 3. Set Comprehensions — множественные включения

Синтаксис:

```python
{выражение for элемент in итератор if условие}
```

Отличие от dict comprehension — нет двоеточия (только значение, не пара ключ-значение).

#### Создание множества

```python
# Все уникальные первые буквы
words = ["python", "philosophy", "programming", "code", "clear"]
initials = {w[0] for w in words}
# {'p', 'c'}
```

#### Удаление дубликатов с сохранением порядка

Set comprehension не сохраняет порядок. Если порядок важен, используйте `dict.fromkeys()`:

```python
items = [3, 1, 2, 1, 3, 2, 4]
unique_ordered = list(dict.fromkeys(items))
# [3, 1, 2, 4]
```

### 4. Nested Comprehensions — вложенные включения

Вложенные comprehensions читаются как вложенные циклы: внешний цикл первый, внутренний следующий.

#### Плоский список из вложенного

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# ❌ Вложенные циклы
flat = []
for row in matrix:
    for item in row:
        flat.append(item)

# ✅ Nested comprehension
flat = [item for row in matrix for item in row]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Порядок `for` в comprehension соответствует порядку вложенных циклов: сначала `for row in matrix`, потом `for item in row`.

#### Транспонирование матрицы

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = [[row[i] for row in matrix] for i in range(3)]
# [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
```

#### Фильтрация во вложенных comprehensions

```python
# Только чётные числа из матрицы
evens = [item for row in matrix for item in row if item % 2 == 0]
```

### 5. Generator Expressions — генераторные выражения

Генераторное выражение выглядит как list comprehension, но в круглых скобках. Оно не создаёт список в памяти — элементы вычисляются лениво.

```python
# List comprehension — создаёт список в памяти
squares_list = [x ** 2 for x in range(1_000_000)]  # 8+ MB в памяти

# Generator expression — не создаёт список
squares_gen = (x ** 2 for x in range(1_000_000))    # почти 0 памяти
```

Генераторное выражение можно передать в функцию, которая принимает итератор:

```python
# Сумма квадратов — без создания промежуточного списка
total = sum(x ** 2 for x in range(1_000_000))
```

Обратите внимание: когда генераторное выражение — единственный аргумент функции, двойные скобки не нужны. Это распространённый идиоматический паттерн.

```python
# Двойные скобки (работает, но некрасиво)
total = sum((x ** 2 for x in range(1_000_000)))

# Идиоматичный вариант
total = sum(x ** 2 for x in range(1_000_000))
```

### 6. Производительность: comprehension vs цикл

Рассмотрим бенчмарк:

```python
import timeit

# List comprehension
t1 = timeit.timeit("[x ** 2 for x in range(1000)]", number=100_000)

# Цикл for
t2 = timeit.timeit(
    """
result = []
for x in range(1000):
    result.append(x ** 2)
""",
    number=100_000,
)

print(f"Comprehension: {t1:.3f}s")
print(f"For loop:      {t2:.3f}s")
print(f"Speedup:       {t2 / t1:.1f}x")
```

Типичный результат: comprehension быстрее в 1.5-2 раза. Причина: `append` — это поиск атрибута через словарь + вызов метода, а comprehension строит список напрямую через C-API.

### 7. Когда НЕ использовать comprehensions

Comprehensions — мощный инструмент, но есть границы их применимости.

#### ⚠️ Правило: если comprehension не читается за один взгляд — используй цикл

**❌ НЕ делайте так:**

```python
# Антипаттерн: слишком сложный comprehension
result = [
    process(x)
    for x in data
    if validate(x) and x.status == "active"
    for tag in x.tags
    if tag.startswith("py")
]
```

**✅ Лучше — цикл с пояснениями:**

```python
result = []
for x in data:
    if not validate(x):
        continue
    if x.status != "active":
        continue
    processed = process(x)
    for tag in x.tags:
        if tag.startswith("py"):
            result.append(processed)
            break
```

#### ⚠️ Побочные эффекты

Comprehensions предназначены для создания коллекций. Не используйте их для побочных эффектов:

```python
# ❌ Антипаттерн: comprehension ради побочного эффекта
[print(x) for x in items]  # Создаёт список [None, None, ...] — бесполезный!

# ✅ Правильно: обычный цикл
for x in items:
    print(x)
```

#### ⚠️ Обработка исключений

Comprehension не может содержать `try/except`. Если нужна обработка ошибок — используйте цикл или вынесите логику в функцию:

```python
# ❌ Нельзя: comprehension с try/except
# safe = [int(x) for x in strings]  # Упадёт на нечисловой строке

# ✅ Выносим в функцию
def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return None


safe = [safe_int(s) for s in strings]
safe = [x for x in safe if x is not None]
```

### 8. Сравнение с другими языками

#### Java Streams

Java 8+ предлагает Stream API, который концептуально близок к comprehensions, но синтаксически тяжелее:

```java
// Java — многословно, цепочки методов
List<Integer> result = items.stream()
    .filter(x -> x % 2 == 0)
    .map(x -> x * x)
    .collect(Collectors.toList());
```

```python
# Python — лаконично, один компактный синтаксис
result = [x ** 2 for x in items if x % 2 == 0]
```

#### C++ std::transform

В C++ трансформация коллекции требует явного использования алгоритмов и итераторов:

```cpp
// C++ — многословно, нужны begin/end, back_inserter
std::vector<int> result;
std::transform(items.begin(), items.end(), std::back_inserter(result),
               [](int x) { return x * x; });
```

```python
# Python — тот же смысл, но в разы короче
result = [x ** 2 for x in items]
```

#### JavaScript map/filter

JavaScript использует цепочки методов, что ближе к Python, но синтаксически иначе:

```javascript
// JavaScript — цепочки методов
const result = items
    .filter(x => x % 2 === 0)
    .map(x => x ** 2);
```

```python
# Python — один синтаксис для всех операций
result = [x ** 2 for x in items if x % 2 == 0]
```

Python выигрывает в единообразии: один синтаксис для list, dict, set и generator expressions. В других языках это разные API.

### 9. Продвинутые приёмы

#### Использование walrus operator (:=) в comprehensions

С Python 3.8 можно использовать оператор присваивания внутри comprehension:

```python
# Без walrus: вычисляем дважды
results = [expensive_computation(x) for x in data if expensive_computation(x) > 0]

# С walrus: вычисляем один раз
results = [result for x in data if (result := expensive_computation(x)) > 0]
```

#### Множественные условия

```python
# Фильтрация по нескольким критериям
valid = [
    user
    for user in users
    if user.is_active
    and user.age >= 18
    and user.has_permission("read")
]
```

#### Создание вложенных структур

```python
# Словарь списков: группировка по первой букве
from collections import defaultdict

words = ["apple", "banana", "avocado", "blueberry", "cherry", "coconut"]
grouped = defaultdict(list)
[grouped[w[0]].append(w) for w in words]  # Не используйте так (побочный эффект!)

# Лучше — обычный цикл:
grouped = defaultdict(list)
for w in words:
    grouped[w[0]].append(w)

# Или через itertools.groupby
from itertools import groupby

words_sorted = sorted(words, key=lambda w: w[0])
grouped = {k: list(g) for k, g in groupby(words_sorted, key=lambda w: w[0])}
```

---

## Практическое задание

### Задание 1: Перепишите на comprehensions

Преобразуйте следующие фрагменты из циклов в comprehensions (или generator expressions, где уместно):

```python
# 1. Список длин строк
lengths = []
for word in ["hello", "world", "python", "code"]:
    lengths.append(len(word))

# 2. Словарь: слово -> длина, только для слов длиннее 3
word_lengths = {}
for word in ["hello", "a", "world", "py", "python", "x", "code"]:
    if len(word) > 3:
        word_lengths[word] = len(word)

# 3. Множество уникальных первых букв (только для слов длиннее 2)
initials = set()
for word in ["hello", "hi", "a", "world", "python"]:
    if len(word) > 2:
        initials.add(word[0])

# 4. Сумма квадратов чётных чисел
total = 0
for x in range(1, 101):
    if x % 2 == 0:
        total += x ** 2
```

### Задание 2: Найдите антипаттерны

Какие из следующих comprehensions написаны неправильно или неидиоматично? Объясните почему и предложите исправление.

```python
# A
[print(x) for x in range(10)]

# B
result = [x for x in range(100) if x % 2 == 0 if x % 3 == 0]

# C
data = [[x * y for y in range(10)] for x in range(10)]

# D
result = sum([x ** 2 for x in range(1_000_000)])

# E
result = [x for x in data if check(x) and transform(x) > 0]
```

### Задание 3: Задача на группировку

Дан список транзакций:

```python
transactions = [
    {"date": "2024-01-01", "amount": 100, "category": "food"},
    {"date": "2024-01-01", "amount": 200, "category": "transport"},
    {"date": "2024-01-02", "amount": 50, "category": "food"},
    {"date": "2024-01-02", "amount": 300, "category": "entertainment"},
    {"date": "2024-01-03", "amount": 150, "category": "food"},
]
```

Используя dict comprehension и другие идиоматичные средства, создайте:
1. Словарь `{дата: общая сумма за день}`
2. Словарь `{категория: [список сумм]}`
3. Множество категорий, где была хотя бы одна транзакция > 100

---

## Дополнительные материалы

### Документация

- [Python Tutorial: List Comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [PEP 202 — List Comprehensions](https://peps.python.org/pep-0202/)
- [PEP 274 — Dict Comprehensions](https://peps.python.org/pep-0274/)
- [PEP 289 — Generator Expressions](https://peps.python.org/pep-0289/)

### Книги

- **«Fluent Python»**, Лучано Рамальо — глава 2 (последовательности) и глава 14 (итераторы и генераторы).
- **«Effective Python»**, Бретт Слаткин — совет 7: «Используйте list comprehensions вместо map и filter», совет 8: «Избегайте более двух выражений в list comprehensions».

### Видео

- **«List Comprehensions and Generator Expressions»**, Реймонд Хеттингер — глубокое погружение в тему.
- **«Comprehensible Comprehensions»**, Трей Ханнер (PyCon 2017) — о читаемости и границах применимости.

### Статьи

- [Real Python: List Comprehensions in Python](https://realpython.com/list-comprehension-python/)
- [Python Patterns: Comprehensions](https://python-patterns.guide/)