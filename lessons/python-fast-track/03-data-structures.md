---
title: "Структуры данных: списки, кортежи, словари, множества"
order: 3
tags: ["list", "tuple", "dict", "set", "структуры-данных"]
prerequisites: "Урок 2"
objective: "Уверенно использовать все встроенные структуры данных Python"
---

## Введение

Встроенные структуры данных Python — одна из главных причин, почему язык так выразителен. Если в Java вам нужно импортировать `java.util.ArrayList`, `java.util.HashMap`, `java.util.HashSet`, и для каждой операции писать многословный код, то в Python списки, словари и множества — часть синтаксиса языка.

В этом уроке мы разберём четыре основные структуры: **списки** (list), **кортежи** (tuple), **словари** (dict) и **множества** (set). Вы узнаете, когда использовать каждую, как работает slicing и как Python делает операции с коллекциями лаконичными.

### 🎯 Цель урока

Уверенно использовать все встроенные структуры данных Python. После этого урока вы сможете выбрать правильную структуру для задачи, написать эффективный код с comprehensions и объяснить разницу между list и tuple.

### 📋 Предпосылки

Вы освоили базовый синтаксис Python (Урок 2): переменные, типы, условия, циклы и функции.

---

## Основная часть

### 1. Списки (list): изменяемые последовательности

Список (`list`) — это **упорядоченная, изменяемая** коллекция элементов. Аналог `ArrayList` в Java, `std::vector` в C++, `Array` в JavaScript.

```python
# Создание списка
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, None]  # Можно смешивать типы (но обычно не нужно)

# Доступ к элементам
print(fruits[0])      # apple (первый элемент)
print(fruits[-1])     # cherry (последний элемент)
print(fruits[1])      # banana

# Изменение элементов
fruits[0] = "apricot"
print(fruits)         # ["apricot", "banana", "cherry"]

# Добавление и удаление
fruits.append("date")           # В конец
fruits.insert(1, "blueberry")   # По индексу
fruits.extend(["elderberry", "fig"])  # Слияние списков
last = fruits.pop()             # Удалить и вернуть последний
fruits.remove("banana")         # Удалить по значению (первое вхождение)
del fruits[0]                   # Удалить по индексу
```

**Сравнение с Java:**

```python
# Python: список — часть языка
fruits = ["apple", "banana", "cherry"]
fruits.append("date")
print(fruits[0])
```

```java
// Java: список — библиотечный тип
import java.util.ArrayList;
import java.util.List;

List<String> fruits = new ArrayList<>(List.of("apple", "banana", "cherry"));
fruits.add("date");
System.out.println(fruits.get(0));
```

| Операция | Python | Java |
|----------|--------|------|
| Создание | `["a", "b"]` | `new ArrayList<>(List.of("a", "b"))` |
| Добавление | `items.append(x)` | `items.add(x)` |
| Доступ | `items[i]` | `items.get(i)` |
| Длина | `len(items)` | `items.size()` |
| Срез | `items[1:3]` | `items.subList(1, 3)` |

### 2. Срезы (slicing): мощнейший инструмент

Срезы — одна из наиболее выразительных возможностей Python. Они работают для всех последовательностей: списков, строк, кортежей.

```python
items = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Синтаксис: items[start:stop:step]
# start — включительно, stop — НЕ включительно

print(items[2:5])      # [2, 3, 4]        (с индекса 2 до 5, не включая 5)
print(items[:5])       # [0, 1, 2, 3, 4]  (от начала до 5)
print(items[5:])       # [5, 6, 7, 8, 9]  (с 5 до конца)
print(items[:])        # [0, 1, ..., 9]    (копия списка!)
print(items[::2])      # [0, 2, 4, 6, 8]  (каждый второй)
print(items[::-1])     # [9, 8, 7, ..., 0] (реверс!)
print(items[-3:])      # [7, 8, 9]         (последние 3 элемента)
print(items[-5:-2])    # [5, 6, 7]         (отрицательные индексы)
```

**Отрицательные индексы:**

```
Индексы:      0    1    2    3    4    5    6    7    8    9
Значения:    [0,   1,   2,   3,   4,   5,   6,   7,   8,   9]
Отрицательные: -10  -9   -8   -7   -6   -5   -4   -3   -2   -1
```

**Сравнение: реверс списка**

```python
# Python
reversed_items = items[::-1]
```

```java
// Java
import java.util.Collections;
import java.util.ArrayList;
// ...
ArrayList<Integer> reversed = new ArrayList<>(items);
Collections.reverse(reversed);
```

```cpp
// C++
#include <algorithm>
std::reverse(items.begin(), items.end());
```

```javascript
// JavaScript
const reversed = items.slice().reverse();
```

### 3. List comprehensions: генерация списков

List comprehension — это идиоматичный способ создания нового списка путём преобразования существующей последовательности. Это то, что заменяет `map + filter` в Python.

```python
# Базовый синтаксис: [expression for item in iterable if condition]

# Квадраты чисел от 0 до 9
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Только чётные квадраты
even_squares = [x**2 for x in range(10) if x % 2 == 0]
print(even_squares)  # [0, 4, 16, 36, 64]

# Вложенные циклы (читается слева направо, как обычные циклы)
pairs = [(x, y) for x in range(3) for y in range(2)]
print(pairs)  # [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

# Преобразование элементов
names = ["alice", "bob", "charlie"]
capitalized = [name.title() for name in names]
print(capitalized)  # ["Alice", "Bob", "Charlie"]

# Фильтрация
numbers = [1, -2, 3, -4, 5, -6]
positives = [n for n in numbers if n > 0]
print(positives)  # [1, 3, 5]
```

**Сравнение: list comprehension vs традиционный цикл vs map/filter**

```python
# Задача: получить квадраты положительных чисел из списка

numbers = [1, -2, 3, -4, 5, -6]

# ❌ Анти-паттерн: традиционный цикл
result = []
for n in numbers:
    if n > 0:
        result.append(n**2)

# ❌ Сложно читать: map + filter + lambda
result = list(map(lambda n: n**2, filter(lambda n: n > 0, numbers)))

# ✅ Идиоматично: list comprehension
result = [n**2 for n in numbers if n > 0]
```

**Сравнение с Java Streams:**

```java
// Java 8+ Stream API
List<Integer> result = numbers.stream()
    .filter(n -> n > 0)
    .map(n -> n * n)
    .collect(Collectors.toList());
```

```python
# Python list comprehension
result = [n**2 for n in numbers if n > 0]
```

Python-версия: одна строка, читается слева направо, не требует импортов и `Collectors`.

### 4. Кортежи (tuple): неизменяемые последовательности

Кортеж (`tuple`) — это **упорядоченная, неизменяемая** последовательность. После создания кортеж нельзя изменить.

```python
# Создание кортежа
point = (3, 4)
rgb = (255, 128, 0)
single = (42,)      # Запятая обязательна для кортежа из одного элемента!
not_a_tuple = (42)  # Это просто число 42 в скобках!

# Без скобок (packing)
coordinates = 10, 20, 30
print(type(coordinates))  # <class 'tuple'>

# Распаковка (unpacking)
x, y, z = coordinates
print(x, y, z)  # 10 20 30

# Обмен значений без временной переменной
a, b = 1, 2
a, b = b, a
print(a, b)  # 2 1
```

**List vs Tuple: когда что использовать?**

| Критерий | list | tuple |
|----------|------|-------|
| Изменяемость | ✅ Изменяемый | ❌ Неизменяемый |
| Методы | `append`, `extend`, `pop`, `remove`, `insert`, `sort`, ... | `count`, `index` (только чтение) |
| Производительность | Медленнее (требует аллокации для роста) | Быстрее (фиксированный размер) |
| Память | Больше (overhead под рост) | Меньше |
| Хешируемость | ❌ Не хешируемый | ✅ Хешируемый (если все элементы хешируемы) |
| Использование как ключ dict | ❌ Нельзя | ✅ Можно |
| Семантика | «Коллекция однотипных элементов» | «Запись / структура с полями» |

**Идиоматическое использование:**

```python
# ✅ tuple: запись с фиксированной структурой
person = ("Alice", 30, "alice@example.com")  # Имя, возраст, email
name, age, email = person  # Распаковка — читаемо

# ✅ tuple: возврат нескольких значений из функции
def min_max(items):
    return min(items), max(items)  # Возвращает tuple

lowest, highest = min_max([3, 1, 4, 1, 5, 9])

# ✅ list: коллекция однотипных элементов
temperatures = [36.6, 37.0, 36.8, 37.2]  # Может пополняться

# ✅ tuple: ключ словаря
locations = {
    (55.7558, 37.6173): "Moscow",
    (40.7128, -74.0060): "New York",
}
```

**Сравнение: обмен значений**

```python
# Python: одна строка, без временной переменной
a, b = b, a
```

```java
// Java: нужна временная переменная
int temp = a;
a = b;
b = temp;
```

```cpp
// C++: через std::swap или временную переменную
std::swap(a, b);
```

```javascript
// JavaScript: деструктуризация (ES6+)
[a, b] = [b, a];
```

### 5. Словари (dict): hash maps

Словарь (`dict`) — это **неупорядоченная** (до Python 3.6) / **упорядоченная по вставке** (Python 3.7+) коллекция пар **ключ-значение**. Аналог `HashMap` в Java, `std::unordered_map` в C++, `Object` / `Map` в JavaScript.

```python
# Создание словаря
user = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
}

# Доступ к элементам
print(user["name"])         # Alice
print(user.get("phone"))    # None (без KeyError!)
print(user.get("phone", "N/A"))  # N/A (значение по умолчанию)

# Добавление и обновление
user["phone"] = "+1234567890"
user["age"] = 31            # Обновление существующего ключа
user.update({"city": "NYC", "zip": "10001"})  # Массовое обновление

# Удаление
email = user.pop("email")   # Удалить и вернуть значение
del user["zip"]             # Удалить ключ

# Перебор словаря
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(f"{key}: {value}")

for key in user.keys():
    print(key)

for value in user.values():
    print(value)
```

**Сравнение с Java:**

```python
# Python: словарь — часть синтаксиса
ages = {"Alice": 30, "Bob": 25, "Charlie": 35}
print(ages["Alice"])
ages["David"] = 40
```

```java
// Java: HashMap — библиотечный тип
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> ages = new HashMap<>();
ages.put("Alice", 30);
ages.put("Bob", 25);
ages.put("Charlie", 35);
System.out.println(ages.get("Alice"));
ages.put("David", 40);
```

| Операция | Python | Java |
|----------|--------|------|
| Создание | `{"a": 1, "b": 2}` | `new HashMap<>(Map.of("a", 1, "b", 2))` |
| Доступ | `d["key"]` | `d.get("key")` |
| Безопасный доступ | `d.get("key", default)` | `d.getOrDefault("key", default)` |
| Проверка ключа | `"key" in d` | `d.containsKey("key")` |
| Перебор | `for k, v in d.items():` | `for (var e : d.entrySet())` |

#### Dict comprehensions

```python
# Создание словаря через comprehension
squares = {x: x**2 for x in range(5)}
print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Фильтрация
even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
print(even_squares)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}

# Инвертирование словаря (ключи ↔ значения)
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(inverted)  # {1: "a", 2: "b", 3: "c"}
```

#### defaultdict и Counter (из модуля collections)

```python
from collections import defaultdict, Counter

# defaultdict: словарь со значением по умолчанию
# Без defaultdict:
word_count = {}
for word in ["a", "b", "a", "c", "b", "a"]:
    if word not in word_count:
        word_count[word] = 0
    word_count[word] += 1

# С defaultdict:
word_count = defaultdict(int)
for word in ["a", "b", "a", "c", "b", "a"]:
    word_count[word] += 1  # Нет проверки на существование!

# Counter: счётчик элементов
word_count = Counter(["a", "b", "a", "c", "b", "a"])
print(word_count)         # Counter({'a': 3, 'b': 2, 'c': 1})
print(word_count.most_common(2))  # [('a', 3), ('b', 2)]
```

### 6. Множества (set): уникальные неупорядоченные коллекции

Множество (`set`) — это **неупорядоченная** коллекция **уникальных** элементов. Аналог `HashSet` в Java, `std::unordered_set` в C++, `Set` в JavaScript.

```python
# Создание множества
fruits = {"apple", "banana", "cherry"}
numbers = set([1, 2, 2, 3, 3, 3, 4])  # Дубликаты удаляются
print(numbers)  # {1, 2, 3, 4}

empty = set()  # НЕ {} — это пустой словарь!

# Операции над множествами
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)   # {1, 2, 3, 4, 5, 6} — объединение
print(a & b)   # {3, 4}               — пересечение
print(a - b)   # {1, 2}               — разность
print(a ^ b)   # {1, 2, 5, 6}         — симметрическая разность

# Проверки
print(3 in a)          # True
print(a.isdisjoint(b)) # False (есть общие элементы)
print(a.issubset({1, 2, 3, 4, 5}))  # True
```

**Идиоматическое использование:**

```python
# Удаление дубликатов из списка
items = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(items))  # [1, 2, 3, 4] (порядок не гарантирован!)

# Сохранение порядка при удалении дубликатов (Python 3.7+)
unique_ordered = list(dict.fromkeys(items))  # [1, 2, 3, 4]

# Проверка принадлежности
allowed = {"admin", "manager", "editor"}
if user_role in allowed:
    grant_access()

# Эффективная проверка дубликатов
def has_duplicates(items):
    return len(items) != len(set(items))
```

**Сравнение: удаление дубликатов из списка**

```python
# Python
unique = list(set(items))
```

```java
// Java
List<String> unique = new ArrayList<>(new HashSet<>(items));
```

```cpp
// C++
std::unordered_set<int> s(items.begin(), items.end());
std::vector<int> unique(s.begin(), s.end());
```

```javascript
// JavaScript
const unique = [...new Set(items)];
```

### 7. Сравнительная таблица всех структур

| Характеристика | list | tuple | dict | set |
|---------------|------|-------|------|-----|
| Синтаксис | `[]` | `()` | `{}` | `{*}` или `set()` |
| Изменяемость | ✅ Да | ❌ Нет | ✅ Да (ключи нет) | ✅ Да |
| Упорядоченность | ✅ По индексу | ✅ По индексу | ✅ С 3.7 (по вставке) | ❌ Нет |
| Дубликаты | ✅ Да | ✅ Да | ❌ Ключи уникальны | ❌ Нет |
| Индексация | ✅ `items[i]` | ✅ `t[i]` | ❌ Только по ключу | ❌ Нет |
| Срезы | ✅ Да | ✅ Да | ❌ Нет | ❌ Нет |
| Хешируемость | ❌ Нет | ✅ Да | ❌ Нет | ❌ Нет (но frozenset — да) |
| Поиск по значению | O(n) | O(n) | O(1) по ключу | O(1) |
| Типичное использование | Коллекция элементов | Запись/структура | Lookup-таблица | Уникальные элементы |

### 8. Анти-паттерны и идиоматический код

#### Анти-паттерн 1: Проверка на пустоту

```python
# ❌ Плохо: явная проверка длины
if len(items) == 0:
    print("Пусто")
if len(items) != 0:
    print("Не пусто")

# ✅ Идиоматично: используйте truthiness
if not items:
    print("Пусто")
if items:
    print("Не пусто")
```

#### Анти-паттерн 2: Проверка вхождения

```python
# ❌ Плохо: метод .index() с обработкой исключения
try:
    idx = items.index(target)
    print(f"Найден на позиции {idx}")
except ValueError:
    print("Не найден")

# ✅ Идиоматично: оператор in
if target in items:
    idx = items.index(target)
    print(f"Найден на позиции {idx}")
else:
    print("Не найден")
```

#### Анти-паттерн 3: Ручное построение списка

```python
# ❌ Плохо: цикл с append
result = []
for item in items:
    if condition(item):
        result.append(transform(item))

# ✅ Идиоматично: list comprehension
result = [transform(item) for item in items if condition(item)]
```

#### Анти-паттерн 4: Словарь с проверками

```python
# ❌ Плохо: проверка существования ключа
if key in d:
    d[key] += 1
else:
    d[key] = 1

# ✅ Идиоматично: defaultdict или get
from collections import defaultdict
d = defaultdict(int)
d[key] += 1

# Или
d[key] = d.get(key, 0) + 1
```

### 9. Производительность и выбор структуры

| Операция | list | tuple | dict | set |
|----------|------|-------|------|-----|
| Вставка | O(1)* в конец | N/A | O(1) | O(1) |
| Поиск по значению | O(n) | O(n) | N/A | N/A |
| Поиск по ключу | N/A | N/A | O(1) | O(1) |
| Проверка `in` | O(n) | O(n) | O(1) | O(1) |
| Удаление | O(n) | N/A | O(1) | O(1) |
| Доступ по индексу | O(1) | O(1) | N/A | N/A |

*Амортизированное O(1); вставка в начало — O(n).

**Правило выбора:**
- Нужна упорядоченная коллекция с частым изменением → `list`
- Нужна неизменяемая запись или ключ словаря → `tuple`
- Нужен быстрый lookup по ключу → `dict`
- Нужна коллекция уникальных элементов или быстрый `in` → `set`

---

## Практическое задание

### Задание 1: Анализ текста

Напишите функцию `analyze_text(text)`:

1. Принимает строку, разбивает на слова
2. Возвращает словарь с ключами:
   - `word_count` — общее количество слов
   - `unique_words` — множество уникальных слов
   - `word_frequency` — словарь {слово: частота} (используйте `Counter`)
   - `longest_word` — самое длинное слово
   - `most_common` — топ-5 самых частых слов

### Задание 2: Срезы и преобразования

```python
# Дана строка с данными
data = "apple,banana,cherry,date,elderberry,fig,grape,honeydew"
```

1. Преобразуйте в список фруктов
2. Получите первые 3 фрукта (срез)
3. Получите последние 3 фрукта (срез)
4. Получите каждый второй фрукт (срез с шагом)
5. Получите список в обратном порядке (срез)
6. Получите список фруктов с длиной больше 5 (list comprehension)

### Задание 3: Работа со словарями

Создайте функцию `merge_orders(orders)`:

```python
orders = [
    {"customer": "Alice", "product": "apple", "quantity": 3},
    {"customer": "Bob", "product": "banana", "quantity": 2},
    {"customer": "Alice", "product": "cherry", "quantity": 1},
    {"customer": "Alice", "product": "apple", "quantity": 2},
    {"customer": "Bob", "product": "date", "quantity": 4},
]
```

Функция должна вернуть словарь, где ключ — имя покупателя, а значение — словарь с суммарным количеством по каждому продукту:

```python
{
    "Alice": {"apple": 5, "cherry": 1},
    "Bob": {"banana": 2, "date": 4},
}
```

### Задание 4: Исправьте анти-паттерны

Перепишите следующий код идиоматично:

```python
# Фрагмент 1
def get_unique(items):
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result

# Фрагмент 2
def count_words(words):
    result = {}
    for word in words:
        if word in result:
            result[word] = result[word] + 1
        else:
            result[word] = 1
    return result

# Фрагмент 3
def filter_adults(people):
    result = []
    for i in range(len(people)):
        person = people[i]
        if person["age"] >= 18:
            result.append(person["name"])
    return result
```

---

## Дополнительные материалы

### 📖 Книги

- **«Fluent Python»** (главы 2, 3, 8) — Luciano Ramalho. Глубокий разбор всех структур данных Python.
- **«Effective Python»** (советы 11–18) — Brett Slatkin. Практические рекомендации по работе со структурами данных.

### 🎥 Видео

- **«The Mighty Dictionary»** — Brandon Rhodes (PyCon 2010). Как устроены словари внутри CPython.
- **«Modern Dictionaries»** — Raymond Hettinger (PyCon 2017). Как компактное представление dict ускорило Python 3.6.

### 🔗 Ссылки

- [Python 3 Tutorial: Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python 3: collections — Container datatypes](https://docs.python.org/3/library/collections.html)
- [Time Complexity of Python Operations](https://wiki.python.org/moin/TimeComplexity)
- [PEP 202 — List Comprehensions](https://peps.python.org/pep-0202/)
- [PEP 274 — Dict Comprehensions](https://peps.python.org/pep-0274/)

### 💡 Интересные факты

- Словари в Python 3.6+ стали более компактными благодаря новому внутреннему представлению (Raymond Hettinger). Память сократилась на 20–25%, а итерация ускорилась.
- `namedtuple` из модуля `collections` — это кортеж с именованными полями, эдакий «легковесный класс» без методов.
- `frozenset` — неизменяемая версия `set`, которую можно использовать как ключ словаря.
- `*`-оператор распаковки работает со всеми итерируемыми объектами: `[*a, *b]` объединяет два списка, `{**d1, **d2}` — два словаря (Python 3.5+).