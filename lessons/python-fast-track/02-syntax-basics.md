---
title: "Синтаксис Python: что нужно знать за 30 минут"
order: 2
tags: ["синтаксис", "типы", "управляющие-конструкции"]
prerequisites: "Урок 1"
objective: "Освоить базовый синтаксис Python: переменные, типы, условия, циклы, функции"
---

## Введение

Одна из первых вещей, которая удивляет программистов, переходящих на Python с Java, C++ или C# — **отсутствие точек с запятой и фигурных скобок**. Блоки кода в Python выделяются отступами (indentation), и это не просто косметическое решение — это фундаментальная часть синтаксиса.

Этот урок покроет всё, что нужно знать для комфортного старта: переменные и динамическую типизацию, условные конструкции, циклы и базовые функции. Мы не будем углубляться в продвинутые темы — для этого есть отдельные уроки.

### 🎯 Цель урока

Освоить базовый синтаксис Python: переменные, типы, условия, циклы, функции. После этого урока вы сможете читать и писать простые Python-программы без постоянного обращения к документации.

### 📋 Предпосылки

Вы прочитали Урок 1 («Почему Python») и понимаете философию языка. Вы уже программируете на Java, C++, JavaScript, C# или подобном языке и знаете, что такое переменные, типы, условия и циклы.

---

## Основная часть

### 1. Отступы — это синтаксис

Самое заметное отличие Python от C-подобных языков: **блоки кода выделяются отступами, а не фигурными скобками**. Это не опционально — это жёсткое требование синтаксиса.

```python
# ✅ Правильно: 4 пробела на уровень отступа
def greet(name):
    if name:
        print(f"Hello, {name}!")
    else:
        print("Hello, stranger!")
```

```java
// Java: фигурные скобки (опциональны для однострочников)
public void greet(String name) {
    if (name != null && !name.isEmpty()) {
        System.out.println("Hello, " + name + "!");
    } else {
        System.out.println("Hello, stranger!");
    }
}
```

```cpp
// C++: фигурные скобки
void greet(const std::string& name) {
    if (!name.empty()) {
        std::cout << "Hello, " << name << "!" << std::endl;
    } else {
        std::cout << "Hello, stranger!" << std::endl;
    }
}
```

**Правила отступов в Python:**

| Правило | Пример |
|---------|--------|
| Один уровень = 4 пробела (PEP 8) | Стандарт индустрии. Не используйте табуляцию |
| Не смешивайте пробелы и табы | Python 3 запрещает смешивание — ошибка `TabError` |
| После двоеточия (`:`) — новая строка с отступом | `if x:`, `for x in:`, `def f():`, `class C:` |
| Пустые блоки — `pass` | `if x: pass` — заглушка |

**Анти-паттерн: неправильные отступы**

```python
# ❌ Ошибка IndentationError
if True:
print("Hello")  # Нет отступа!
```

```python
# ❌ Ошибка TabError (смешивание табов и пробелов)
def foo():
    print("indented with spaces")
	print("indented with tab")  # Tab!
```

### 2. Переменные и динамическая типизация

Python — язык с **динамической типизацией**. Вы не объявляете тип переменной; он определяется во время выполнения.

```python
# Python: тип определяется автоматически
name = "Alice"          # str
age = 30                # int
height = 1.75           # float
is_student = False      # bool
data = [1, 2, 3]        # list
```

```java
// Java: строгая статическая типизация
String name = "Alice";
int age = 30;
double height = 1.75;
boolean isStudent = false;
List<Integer> data = Arrays.asList(1, 2, 3);
```

```cpp
// C++: статическая типизация
std::string name = "Alice";
int age = 30;
double height = 1.75;
bool is_student = false;
std::vector<int> data = {1, 2, 3};
```

**Важно:** динамическая типизация ≠ отсутствие типов. Типы есть всегда, просто они проверяются во время выполнения, а не компиляции.

```python
# Переменная может менять тип — но это не всегда хорошая идея
x = 42
print(type(x))  # <class 'int'>

x = "hello"
print(type(x))  # <class 'str'>

x = [1, 2, 3]
print(type(x))  # <class 'list'>
```

**Анти-паттерн: злоупотребление динамической типизацией**

```python
# ❌ Плохо: одна переменная меняет тип в рамках одной функции
def process(data):
    data = data.strip()              # data была bytes, стала str
    data = int(data)                 # data была str, стала int
    data = [data]                    # data была int, стала list
    return data
```

```python
# ✅ Лучше: используйте осмысленные имена для разных типов
def process(raw_data):
    text = raw_data.strip()
    value = int(text)
    return [value]
```

### 3. Базовые типы: числа, строки, булевы значения

#### Числа

```python
# Целые числа (int) — произвольная точность
big = 10**100  # 10^100 — никакого переполнения!
print(big)     # 10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# Вещественные числа (float) — IEEE 754 double
pi = 3.141592653589793

# Комплексные числа (complex) — встроенные!
z = 2 + 3j
print(z.real)  # 2.0
print(z.imag)  # 3.0
print(z * z)   # (-5+12j)
```

```java
// Java: BigInteger для больших чисел, Complex — только через Apache Commons Math
import java.math.BigInteger;
BigInteger big = new BigInteger("10").pow(100);  // 10 строк ceremony
```

#### Строки

```python
# Строки: одинарные, двойные, тройные кавычки
s1 = 'hello'
s2 = "hello"
s3 = """Многострочная
строка с "кавычками" внутри"""
s4 = '''Тоже
многострочная'''

# Строки — неизменяемые (как в Java, в отличие от C++)
name = "Alice"
# name[0] = "B"  # ❌ TypeError: 'str' object does not support item assignment

# f-строки (Python 3.6+) — интерполяция
name = "Alice"
age = 30
print(f"{name} is {age} years old")  # Alice is 30 years old
print(f"{name.upper()} is {age + 5} in 5 years")  # ALICE is 35 in 5 years

# Конкатенация и умножение
print("Hello, " + "World!")   # Hello, World!
print("Ha" * 3)               # HaHaHa
```

```java
// Java: форматирование строк
String name = "Alice";
int age = 30;
System.out.println(String.format("%s is %d years old", name, age));
// или
System.out.println(name + " is " + age + " years old");
```

```javascript
// JavaScript: template literals (ближе всего к f-строкам)
const name = "Alice";
const age = 30;
console.log(`${name} is ${age} years old`);
```

#### Булевы значения и Truthiness

```python
# Булевы значения: True и False (с большой буквы!)
is_valid = True
is_empty = False

# Любой объект может быть проверен на истинность
# Пустые контейнеры, None, 0, "" — ложны
# Всё остальное — истинно

# ✅ Идиоматично: используйте truthiness
if items:                    # вместо if len(items) > 0
    print("Список не пуст")

if name:                     # вместо if name != ""
    print(f"Привет, {name}")

if not errors:               # вместо if len(errors) == 0
    print("Ошибок нет")

# ❌ Анти-паттерн: явные сравнения с True/False/None
if is_valid == True:         # избыточно
    ...
if is_valid is True:         # ещё хуже
    ...
```

**Таблица truthiness:**

| Значение | Истинность |
|----------|-----------|
| `True` | ✅ True |
| `False` | ❌ False |
| `None` | ❌ False |
| `0`, `0.0`, `0j` | ❌ False |
| `""` (пустая строка) | ❌ False |
| `[]`, `()`, `{}`, `set()` | ❌ False |
| `"hello"`, `[1,2]`, `42` | ✅ True |

### 4. Условные конструкции: if / elif / else

```python
# Классический if / elif / else
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Score {score} → Grade {grade}")  # Score 85 → Grade B
```

**Сравнение с другими языками:**

| Язык | Синтаксис | Особенность |
|------|-----------|-------------|
| Python | `if ... elif ... else` | Нет скобок вокруг условия, блоки — отступами |
| Java | `if (...) {...} else if (...) {...} else {...}` | Скобки вокруг условия обязательны |
| C++ | `if (...) {...} else if (...) {...} else {...}` | Скобки вокруг условия обязательны |
| JavaScript | `if (...) {...} else if (...) {...} else {...}` | Скобки вокруг условия обязательны |

**Тернарный оператор (условное выражение):**

```python
# Python: value_if_true if condition else value_if_false
age = 20
status = "Adult" if age >= 18 else "Minor"
print(status)  # Adult

# Java: condition ? value_if_true : value_if_false
# String status = age >= 18 ? "Adult" : "Minor";
```

**Обратите внимание:** порядок `if ... else` в Python отличается от тернарного оператора `? :` в C-подобных языках. В Python условие *посередине*, что читается ближе к естественному языку.

**Анти-паттерн: вложенные if (Java-стиль)**

```python
# ❌ Плохо: глубоко вложенные условия
def process_order(order):
    if order is not None:
        if order.status == "pending":
            if order.amount > 0:
                if order.customer.is_verified:
                    # наконец-то логика
                    ...
```

```python
# ✅ Идиоматично: early return (guard clauses)
def process_order(order):
    if order is None:
        return
    if order.status != "pending":
        return
    if order.amount <= 0:
        return
    if not order.customer.is_verified:
        return
    # логика здесь, на верхнем уровне отступа
    ...
```

### 5. Циклы: for и while

#### Цикл for: итерация по элементам

Python не имеет традиционного `for (int i = 0; i < n; i++)`. Вместо этого `for` всегда итерируется по **итерируемому объекту** — списку, строке, диапазону, файлу и т.д.

```python
# Итерация по списку
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Итерация по строке (по символам)
for char in "Python":
    print(char)

# Итерация по диапазону чисел
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 7):   # 2, 3, 4, 5, 6
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8 (шаг 2)
    print(i)
```

**Сравнение: Python for vs Java/C++ for**

```python
# Python: идиоматичная итерация по элементам
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

```java
// Java: три разных способа
String[] fruits = {"apple", "banana", "cherry"};

// Способ 1: индексы (многословно)
for (int i = 0; i < fruits.length; i++) {
    System.out.println(fruits[i]);
}

// Способ 2: enhanced for (похоже на Python)
for (String fruit : fruits) {
    System.out.println(fruit);
}

// Способ 3: Stream API (Java 8+)
Arrays.stream(fruits).forEach(System.out::println);
```

```cpp
// C++: range-based for (C++11+)
std::vector<std::string> fruits = {"apple", "banana", "cherry"};
for (const auto& fruit : fruits) {
    std::cout << fruit << std::endl;
}
```

**Если нужен индекс: `enumerate()`**

```python
# ✅ Идиоматично: enumerate для индекса
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Вывод:
# 0: apple
# 1: banana
# 2: cherry

# С начальным индексом
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")

# ❌ Анти-паттерн: ручной индекс
for i in range(len(fruits)):
    fruit = fruits[i]
    print(f"{i}: {fruit}")
```

#### Цикл while

```python
# while: выполняется пока условие истинно
count = 0
while count < 5:
    print(count)
    count += 1

# Бесконечный цикл с выходом
while True:
    user_input = input("Введите 'quit' для выхода: ")
    if user_input == "quit":
        break
    print(f"Вы ввели: {user_input}")
```

#### Ключевые слова break и continue

```python
# break: выход из цикла
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: пропуск итерации
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
```

#### else в циклах (уникальная фича Python!)

```python
# else после for/while: выполняется, если цикл завершился БЕЗ break
for i in range(5):
    if i == 10:  # никогда не случится
        break
else:
    print("Цикл завершился без break")  # Это выведется

# Полезный пример: поиск элемента
def find_user(users, target_name):
    for user in users:
        if user.name == target_name:
            print(f"Найден: {user}")
            break
    else:
        print(f"Пользователь {target_name} не найден")
```

Этот `else` часто сбивает с толку новичков — его можно читать как `nobreak`.

### 6. Функции: объявление и вызов

```python
# Определение функции
def greet(name, greeting="Hello"):
    """Возвращает приветствие. (Это docstring — документация функции.)"""
    return f"{greeting}, {name}!"

# Вызов
print(greet("Alice"))           # Hello, Alice!
print(greet("Bob", "Hi"))       # Hi, Bob!
print(greet(greeting="Hey", name="Charlie"))  # Hey, Charlie! (keyword arguments)

# Функция без return возвращает None
def log(message):
    print(f"[LOG] {message}")
    # Неявный return None

result = log("test")  # [LOG] test
print(result)         # None
```

**Сравнение с другими языками:**

```python
# Python
def add(a, b):
    return a + b
```

```java
// Java
public static int add(int a, int b) {
    return a + b;
}
```

```cpp
// C++
int add(int a, int b) {
    return a + b;
}
```

```javascript
// JavaScript
function add(a, b) {
    return a + b;
}
```

В Python, в отличие от Java и C++:
- **Нет типов в сигнатуре** (но есть опциональные аннотации: `def add(a: int, b: int) -> int:`)
- **Нет ключевого слова для возвращаемого типа** (он определяется динамически)
- **Нет `public`/`private`/`static`** (это решается на уровне модуля и соглашений)

#### Параметры по умолчанию

```python
# Значения по умолчанию вычисляются ОДИН РАЗ при определении функции
def append_to_list(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target

# ❌ Анти-паттерн: изменяемый объект как значение по умолчанию
def bad_append(item, target=[]):  # Одна и та же ссылка на список!
    target.append(item)
    return target

print(bad_append(1))  # [1]
print(bad_append(2))  # [1, 2] — Ожидали [2], а получили [1, 2]!
print(bad_append(3))  # [1, 2, 3] — Список растёт при каждом вызове!
```

Это одна из классических «ловушек» Python для новичков. Всегда используйте `None` как значение по умолчанию для изменяемых типов.

#### Keyword arguments (именованные аргументы)

```python
# Позиционные и keyword-аргументы
def create_user(name, age, email=None, is_active=True):
    return {
        "name": name,
        "age": age,
        "email": email,
        "is_active": is_active,
    }

# Все способы вызова валидны:
user1 = create_user("Alice", 30)
user2 = create_user("Bob", 25, email="bob@example.com")
user3 = create_user(age=22, name="Charlie", is_active=False)

# ❌ Нельзя: позиционные после keyword
# create_user(name="Dave", 35)  # SyntaxError
```

### 7. Ввод и вывод

```python
# Вывод на экран
print("Hello")                     # Одно значение
print("Hello", "World")            # Несколько значений (через пробел)
print("Hello", "World", sep="-")   # Свой разделитель
print("Hello", end="!")            # Свой конец строки (вместо \n)
print("World")                     # Hello!World

# Ввод с клавиатуры
name = input("Введите имя: ")      # Всегда возвращает str
age = int(input("Введите возраст: "))  # Явное преобразование
```

### 8. Комментарии и документация

```python
# Однострочный комментарий

"""
Многострочный
комментарий (на самом деле это строка, которая никуда не присваивается)
"""

def calculate(x, y):
    """Это docstring — документация функции.

    Доступна через help(calculate) или calculate.__doc__.
    Описывает, ЧТО делает функция, а не КАК.
    """
    return x + y

# Доступ к документации
help(calculate)
print(calculate.__doc__)
```

---

## Практическое задание

### Задание 1: FizzBuzz

Напишите программу, которая выводит числа от 1 до 50 с заменами:
- Если число делится на 3 — вывести `Fizz`
- Если на 5 — `Buzz`
- Если на 3 и на 5 — `FizzBuzz`
- Иначе — само число

Требования:
- Используйте `for` и `range`
- Используйте `if / elif / else`
- НЕ используйте `while` или ручные индексы

### Задание 2: Калькулятор с обработкой ввода

Напишите программу-калькулятор, которая:
1. Запрашивает у пользователя два числа
2. Запрашивает операцию (`+`, `-`, `*`, `/`)
3. Выводит результат
4. Обрабатывает деление на ноль (выводит «Ошибка: деление на ноль»)
5. Продолжает работать, пока пользователь не введёт `quit`

### Задание 3: Исправьте код

Даны фрагменты кода с ошибками. Найдите и исправьте их:

```python
# Фрагмент 1
def bad_default(items=[]):
    items.append("x")
    return items

# Фрагмент 2
for i in range(len(names)):
    name = names[i]
    print(f"{i}: {name}")

# Фрагмент 3
if len(items) == 0:
    print("Пусто")
else:
    if len(items) == 1:
        print("Один элемент")
    else:
        if len(items) > 1:
            print("Много элементов")

# Фрагмент 4
x = 10
if x > 5:
print("Больше 5")
```

### Задание 4: Функция с валидацией

Напишите функцию `create_profile(name, age, *, email=None, phone=None)`:
- `name` — обязательный строковый параметр
- `age` — обязательный целочисленный параметр
- `email` и `phone` — keyword-only параметры (хотя бы один должен быть передан)
- Функция должна возвращать словарь с профилем
- Если `age < 0` или `age > 150` — выбросить `ValueError`
- Используйте docstring

---

## Дополнительные материалы

### 📖 Книги

- **«Python Crash Course»** (главы 2–8) — Eric Matthes. Пошаговое введение в синтаксис.
- **«Fluent Python»** (глава 2) — Luciano Ramalho. Глубокий разбор типов и структур данных.

### 🎥 Видео

- **«Transforming Code into Beautiful, Idiomatic Python»** — Raymond Hettinger (PyCon 2013). Как писать идиоматичный Python-код.
- **«Beyond PEP 8»** — Raymond Hettinger (PyCon 2015). О читаемости кода сверх стандартов оформления.

### 🔗 Ссылки

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Python 3 Tutorial: Control Flow](https://docs.python.org/3/tutorial/controlflow.html)
- [Python 3 Tutorial: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [Python 3 Built-in Functions](https://docs.python.org/3/library/functions.html)

### 💡 Интересные факты

- Python использует 4 пробела для отступа по PEP 8, но технически можно использовать любое количество — главное, чтобы оно было одинаковым в пределах блока. 4 пробела — это результат голосования в сообществе.
- `range()` в Python 3 возвращает не список, а ленивый объект, который вычисляет следующее значение на лету. Это экономит память: `range(10**9)` занимает столько же места, сколько `range(3)`.
- `print()` стал функцией в Python 3 (вместо statement в Python 2) — это позволяет передавать его как аргумент: `map(print, items)`.
- Конструкция `for ... else` настолько неочевидна, что обсуждалось её удаление из языка. Но она осталась, потому что полезна для паттерна «поиск с fallback».