---
title: "Профилирование Python: cProfile, line_profiler, memory_profiler, py-spy"
order: 1
tags: ["профилирование", "cProfile", "line_profiler", "memory", "py-spy"]
prerequisites: "Функции, декораторы, командная строка"
objective: "Освоить инструменты профилирования для поиска узких мест в Python-коде"
---

# Профилирование Python: cProfile, line_profiler, memory_profiler, py-spy

## Введение

> "Вы не можете оптимизировать то, что не измеряете." — распространённая мантра performance-инженеров.

Профилирование — это **первый и обязательный** шаг любой оптимизации. Без профилировщика вы гадаете. С профилировщиком вы получаете точную карту того, где ваш код тратит время и память. В мире Python доступно несколько мощных инструментов, каждый из которых решает свою задачу: от высокоуровневого анализа вызовов до построчного разбора и отслеживания аллокаций.

В этом уроке мы разберём:

- **cProfile** — встроенный детерминированный профилировщик;
- **pstats** и **SnakeViz** — анализ и визуализация статистики;
- **line_profiler** — построчное профилирование;
- **memory_profiler** — отслеживание потребления памяти;
- **py-spy** — семплирующий профилировщик для production;
- **tracemalloc** — встроенный трейсер аллокаций памяти.

### 🎯 Цель урока

Освоить инструменты профилирования для поиска узких мест в Python-коде.

### 📋 Предпосылки

Функции, декораторы, командная строка.

---

## Основная часть

### 1. cProfile: встроенный детерминированный профилировщик

`cProfile` — это профилировщик на C, входящий в стандартную библиотеку Python. Он отслеживает **каждый вызов функции** и записывает: количество вызовов, общее время, собственное время (без учёта вложенных вызовов), время на вызов.

#### 1.1 Запуск из командной строки

```bash
# Профилирование скрипта
python -m cProfile -s cumulative my_script.py

# Сохранение статистики в файл для дальнейшего анализа
python -m cProfile -o output.prof my_script.py
```

Ключи сортировки (`-s`):

| Ключ          | Описание                          |
|---------------|-----------------------------------|
| `calls`       | Количество вызовов                |
| `cumulative`  | Общее время (с учётом вложенных)  |
| `time`        | Собственное время (tottime)       |
| `name`        | Имя функции (лексикографически)   |
| `ncalls`      | Количество вызовов                |
| `filename`    | Имя файла + номер строки          |

#### 1.2 Программный запуск через `Profile`

```python
import cProfile
import pstats
from io import StringIO


def fibonacci(n: int) -> int:
    """Наивная рекурсивная реализация — намеренно медленная."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def main() -> int:
    return fibonacci(30)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    result = main()
    profiler.disable()

    # Вывод статистики с сортировкой по cumulative time
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(20)  # Топ-20 функций
    print(stream.getvalue())
    print(f"Результат: {result}")
```

Пример вывода:

```
         2692539 function calls (3 primitive calls) in 0.891 seconds

   Ordered by: cumulative time
   List reduced from 4 to 4 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.891    0.891 script.py:13(main)
2692537/1    0.891    0.000    0.891    0.891 script.py:6(fibonacci)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.exec}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

**Что мы видим:** `fibonacci` вызвана 2 692 537 раз — это и есть узкое место. Наивная рекурсия без мемоизации экспоненциальна по времени.

#### 1.3 Контекстный менеджер для профилирования

```python
import cProfile
import pstats
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def profile_block(sort_by: str = "cumulative", limit: int = 20):
    """Контекстный менеджер для профилирования блока кода."""
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield
    finally:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats(sort_by)
        stats.print_stats(limit)


def expensive_operation() -> list[int]:
    return [i ** 2 for i in range(10_000_000)]


with profile_block(sort_by="time"):
    expensive_operation()
```

#### 1.4 Модуль pstats: глубокий анализ статистики

`pstats` позволяет анализировать сохранённые `.prof`-файлы интерактивно:

```python
import pstats

# Загрузка ранее сохранённого профиля
stats = pstats.Stats("output.prof")

# Топ-10 по собственному времени
stats.sort_stats("time").print_stats(10)

# Фильтрация по имени функции
stats.sort_stats("cumulative").print_stats("fibonacci")

# Только функции из конкретного файла
stats.sort_stats("time").print_stats("my_module.py")

# Обратная сортировка (по возрастанию)
stats.sort_stats("time").print_stats(-10)

# Получить список вызывающих (callers) для функции
stats.print_callers("fibonacci")

# Получить список вызываемых (callees) для функции
stats.print_callees("expensive_operation")
```

#### 1.5 SnakeViz: визуализация

SnakeViz — это веб-интерфейс для `.prof`-файлов, который строит **sunburst-диаграмму** и **icicle-график**:

```bash
# Установка
pip install snakeviz

# Запуск
snakeviz output.prof
```

SnakeViz открывает браузер с интерактивной визуализацией. Sunburst-диаграмма показывает иерархию вызовов: внутренние кольца — родительские функции, внешние — дочерние. Площадь сегмента пропорциональна времени выполнения. Это самый быстрый способ найти "горячие" функции в большом проекте.

---

### 2. line_profiler: построчное профилирование

`cProfile` показывает время на уровне функций. Но что если внутри функции 50 строк, и вы хотите знать, какая именно строка тормозит? Для этого нужен `line_profiler`.

#### 2.1 Установка и использование

```bash
pip install line_profiler
```

Декоратор `@profile`:

```python
# Файл: slow_parser.py
import re


@profile
def parse_logs(log_lines: list[str]) -> list[dict]:
    """Парсинг строк лога — найдите узкое место."""
    results = []
    pattern = re.compile(
        r"^(?P<timestamp>\S+)\s+(?P<level>\w+)\s+(?P<message>.+)$"
    )

    for line in log_lines:
        match = pattern.match(line)
        if match:
            # Извлечение групп
            entry = {
                "timestamp": match.group("timestamp"),
                "level": match.group("level"),
                "message": match.group("message").strip(),
            }
            # Дополнительная обработка
            entry["length"] = len(entry["message"])
            entry["has_error"] = "ERROR" in entry["message"].upper()
            results.append(entry)

    return results
```

Запуск:

```bash
kernprof -l -v slow_parser.py
```

Флаги:
- `-l` — построчное профилирование (line-by-line)
- `-v` — вывод результатов сразу после выполнения

Пример вывода:

```
Timer unit: 1e-06 s

Total time: 2.14567 s
File: slow_parser.py
Function: parse_logs at line 5

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     5                                           @profile
     6                                           def parse_logs(log_lines):
     7         1          3.0      3.0      0.0      results = []
     8         1         45.0     45.0      0.0      pattern = re.compile(...)
     9     10001       2345.0      0.2      0.1      for line in log_lines:
    10     10000     580234.0     58.0     27.0          match = pattern.match(line)
    11      8000      12345.0      1.5      0.6          if match:
    12      8000      89012.0     11.1      4.1              entry = { ... }
    13      8000    1234567.0    154.3     57.5              entry["length"] = len(...)
    14      8000     210987.0     26.4      9.8              entry["has_error"] = ...
    15      8000      15678.0      2.0      0.7              results.append(entry)
    16         1          1.0      1.0      0.0      return results
```

**Вывод:** строка `entry["length"] = ...` занимает 57.5% времени — это неожиданно. Причина: лишний обход строки внутри цикла.

#### 2.2 Профилирование в IPython / Jupyter

```python
%load_ext line_profiler

# Профилирование одной функции
%lprun -f parse_logs parse_logs(large_log_dataset)
```

---

### 3. memory_profiler: отслеживание потребления памяти

Время — не единственный ресурс. Память тоже важна, особенно в long-running сервисах и при обработке больших данных.

#### 3.1 Установка и базовое использование

```bash
pip install memory_profiler
```

```python
# Файл: memory_test.py
from memory_profiler import profile


@profile
def build_large_structure(n: int) -> list[dict]:
    """Создаёт большой список словарей — отслеживаем память."""
    data = []
    for i in range(n):
        record = {
            "id": i,
            "name": f"user_{i:08d}",
            "tags": [f"tag_{j}" for j in range(i % 100)],
        }
        data.append(record)
    return data


@profile
def process_with_generator(n: int):
    """Генераторная версия — сравниваем память."""
    for i in range(n):
        yield {
            "id": i,
            "name": f"user_{i:08d}",
            "tags": [f"tag_{j}" for j in range(i % 100)],
        }


if __name__ == "__main__":
    result = build_large_structure(100_000)
    # Принудительно материализуем генератор
    # list(process_with_generator(100_000))
```

```bash
python -m memory_profiler memory_test.py
```

Пример вывода:

```
Line #    Mem usage    Increment   Line Contents
================================================
     7     39.2 MiB     39.2 MiB   @profile
     8                             def build_large_structure(n):
     9     39.2 MiB      0.0 MiB       data = []
    10     78.5 MiB     39.3 MiB       for i in range(n):
    ...
```

#### 3.2 Построчный мониторинг памяти

```python
from memory_profiler import memory_usage


def my_function():
    data = [0] * 10_000_000  # ~80 MB для списка int
    return sum(data)


# Измерение пикового использования памяти во время вызова
usage = memory_usage((my_function,), interval=0.1)
print(f"Пиковое потребление: {max(usage):.1f} MiB")
print(f"Среднее потребление: {sum(usage) / len(usage):.1f} MiB")
```

#### 3.3 mprof: график потребления памяти во времени

```bash
# Запуск с профилированием памяти
mprof run my_script.py

# Построение графика
mprof plot

# Просмотр пиков
mprof peak
```

Это особенно полезно для поиска **утечек памяти** в долгоживущих процессах.

---

### 4. py-spy: семплирующий профилировщик для production

`cProfile` и `line_profiler` — это **детерминированные** профилировщики. Они добавляют накладные расходы (иногда до 10x замедления) и не подходят для production. `py-spy` решает эту проблему: он работает как **семплирующий** (sampling) профилировщик, подключаясь к уже работающему процессу Python.

#### 4.1 Установка

```bash
pip install py-spy
```

#### 4.2 Профилирование работающего процесса

```bash
# Найти PID процесса Python
ps aux | grep python

# Подключиться и снять профиль (top-like интерфейс)
py-spy top --pid 12345

# Записать flame-граф в SVG
py-spy record -o profile.svg --pid 12345

# Дамп текущего стека (без остановки процесса)
py-spy dump --pid 12345
```

#### 4.3 Flame-графы: чтение и интерпретация

Flame-граф — это визуализация стека вызовов, где:

- **Ось X** — алфавитный порядок имён функций (не время!)
- **Ось Y** — глубина стека
- **Ширина блока** — доля семплов, в которых функция присутствовала
- **Цвет** — обычно случаен, иногда кодирует тип (Python / C / системный)

"Горячие" функции — это широкие блоки наверху стека. Именно они потребляют CPU.

#### 4.4 Сравнение подходов: детерминированный vs семплирующий

| Характеристика            | cProfile (детерминированный) | py-spy (семплирующий)     |
|---------------------------|-------------------------------|----------------------------|
| Принцип работы            | Перехватывает каждый вызов    | Снимает стек N раз/сек     |
| Накладные расходы         | Высокие (2x–10x замедление)   | Низкие (1–3%)              |
| Production-safe           | ❌ Нет                         | ✅ Да                       |
| Видит C-расширения        | ❌ Нет                         | ✅ Да (нативные фреймы)     |
| Точность                  | Абсолютная (каждый вызов)     | Статистическая             |
| Подключение к процессу    | Только при старте             | В любой момент             |
| Гранулярность             | Функция                       | Функция / строка (Cython)  |

---

### 5. tracemalloc: встроенный трейсер аллокаций памяти

Начиная с Python 3.4, в стандартной библиотеке есть `tracemalloc` — модуль для отслеживания аллокаций памяти с указанием точного файла и строки.

```python
import tracemalloc


def memory_leak_simulation() -> list[bytes]:
    """Симуляция утечки: накопление данных без очистки."""
    tracemalloc.start()

    snapshot1 = tracemalloc.take_snapshot()
    buffers = []
    for i in range(1000):
        buffers.append(b"x" * 1024 * 1024)  # 1 MB каждая итерация
    snapshot2 = tracemalloc.take_snapshot()

    # Сравнение снапшотов: какие аллокации появились?
    top_stats = snapshot2.compare_to(snapshot1, "lineno")

    print("Топ-10 новых аллокаций:")
    for stat in top_stats[:10]:
        print(stat)

    tracemalloc.stop()
    return buffers


def show_top_memory_consumers() -> None:
    """Показать текущие топ-потребители памяти."""
    tracemalloc.start()

    # Создаём нагрузку
    data = {i: [j for j in range(1000)] for i in range(10000)}
    snapshot = tracemalloc.take_snapshot()

    top_stats = snapshot.statistics("lineno")
    print("\nТоп-10 по потреблению памяти:")
    for stat in top_stats[:10]:
        print(stat)

    tracemalloc.stop()


if __name__ == "__main__":
    memory_leak_simulation()
    show_top_memory_consumers()
```

Пример вывода:

```
Топ-10 новых аллокаций:
memory_leak.py:10: size=1000 MiB (+1000 MiB), count=1000 (+1000), average=1.0 MiB
...
```

`tracemalloc` незаменим при отладке утечек памяти в production-сервисах: он показывает не только объём, но и **точное место** в коде, где была выделена память.

---

### 6. Классификация узких мест

Прежде чем выбирать инструмент, классифицируйте проблему:

#### 6.1 CPU-bound vs I/O-bound

| Тип                | Признак                                      | Инструмент             |
|--------------------|----------------------------------------------|------------------------|
| **CPU-bound**      | `python` процесс на 100% CPU                 | cProfile, py-spy       |
| **I/O-bound**      | Низкий CPU, много ожидания                   | Кастомное логирование  |
| **Memory-bound**   | Высокий RSS, частые сборки мусора            | memory_profiler, tracemalloc |
| **Call-overhead**  | Много мелких вызовов функций                 | cProfile (ncalls)      |

#### 6.2 Частые источники проблем в Python

| Проблема                              | Инструмент для диагностики     |
|---------------------------------------|--------------------------------|
| Рекурсия без мемоизации               | cProfile (ncalls)              |
| Конкатенация строк в цикле (`s +=`)  | line_profiler                  |
| Создание объектов в горячем цикле     | memory_profiler                |
| Избыточные атрибутные доступы в цикле | line_profiler                  |
| Повторные вычисления                  | cProfile + ручной анализ       |
| Утечки памяти (накопление ссылок)     | tracemalloc, mprof             |
| GIL-контеншен в потоках               | py-spy (нативные фреймы)       |

---

### 7. Сравнение с другими языками

#### 7.1 Java: JProfiler, VisualVM, async-profiler

| Аспект                | Python                           | Java                                  |
|-----------------------|----------------------------------|---------------------------------------|
| **Встроенный проф.**  | cProfile (детерминированный)     | JFR (Java Flight Recorder) — production-safe |
| **Продакшен-проф.**   | py-spy                           | async-profiler (семплирующий)         |
| **Визуализация**      | SnakeViz                         | JProfiler, VisualVM, JMC              |
| **Память**            | memory_profiler, tracemalloc     | Eclipse MAT, JFR heap dump            |
| **Just-in-time**      | Нет (CPython — интерпретатор)    | JIT-компиляция: C1/C2, GraalVM        |
| **Накладные расходы** | Высокие у cProfile               | Низкие у JFR (<2%)                    |

Java имеет преимущество: JIT-компилятор выполняет инлайнинг вызовов, что может сделать профиль менее интуитивным. Python же интерпретируется построчно, и профиль точно отражает исходный код.

#### 7.2 C++: perf, gprof, Valgrind

| Аспект                | Python                           | C++                                   |
|-----------------------|----------------------------------|---------------------------------------|
| **Семплирующий проф.**| py-spy                           | `perf` (Linux), Instruments (macOS)   |
| **Инструментация**    | cProfile                         | gprof, Valgrind (callgrind)           |
| **Память**            | memory_profiler                  | Valgrind (memcheck, massif)           |
| **Уровень**           | Строки Python                    | Строки исходного кода → ассемблер     |
| **Оптимизации**       | Нет                              | Компилятор: -O2/-O3, LTO, PGO         |

C++ `perf` работает на уровне процессорных счётчиков (cache misses, branch mispredictions) — это гораздо глубже, чем любой Python-профилировщик.

#### 7.3 JavaScript (V8): Chrome DevTools

| Аспект                | Python                           | JavaScript (V8)                       |
|-----------------------|----------------------------------|---------------------------------------|
| **Семплирующий проф.**| py-spy                           | Chrome DevTools Performance tab       |
| **Память**            | memory_profiler                  | Heap snapshot, allocation timeline    |
| **Production**        | py-spy                           | `--inspect` + DevTools, Clinic.js     |
| **JIT-эффекты**       | Нет                              | Деоптимизации, inline caching         |

V8-специфичные проблемы: деоптимизации (deopts), скрытые классы (hidden classes), инлайн-кеширование. Python-разработчику не нужно о них думать, но V8 добавляет сложность профилирования.

---

### 8. Практический workflow профилирования

Рекомендуемый порядок действий при поиске узкого места:

```text
1. cProfile → найти "горячие" функции по cumulative time
2. SnakeViz → визуально оценить иерархию вызовов
3. line_profiler → внутри горячей функции найти конкретную строку
4. memory_profiler → если есть подозрение на проблемы с памятью
5. tracemalloc → если есть подозрение на утечку памяти
6. py-spy → для production или для анализа GIL-контеншена
```

---

## Практическое задание

### Задача: профилирование JSON-парсера

Вам дан скрипт, который читает большой JSON-файл и строит агрегированную статистику. Скрипт работает медленно. Ваша задача — найти узкие места и предложить оптимизации.

```python
# Файл: json_parser.py
import json
from pathlib import Path


def load_and_aggregate(filepath: str) -> dict:
    """Читает JSON-файл с транзакциями и агрегирует по категориям."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    categories: dict[str, float] = {}
    for transaction in data["transactions"]:
        cat = transaction["category"]
        amount = transaction["amount"]
        if cat in categories:
            categories[cat] += amount
        else:
            categories[cat] = amount

    # Добавляем вычисляемое поле
    for cat in categories:
        categories[cat] = round(categories[cat], 2)

    return categories


def generate_test_data(n: int) -> None:
    """Генерирует тестовый JSON-файл с n транзакциями."""
    import random
    import string

    categories = ["food", "transport", "housing", "entertainment", "health"]
    transactions = []
    for _ in range(n):
        transactions.append({
            "id": "".join(random.choices(string.ascii_letters, k=10)),
            "category": random.choice(categories),
            "amount": round(random.uniform(1, 1000), 2),
            "timestamp": "2024-01-01T00:00:00Z",
            "description": " ".join(
                random.choices(string.ascii_lowercase, k=random.randint(3, 20))
            ),
        })

    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump({"transactions": transactions}, f)


if __name__ == "__main__":
    generate_test_data(100_000)

    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()
    result = load_and_aggregate("test_data.json")
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)

    # Сохранить для SnakeViz
    stats.dump_stats("json_parser.prof")
    print(f"Результат: {len(result)} категорий")
```

### Шаги выполнения

1. **Запустите скрипт** и проанализируйте вывод `cProfile`. Какая функция занимает больше всего времени?

2. **Визуализируйте** профиль через SnakeViz:
   ```bash
   snakeviz json_parser.prof
   ```

3. **Примените line_profiler** к функции `load_and_aggregate`:
   ```bash
   # Добавьте декоратор @profile и запустите
   kernprof -l -v json_parser.py
   ```

4. **Измерьте память** с помощью `memory_profiler`. Сколько памяти потребляет `json.load()` при чтении 100 000 записей?

5. **Предложите оптимизации** на основе полученных данных. Например:
   - Использование `collections.defaultdict(float)` вместо проверки `if cat in categories`
   - Итеративная потоковая обработка вместо `json.load()` всего файла
   - Использование `orjson` для быстрого парсинга

6. **Измерьте эффект** каждой оптимизации: сравните cProfile-отчёты до и после.

### Ожидаемые результаты

- Отчёт о профилировании: топ-5 функций по времени
- Flame-граф из SnakeViz (скриншот или описание)
- Построчный профиль `load_and_aggregate`: какая строка самая медленная
- Отчёт о потреблении памяти: пиковое значение и основная аллокация
- Оптимизированная версия с улучшением не менее чем в 2x по времени

---

## Дополнительные материалы

### Книги

- **High Performance Python**, Micha Gorelick & Ian Ozsvald — главы 1–3 о profiling и benchmarking
- **Python Performance Tuning**, Gabriele Lanaro — глава о профилировании
- **Effective Python**, Brett Slatkin — Item 59: Use `tracemalloc` to Understand Memory Usage

### Инструменты

- [SnakeViz](https://jiffyclub.github.io/snakeviz/) — визуализация cProfile
- [py-spy](https://github.com/benfred/py-spy) — семплирующий профилировщик
- [pyinstrument](https://github.com/joerick/pyinstrument) — альтернативный статистический профилировщик
- [Austin](https://github.com/P403n1x87/austin) — семплирующий профилировщик с поддержкой flame-графов
- [scalene](https://github.com/plasma-umass/scalene) — высокопроизводительный профайлер CPU + памяти + GPU
- [filprofiler](https://pypi.org/project/filprofiler/) — профилировщик памяти на основе системных вызовов

### Онлайн-ресурсы

- [The Python Profilers](https://docs.python.org/3/library/profile.html) — официальная документация
- [tracemalloc documentation](https://docs.python.org/3/library/tracemalloc.html)
- [Brendan Gregg's Flame Graphs](https://www.brendangregg.com/flamegraphs.html) — теория flame-графов
- [PyCon talk: "Profiling Python" by Dustin Ingram](https://www.youtube.com/watch?v=mxjI2M7ZvMY)

### Сравнительная таблица инструментов

| Инструмент       | Тип              | Накладные расходы | Production | Строки | Память | Визуализация |
|------------------|------------------|--------------------|------------|--------|--------|--------------|
| cProfile         | Детерминированный| Высокие (2x–10x)   | ❌          | ❌      | ❌      | SnakeViz     |
| line_profiler    | Детерминированный| Очень высокие      | ❌          | ✅      | ❌      | Нет          |
| memory_profiler  | Детерминированный| Средние            | ❌          | ✅      | ✅      | mprof plot   |
| py-spy           | Семплирующий     | Низкие (1–3%)      | ✅          | ❌      | ❌      | Flame-граф   |
| tracemalloc      | Трейсинг         | Средние            | ⚠️ (с осторожностью) | ✅ | ✅      | Нет          |
| scalene          | Семплирующий     | Низкие             | ✅          | ✅      | ✅      | HTML-отчёт   |