---
title: "Оптимизация Python-кода: паттерны и антипаттерны"
order: 2
tags: ["оптимизация", "производительность", "паттерны", "timeit"]
prerequisites: "Урок 1"
objective: "Освоить практические техники оптимизации Python-кода"
---

# Оптимизация Python-кода: паттерны и антипаттерны

## Введение

> "Преждевременная оптимизация — корень всех зол." — Дональд Кнут

Профилирование (Урок 1) показало вам, **где** болит. Теперь мы разберём, **как лечить**. Этот урок — практический каталог проверенных техник оптимизации Python-кода. Каждая техника подкреплена микробенчмарками на `timeit` и сравнением с аналогами из Java, C++ и JavaScript.

Ключевой принцип: **измеряйте до и после**. Оптимизация без бенчмаркинга — это шаманство. Мы будем использовать `timeit` для каждого приёма.

### 🎯 Цель урока

Освоить практические техники оптимизации Python-кода.

### 📋 Предпосылки

Урок 1: профилирование (cProfile, line_profiler, memory_profiler).

---

## Основная часть

### 1. Микробенчмаркинг с timeit

`timeit` — модуль стандартной библиотеки для точного измерения времени выполнения небольших фрагментов кода. Он отключает сборщик мусора, выполняет код многократно и возвращает лучшее время.

```python
import timeit
from typing import Callable, Any


def benchmark(
    name: str,
    stmt: str,
    setup: str = "",
    number: int = 1000,
    globals_dict: dict[str, Any] | None = None,
) -> None:
    """Удобная обёртка для timeit с форматированным выводом."""
    total = timeit.timeit(
        stmt, setup=setup, number=number, globals=globals_dict
    )
    per_iter = (total / number) * 1_000_000  # микросекунды
    print(f"{name:40s}: {per_iter:8.2f} µs/iter  (total={total:.4f}s)")


# Пример: сравнение двух подходов
N = 10_000

benchmark(
    "Генератор списка (list comp)",
    stmt="[i * 2 for i in range(n)]",
    globals_dict={"n": N},
)

benchmark(
    "Цикл for с append",
    stmt="""result = []
for i in range(n):
    result.append(i * 2)""",
    globals_dict={"n": N},
)
```

Пример вывода:

```
Генератор списка (list comp)            :    45.23 µs/iter  (total=0.0452s)
Цикл for с append                       :    78.91 µs/iter  (total=0.0789s)
```

Разница — 1.7x. Генератор списка быстрее, потому что выполняется на уровне C-цикла интерпретатора, без байткода для каждой итерации.

---

### 2. Локальное кеширование переменных

Python разрешает имена через словари (locals, globals, builtins). Каждый доступ к глобальной переменной или атрибуту — это словарный поиск. Кеширование в локальную переменную устраняет этот оверхед.

```python
import timeit
import math


# Антипаттерн: глобальный доступ в цикле
def slow_global_access(n: int) -> float:
    result = 0.0
    for i in range(n):
        result += math.sin(i) * math.cos(i)  # math — глобальный поиск
    return result


# Паттерн: локальное кеширование
def fast_local_cache(n: int) -> float:
    result = 0.0
    sin = math.sin   # Кешируем в локальную переменную
    cos = math.cos
    for i in range(n):
        result += sin(i) * cos(i)
    return result


# Бенчмарк
N = 1_000_000

print("=== Глобальный доступ vs Локальное кеширование ===")
benchmark("Глобальный math.sin", "slow_global_access(n)",
          globals_dict={"slow_global_access": slow_global_access, "n": N})
benchmark("Локальный sin", "fast_local_cache(n)",
          globals_dict={"fast_local_cache": fast_local_cache, "n": N})
```

Ожидаемый результат: локальное кеширование быстрее на 25–35%.

#### Таблица: что кешировать

| Операция                   | Оверхед (относительно локальной) | Рекомендация          |
|----------------------------|----------------------------------|------------------------|
| `module.func` в цикле      | +30–40%                          | Кешировать в локальную |
| `obj.attr` в цикле         | +20–50%                          | Кешировать в локальную |
| `obj.method` в цикле       | +20–30%                          | Кешировать в локальную |
| `dict[key]` в цикле        | +5–10%                           | Не критично            |
| `local_var` в цикле        | 0% (базовый)                     | —                      |

---

### 3. Генераторы списков vs map vs циклы

Классический вопрос: что быстрее? Ответ зависит от контекста.

```python
import timeit
from operator import mul
from functools import partial


def compare_iteration_patterns(n: int = 1_000_000) -> None:
    """Сравнение паттернов итерации."""
    # Простое преобразование: x → x * 2
    print("\n=== Простое преобразование: x → x * 2 ===")

    benchmark(
        "List comprehension",
        stmt="[x * 2 for x in range(n)]",
        globals_dict={"n": n},
    )

    benchmark(
        "map + lambda",
        stmt="list(map(lambda x: x * 2, range(n)))",
        globals_dict={"n": n},
    )

    benchmark(
        "Цикл for + append",
        stmt="""result = []
for x in range(n):
    result.append(x * 2)""",
        globals_dict={"n": n},
    )

    # С фильтром: x → x*2, только чётные
    print("\n=== С фильтром: x → x*2, только x % 2 == 0 ===")

    benchmark(
        "List comprehension + filter",
        stmt="[x * 2 for x in range(n) if x % 2 == 0]",
        globals_dict={"n": n},
    )

    benchmark(
        "filter + map + lambda",
        stmt="list(map(lambda x: x * 2, filter(lambda x: x % 2 == 0, range(n))))",
        globals_dict={"n": n},
    )

    benchmark(
        "Цикл for + append + if",
        stmt="""result = []
for x in range(n):
    if x % 2 == 0:
        result.append(x * 2)""",
        globals_dict={"n": n},
    )


compare_iteration_patterns()
```

#### Итоговая таблица

| Метод                        | Скорость       | Читаемость | Когда использовать              |
|------------------------------|----------------|------------|---------------------------------|
| List comprehension           | ⭐⭐⭐ Быстро    | ⭐⭐⭐       | Всегда, когда возможно          |
| Цикл for + append            | ⭐⭐ Средне     | ⭐⭐⭐+      | Сложная логика, несколько шагов |
| map + lambda                 | ⭐⭐ Средне     | ⭐          | Функциональный стиль, pipe      |
| map + C-функция              | ⭐⭐⭐+ Быстро  | ⭐⭐         | Числовые операции (str, int, operator) |
| Генераторное выражение       | ⭐⭐⭐ Быстро   | ⭐⭐⭐       | Ленивые вычисления, экономия памяти |

**Вывод:** list comprehensions выигрывают в 90% случаев. `map` с C-функциями (без lambda) может быть быстрее для простых операций.

---

### 4. Конкатенация строк: join() vs + vs форматирование

Одна из самых частых ошибок новичков:

```python
import timeit
from io import StringIO


def compare_string_concat(n: int = 10_000) -> None:
    """Сравнение методов конкатенации строк."""

    print("\n=== Конкатенация 10 000 строк ===")

    # Антипаттерн: + в цикле
    benchmark(
        "❌ s += в цикле (квадратичная сложность!)",
        stmt="""s = ""
for i in range(n):
    s += str(i)""",
        globals_dict={"n": n},
    )

    # Паттерн: join()
    benchmark(
        "✅ ''.join() — линейная сложность",
        stmt="''.join(str(i) for i in range(n))",
        globals_dict={"n": n},
    )

    # Паттерн: join() со списком (быстрее генератора)
    benchmark(
        "✅ ''.join([list comp]) — быстрее генератора",
        stmt="''.join([str(i) for i in range(n)])",
        globals_dict={"n": n},
    )

    # Паттерн: StringIO
    benchmark(
        "✅ StringIO — для сложного форматирования",
        stmt="""buf = __import__('io').StringIO()
for i in range(n):
    buf.write(str(i))
buf.getvalue()""",
        globals_dict={"n": n},
    )


compare_string_concat()
```

Ожидаемые результаты (n=10_000):

| Метод               | Время       | Сложность    | Комментарий                       |
|---------------------|-------------|-------------|-----------------------------------|
| `s += ...` в цикле  | ~500 мс     | O(n²)       | Новая строка копируется каждый раз |
| `''.join()` + gen   | ~5 мс       | O(n)        | Хорошо, но генератор даёт оверхед |
| `''.join()` + list  | ~3 мс       | O(n)        | Лучший вариант!                   |
| `StringIO`          | ~4 мс       | O(n)        | Когда нужно много операций записи |

**Почему `+=` в цикле медленный?** Строки в Python неизменяемы. `s += str(i)` создаёт **новую** строку, копируя все предыдущие символы. На 10 000 итераций это ~50 миллионов операций копирования символов.

---

### 5. collections.deque vs list для очередей

```python
import timeit
from collections import deque


def compare_queue_operations(n: int = 100_000) -> None:
    """Сравнение list vs deque для FIFO-очереди."""

    print("\n=== FIFO: добавление справа, удаление слева ===")

    # Антипаттерн: list.pop(0) — O(n) сдвиг
    benchmark(
        "❌ list.pop(0) — O(n) сдвиг элементов",
        stmt="""lst = list(range(n))
while lst:
    lst.pop(0)""",
        globals_dict={"n": n},
        number=10,
    )

    # Паттерн: deque.popleft() — O(1)
    benchmark(
        "✅ deque.popleft() — O(1)",
        stmt="""dq = __import__('collections').deque(range(n))
while dq:
    dq.popleft()""",
        globals_dict={"n": n},
        number=10,
    )


compare_queue_operations()
```

| Операция           | `list`          | `deque`      |
|--------------------|-----------------|--------------|
| `append` справа    | O(1) амортизированное | O(1)    |
| `pop` справа       | O(1)            | O(1)         |
| `pop(0)` слева     | O(n) — сдвиг!   | O(1)         |
| `insert(0, x)`     | O(n) — сдвиг!   | O(1)         |
| Доступ по индексу  | O(1)            | O(n)         |
| Память             | Компактнее      | Чуть больше (блоки) |

**Правило:** если нужен доступ по индексу — `list`. Если нужна очередь (FIFO) или дек (двусторонняя очередь) — `deque`.

---

### 6. __slots__ для экономии памяти

По умолчанию каждый экземпляр класса хранит атрибуты в `__dict__`. Это словарь — дешёвый для нескольких экземпляров, но для миллионов объектов накладные расходы огромны.

```python
import sys
from typing import Any


class PointWithDict:
    """Обычный класс: каждый экземпляр имеет __dict__ (~152 байта overhead)."""

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


class PointWithSlots:
    """Класс со __slots__: нет __dict__, ~56 байт overhead."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


def compare_memory() -> None:
    """Сравнение потребления памяти."""
    N = 1_000_000

    # Создаём по одному экземпляру для измерения размера
    dict_point = PointWithDict(1.0, 2.0, 3.0)
    slots_point = PointWithSlots(1.0, 2.0, 3.0)

    print(f"PointWithDict  (1 экз.): {sys.getsizeof(dict_point)} байт")
    print(f"  + __dict__: {sys.getsizeof(dict_point.__dict__)} байт")
    print(f"PointWithSlots (1 экз.): {sys.getsizeof(slots_point)} байт")

    # Оценка для N экземпляров
    dict_total = (sys.getsizeof(dict_point) + sys.getsizeof(dict_point.__dict__)) * N
    slots_total = sys.getsizeof(slots_point) * N
    print(f"\n{N:,} экземпляров:")
    print(f"  PointWithDict:  {dict_total / 1024 / 1024:.1f} MiB")
    print(f"  PointWithSlots: {slots_total / 1024 / 1024:.1f} MiB")
    print(f"  Экономия: {(1 - slots_total / dict_total) * 100:.1f}%")


compare_memory()
```

Ожидаемый результат: `__slots__` экономит ~60% памяти.

#### __slots__: плюсы и минусы

| ✅ Плюсы                              | ❌ Минусы                                     |
|---------------------------------------|-----------------------------------------------|
| Экономия памяти (до 50–70%)           | Нельзя добавлять новые атрибуты динамически   |
| Быстрее доступ к атрибутам (на ~15%)  | Не работает множественное наследование        |
| Нет __dict__ и __weakref__            | Несовместимо с некоторыми ORM и фреймворками  |
|                                     | Нельзя использовать @cached_property         |

---

### 7. lru_cache для мемоизации

`functools.lru_cache` — это декоратор, который кеширует результаты вызовов функции. Идеально для рекурсивных и дорогих чистых функций.

```python
import timeit
from functools import lru_cache


def fibonacci_no_cache(n: int) -> int:
    """Наивная рекурсия — O(2^n)."""
    if n < 2:
        return n
    return fibonacci_no_cache(n - 1) + fibonacci_no_cache(n - 2)


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    """Рекурсия с мемоизацией — O(n)."""
    if n < 2:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def compare_fibonacci() -> None:
    """Сравнение наивной и кешированной версий."""
    print("\n=== Fibonacci(30): без кеша vs с lru_cache ===")

    benchmark(
        "❌ Без кеша (O(2^n))",
        stmt="fibonacci_no_cache(30)",
        globals_dict={"fibonacci_no_cache": fibonacci_no_cache},
        number=1,
    )

    # Сбрасываем кеш перед измерением
    fibonacci_cached.cache_clear()
    benchmark(
        "✅ lru_cache (O(n))",
        stmt="fibonacci_cached(30)",
        globals_dict={"fibonacci_cached": fibonacci_cached},
        number=1,
    )

    # Информация о кеше
    print(f"\nИнформация о кеше: {fibonacci_cached.cache_info()}")


compare_fibonacci()
```

#### Параметры lru_cache

| Параметр    | Описание                                      |
|-------------|-----------------------------------------------|
| `maxsize`   | Максимальный размер кеша (None = безлимитный) |
| `typed`     | Различать `1` и `1.0` (разные типы)           |

#### Когда НЕ использовать lru_cache

- Функция имеет побочные эффекты (I/O, мутации)
- Аргументы не хешируемы (списки, словари)
- Кеш будет расти бесконечно при `maxsize=None`
- Функция вызывается с уникальными аргументами каждый раз

---

### 8. Избегание атрибутных доступов в горячих циклах

Каждый `obj.attr` в Python — это словарный поиск (или слотовый доступ). В горячих циклах это складывается в ощутимые накладные расходы.

```python
import timeit


class DataProcessor:
    def __init__(self) -> None:
        self.multiplier = 2.5
        self.offset = 1.0

    def process_slow(self, data: list[float]) -> list[float]:
        """Антипаттерн: self.attr в каждой итерации."""
        return [x * self.multiplier + self.offset for x in data]

    def process_fast(self, data: list[float]) -> list[float]:
        """Паттерн: кеширование атрибутов в локальные переменные."""
        mul = self.multiplier
        off = self.offset
        return [x * mul + off for x in data]


def compare_attribute_access() -> None:
    """Сравнение атрибутных доступов."""
    processor = DataProcessor()
    data = list(range(100_000))

    print("\n=== Атрибутные доступы в цикле ===")

    benchmark(
        "❌ self.attr в каждой итерации",
        stmt="processor.process_slow(data)",
        globals_dict={"processor": processor, "data": data},
        number=100,
    )

    benchmark(
        "✅ Локальное кеширование self.attr",
        stmt="processor.process_fast(data)",
        globals_dict={"processor": processor, "data": data},
        number=100,
    )


compare_attribute_access()
```

---

### 9. array vs list для числовых данных

Модуль `array` предоставляет типизированные массивы — компактный аналог списков для однородных числовых данных:

```python
import sys
import array
import timeit


def compare_array_vs_list(n: int = 1_000_000) -> None:
    """Сравнение list и array.array для числовых данных."""

    # Память
    lst = list(range(n))
    arr = array.array("i", range(n))  # 'i' = signed int (4 байта)

    print(f"list[int] ({n} элементов): {sys.getsizeof(lst) + n * 28} байт")
    print(f"array('i') ({n} элементов): {sys.getsizeof(arr) + n * 4} байт")

    # Скорость: сумма элементов
    print("\n=== Сумма элементов ===")
    benchmark("list[int] sum", "sum(lst)",
              globals_dict={"lst": lst}, number=100)
    benchmark("array('i') sum", "sum(arr)",
              globals_dict={"arr": arr}, number=100)

    # Скорость: доступ по индексу
    print("\n=== Доступ по индексу ===")
    benchmark(
        "list[int] доступ",
        stmt="for i in range(10000): _ = lst[i]",
        globals_dict={"lst": lst},
        number=100,
    )
    benchmark(
        "array('i') доступ",
        stmt="for i in range(10000): _ = arr[i]",
        globals_dict={"arr": arr},
        number=100,
    )


compare_array_vs_list()
```

| Характеристика    | `list[int]`              | `array('i')`         |
|-------------------|--------------------------|----------------------|
| Память на элемент | ~28 байт (объект int)    | 4 байта              |
| Гибкость          | Любые типы               | Только int           |
| Скорость sum()    | Медленнее (unboxing)     | Быстрее              |
| Индексный доступ  | Быстрее                  | Медленнее (boxing)   |
| C-совместимость   | Нет                      | buffer protocol      |

**Вывод:** `array` выигрывает по памяти, но проигрывает по скорости доступа. Для числовых вычислений используйте NumPy.

---

### 10. NumPy для числовых операций

Когда `array` недостаточно, NumPy предоставляет векторизованные операции:

```python
import timeit


def compare_numpy_vs_python(n: int = 1_000_000) -> None:
    """Сравнение Python vs NumPy для числовых операций."""
    python_setup = f"import random; data = [random.random() for _ in range({n})]"
    numpy_setup = f"import numpy as np; data = np.random.random({n})"

    print(f"\n=== NumPy vs Python (n={n:,}) ===")

    benchmark(
        "Python: [x * 2 + 1 for x in data]",
        stmt="[x * 2 + 1 for x in data]",
        setup=python_setup,
        number=10,
    )

    benchmark(
        "NumPy: data * 2 + 1 (векторизованно)",
        stmt="data * 2 + 1",
        setup=numpy_setup,
        number=10,
    )

    benchmark(
        "Python: sum(data) / len(data)",
        stmt="sum(data) / len(data)",
        setup=python_setup,
        number=10,
    )

    benchmark(
        "NumPy: data.mean()",
        stmt="data.mean()",
        setup=numpy_setup,
        number=10,
    )


compare_numpy_vs_python()
```

Ожидаемый результат: NumPy быстрее в 10–100x для векторных операций, потому что:
1. Операции выполняются в скомпилированном C-коде
2. Данные хранятся компактно (contiguous memory)
3. Используются SIMD-инструкции процессора

---

### 11. PyPy vs CPython

PyPy — это альтернативная реализация Python с JIT-компилятором. Не всегда быстрее, но для определённых паттернов даёт огромный прирост.

```bash
# Установка PyPy
# Windows: choco install pypy3
# Linux: apt install pypy3
# macOS: brew install pypy3

# Запуск скрипта под PyPy
pypy3 my_script.py

# Сравнение времени выполнения
time python my_script.py
time pypy3 my_script.py
```

| Сценарий                     | CPython      | PyPy         | Прирост      |
|------------------------------|--------------|--------------|--------------|
| Чистые вычисления (циклы)    | Медленно     | Быстро (JIT) | 3x–10x       |
| Рекурсия                     | Медленно     | Быстро (JIT) | 2x–5x        |
| C-расширения (NumPy)         | Быстро       | Медленно     | 0.5x–1x      |
| I/O-bound                    | Одинаково    | Одинаково    | 1x           |
| Строковые операции           | Средне       | Быстро       | 2x–3x        |

---

### 12. Сравнение с другими языками

#### Java JIT-оптимизации

Java HotSpot JIT выполняет оптимизации, которые Python-разработчику приходится делать вручную:

| Оптимизация               | Java (автоматически)                  | Python (вручную)                      |
|---------------------------|---------------------------------------|---------------------------------------|
| Инлайнинг вызовов         | JIT встраивает короткие методы        | Кеширование в локальную переменную    |
| Устранение виртуальных вызовов | CHA (Class Hierarchy Analysis)   | Нет аналога                           |
| Escape analysis           | Размещение на стеке вместо кучи       | `__slots__` (приблизительно)          |
| Loop unrolling            | JIT разворачивает циклы               | Нет в CPython; PyPy делает            |
| Dead code elimination     | JIT удаляет мёртвый код               | Нет                                   |
| Intrinsics                | `Math.sin()` → инструкция CPU         | Нет                                   |

#### C++ компиляторные оптимизации

C++ (`-O2`, `-O3`) даёт оптимизации, недоступные Python:

| Оптимизация             | C++                     | Python                        |
|-------------------------|-------------------------|-------------------------------|
| Константное свёртывание | `2+2` → `4` на этапе компиляции | Только peephole optimizer |
| Devirtualization        | LTO + PGO               | Нет                           |
| Векторизация (SIMD)     | `-O3 -march=native`     | Только через NumPy            |
| Управление памятью      | `std::vector`, стек     | Куча для всего                |

#### JavaScript V8

V8 (Chrome, Node.js) выполняет JIT-компиляцию с интересными особенностями:

| Аспект                  | V8 JIT                          | Python                        |
|-------------------------|---------------------------------|-------------------------------|
| Скрытые классы          | Автоматически                   | `__slots__` (вручную)         |
| Инлайн-кеширование      | Автоматически                   | `lru_cache` (вручную)         |
| Деоптимизации           | Могут убить производительность   | Нет; стабильная скорость      |
| GC                      | Орназальный (Orinoco) GC        | Reference counting + generational GC |

---

### 13. Сводная таблица: ✅ Паттерны и ❌ Антипаттерны

| ✅ Паттерн (быстро)                          | ❌ Антипаттерн (медленно)                       |
|----------------------------------------------|-------------------------------------------------|
| `''.join(strings)`                           | `s += x` в цикле                                |
| List comprehension                           | `map(lambda ...)`                               |
| `deque.popleft()`                            | `list.pop(0)`                                   |
| `__slots__` для миллионов объектов           | `__dict__` для миллионов объектов               |
| `lru_cache` для чистых функций               | Рекурсия без мемоизации                         |
| `local = global.attr` в цикле                | `global.attr` в каждой итерации                 |
| `array('i')` / `np.array` для чисел          | `list[int]` для 10M чисел                       |
| `collections.defaultdict`                    | `if key in dict: ... else: ...`                 |
| `dict.get(key, default)`                     | `try: dict[key] except KeyError` в горячем коде |
| `set` для проверки на вхождение              | `list` для поиска (O(n) vs O(1))                |
| `sys.stdin.buffer.read()` для бинарных данных| `sys.stdin.read()` с decode/encode              |
| `functools.partial` для фиксированных аргументов | `lambda` с захватом переменных              |

---

### 14. Стратегия оптимизации: пошаговый план

```text
1. Профилируйте → найдите узкое место (Урок 1)
2. Измерьте baseline → timeit до оптимизации
3. Примените микро-оптимизации из этого урока
4. Измерьте again → timeit после оптимизации
5. Сравните → зафиксируйте прирост
6. Повторите → если прирост недостаточен
7. Если микро-оптимизаций недостаточно:
   7a. NumPy для числовых операций
   7b. PyPy для CPU-bound кода
   7c. C-расширения (Урок 3)
   7d. Параллелизм (Урок 4)
```

> ⚠️ **Правило 3%:** если оптимизация ускоряет функцию, которая занимает 3% времени программы, общий прирост — 3%. Оптимизируйте только горячие пути, которые в совокупности дают >80% времени выполнения.

---

## Практическое задание

### Задача: оптимизация текстового анализатора

Вам дан скрипт, который читает большой текстовый файл, считает частоту слов и выводит топ-100. Скрипт работает медленно. Примените изученные техники для ускорения.

```python
# Файл: word_frequency.py
import sys
from collections import Counter
from pathlib import Path


def count_words_slow(filepath: str) -> list[tuple[str, int]]:
    """Считает частоту слов в файле. Медленная версия."""
    # Чтение всего файла в память
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Очистка и токенизация
    words = text.lower().split()

    # Удаление знаков препинания — медленный способ
    punctuation = {".", ",", "!", "?", ";", ":", "-", "(", ")", "[", "]", "{", "}", '"', "'"}
    clean_words = []
    for word in words:
        clean = ""
        for ch in word:
            if ch not in punctuation:
                clean += ch  # Антипаттерн: += в цикле!
        if clean:
            clean_words.append(clean)

    # Подсчёт частот
    counter = {}
    for word in clean_words:
        if word in counter:
            counter[word] += 1
        else:
            counter[word] = 1

    # Сортировка — получение топ-100
    sorted_words = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    return sorted_words[:100]


def generate_test_file(filepath: str, num_lines: int = 100_000) -> None:
    """Генерирует тестовый файл."""
    import random
    import string

    words_pool = ["python", "optimization", "profile", "benchmark", "performance",
                  "code", "slow", "fast", "memory", "cpu", "loop", "function",
                  "class", "module", "import", "data", "algorithm", "complexity"]

    with open(filepath, "w", encoding="utf-8") as f:
        for _ in range(num_lines):
            line = " ".join(random.choices(words_pool, k=random.randint(5, 20)))
            f.write(line + "\n")


if __name__ == "__main__":
    test_file = "test_text.txt"
    generate_test_file(test_file, num_lines=100_000)

    result = count_words_slow(test_file)
    print(f"Топ-10 слов: {result[:10]}")
```

### Шаги выполнения

1. **Измерьте baseline** с помощью `timeit` или `cProfile`:
   ```bash
   python -m cProfile -s cumulative word_frequency.py
   ```

2. **Примените оптимизации**:
   - Используйте `str.translate()` или `re.sub()` для удаления пунктуации
   - Используйте `collections.Counter` вместо ручного подсчёта
   - Используйте `''.join()` вместо `+=` в цикле
   - Читайте файл построчно, а не целиком
   - Используйте `locale.strxfrm` или `str.lower()` один раз, а не в цикле

3. **Измерьте эффект** каждой оптимизации отдельно и зафиксируйте прирост.

4. **Сравните** с NumPy-версией токенизации (если применимо).

5. **Проверьте на PyPy** и сравните с CPython:
   ```bash
   pypy3 word_frequency_optimized.py
   time python word_frequency_optimized.py
   time pypy3 word_frequency_optimized.py
   ```

### Ожидаемые результаты

- Baseline-отчёт cProfile с указанием горячих функций
- Оптимизированная версия `count_words_fast`
- Таблица сравнения: каждая оптимизация и её эффект
- Итоговый прирост: минимум 3x по времени выполнения
- Сравнение CPython vs PyPy

---

## Дополнительные материалы

### Книги

- **High Performance Python**, Micha Gorelick & Ian Ozsvald — главы 4–7
- **Python Cookbook**, David Beazley & Brian K. Jones — глава 14: Testing, Debugging, and Exceptions
- **Fluent Python**, Luciano Ramalho — глава 19: Concurrency Models

### Инструменты

- [perfplot](https://github.com/nschloe/perfplot) — визуализация бенчмарков с ростом размера данных
- [pyperf](https://github.com/psf/pyperf) — toolkit для стабильных бенчмарков
- [codon](https://github.com/exaloop/codon) — Python-компилятор в нативный код (альтернатива PyPy)
- [Numba](https://numba.pydata.org/) — JIT-компилятор для числового Python

### Онлайн-ресурсы

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips) — официальная вики
- [The Fastest Way to Loop in Python](https://www.youtube.com/watch?v=Qgevy75co8c) — mCoding
- [Write Fast Python](https://www.youtube.com/watch?v=2H4N5g3g7Wk) — Raymond Hettinger
- [Python bytecode and the interpreter](https://www.youtube.com/watch?v=HVUTjJjNK4A) — James Bennett