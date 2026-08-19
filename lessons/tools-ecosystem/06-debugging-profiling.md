---
title: "Отладка и профилирование: pdb, icecream, cProfile, viztracer"
order: 6
tags: ["отладка", "pdb", "cProfile", "профилирование", "логирование"]
prerequisites: "Базовый Python, функции"
objective: "Освоить инструменты отладки и профилирования Python-кода"
---

# Отладка и профилирование: pdb, icecream, cProfile, viztracer

## Введение

### 🎯 Цель урока

Освоить полный арсенал инструментов для поиска и исправления ошибок, а также для измерения и оптимизации производительности Python-кода. От интерактивной отладки через `pdb` до визуального профилирования через `viztracer`.

### 📋 Предпосылки

- Уверенный Python: функции, классы, исключения, декораторы
- Понимание времени выполнения алгоритмов (Big O)
- Базовое знакомство с командной строкой

### Два типа проблем

1. **Код работает неправильно** → отладка (debugging)
2. **Код работает медленно** → профилирование (profiling)

Для каждой проблемы — свой набор инструментов. Но часто они пересекаются: медленный код может быть медленным из-за бага.

---

## Основная часть

### 1. `pdb` — интерактивный отладчик

`pdb` (Python Debugger) — встроенный в Python интерактивный отладчик. Он позволяет останавливать выполнение программы в любой точке, исследовать значения переменных, выполнять код по шагам и менять состояние на лету.

#### Запуск pdb

```bash
# Запустить скрипт под отладчиком
python -m pdb my_script.py

# Или вставить точку останова в код
```

#### Вставка точки останова (breakpoint)

```python
def calculate(x: int, y: int) -> int:
    """Пример функции с точкой останова."""
    result = x * y
    breakpoint()  # Python 3.7+ — аналог import pdb; pdb.set_trace()
    return result + 10

calculate(5, 3)
```

При запуске такого кода выполнение остановится на `breakpoint()`, и вы попадёте в интерактивную сессию:

```
> calculate()
-> return result + 10
(Pdb)
```

#### Основные команды pdb

| Команда | Сокращение | Действие |
|---------|-----------|----------|
| `help` | `h` | Показать справку |
| `list` | `l` | Показать код вокруг текущей строки |
| `where` | `w` | Показать стек вызовов |
| `next` | `n` | Следующая строка (не заходит в функции) |
| `step` | `s` | Шаг внутрь вызываемой функции |
| `continue` | `c` | Продолжить выполнение до следующей точки останова |
| `return` | `r` | Выполнить до возврата из текущей функции |
| `until` | `unt` | Продолжить до строки с номером больше текущего |
| `print` | `p` | Вывести значение выражения |
| `pp` | `pp` | Красиво вывести значение |
| `args` | `a` | Показать аргументы текущей функции |
| `quit` | `q` | Выйти из отладчика |
| `break` | `b` | Установить точку останова |
| `clear` | `cl` | Удалить точку останова |
| `jump` | `j` | Перейти на другую строку |

#### Практический пример отладки

```python
# buggy.py — программа с ошибкой
def find_user(users: list[dict], user_id: int) -> dict | None:
    """Ищет пользователя по ID. ОШИБКА: сравнивает строку с числом!"""
    for user in users:
        if user["id"] == user_id:  # Ошибка: "id" — строка, user_id — int
            return user
    return None

def main() -> None:
    users = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
    ]

    user = find_user(users, 2)
    if user is None:
        print("User not found!")  # Всегда выводится это!
    else:
        print(f"Found: {user['name']}")

if __name__ == "__main__":
    main()
```

Сессия отладки:

```bash
$ python -m pdb buggy.py
> buggy.py(1)<module>()
-> def find_user(users, user_id):
(Pdb) b 5              # Установить точку останова на строке 5
Breakpoint 1 at buggy.py:5
(Pdb) c                 # Продолжить выполнение
> buggy.py(5)find_user()
-> if user["id"] == user_id:
(Pdb) p user["id"]      # Вывести user["id"]
'1'
(Pdb) p user_id          # Вывести user_id
1
(Pdb) p type(user["id"]) # Проверить тип
<class 'str'>
(Pdb) p type(user_id)    # Проверить тип
<class 'int'>
# Ага! '1' != 1 — сравнение строки с числом всегда False
(Pdb) q                  # Выйти
```

#### Условные точки останова

```python
# Точка останова только когда user["id"] == "2"
(Pdb) b 5, user["id"] == "2"

# Точка останова на функции
(Pdb) b find_user

# Просмотр всех точек останова
(Pdb) b
```

#### Посмертная отладка (post-mortem)

```python
import pdb
import sys

def main() -> None:
    try:
        risky_operation()
    except Exception:
        # Вход в pdb в момент исключения
        pdb.post_mortem(sys.exc_info()[2])

def risky_operation() -> None:
    data = {"key": "value"}
    print(data["nonexistent"])  # KeyError!
```

### 2. `breakpoint()` — встроенная точка останова

С Python 3.7 `breakpoint()` — это стандартный способ поставить точку останова. Он использует переменную окружения `PYTHONBREAKPOINT`:

```bash
# Использовать pdb (по умолчанию)
export PYTHONBREAKPOINT=pdb.set_trace

# Использовать ipdb (более удобный pdb с подсветкой)
pip install ipdb
export PYTHONBREAKPOINT=ipdb.set_trace

# Отключить все breakpoint() в продакшене
export PYTHONBREAKPOINT=0
```

```python
def complex_function(data: list[int]) -> int:
    """Функция с несколькими точками останова."""
    result = 0

    for i, value in enumerate(data):
        result += value * (i + 1)
        breakpoint()  # Остановка на каждой итерации

    return result

# В продакшене breakpoint() просто игнорируется
# если PYTHONBREAKPOINT=0
```

### 3. `icecream` — «print-отладка» на стероидах

`icecream` (пакет `icecream`) — это замена `print()` для отладки. Он выводит не только значение, но и само выражение, и контекст.

```bash
pip install icecream
```

```python
from icecream import ic

def calculate_total(prices: list[float], discount: float) -> float:
    """Вычисляет итоговую сумму с учётом скидки."""
    ic(prices, discount)  # Выводит: ic| prices: [10.0, 20.0, 30.0], discount: 0.1

    subtotal = sum(prices)
    ic(subtotal)  # ic| subtotal: 60.0

    discount_amount = subtotal * discount
    ic(discount_amount)  # ic| discount_amount: 6.0

    total = subtotal - discount_amount
    ic(total)  # ic| total: 54.0

    return total

# ic() всегда возвращает переданное значение, поэтому его можно вставлять
# прямо в выражения:
def process(data: list[int]) -> list[int]:
    return [ic(x * 2) for x in data]
    # ic| x * 2: 2
    # ic| x * 2: 4
    # ic| x * 2: 6
```

#### Настройка icecream

```python
from icecream import ic

# Настроить префикс
ic.configureOutput(prefix="DEBUG| ")

# Включить имя файла и строку
ic.configureOutput(includeContext=True)

# Вывод: DEBUG| buggy.py:15 in calculate_total() - subtotal: 60.0

# Отключить весь вывод в продакшене
ic.disable()

# Включить обратно
ic.enable()

# Запись в файл вместо stdout
import sys
ic.configureOutput(outputFunction=lambda msg: print(msg, file=sys.stderr))
```

#### Сравнение `print` и `ic`

```python
# print — нужно вручную форматировать
print(f"prices: {prices}, discount: {discount}")
print(f"subtotal: {subtotal}")
print(f"total: {total}")

# ic — автоматически
ic(prices, discount)
ic(subtotal)
ic(total)
```

### 4. `logging` — промышленное логирование

`print` и `ic` — для разработки. `logging` — для продакшена. Модуль `logging` из стандартной библиотеки поддерживает уровни, форматирование, ротацию и запись в разные источники.

```python
import logging
import sys
from pathlib import Path

# Базовая настройка
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


def process_order(order_id: int, items: list[str]) -> dict:
    """Обрабатывает заказ с полным логированием."""
    logger.info("Processing order %d with %d items", order_id, len(items))
    logger.debug("Order items: %s", items)

    if not items:
        logger.warning("Order %d has no items!", order_id)
        return {"status": "empty", "order_id": order_id}

    try:
        # Бизнес-логика...
        result = {"status": "ok", "order_id": order_id, "count": len(items)}
        logger.info("Order %d processed successfully", order_id)
        return result
    except Exception as e:
        logger.exception("Failed to process order %d", order_id)
        raise
```

#### Уровни логирования

| Уровень | Значение | Когда использовать |
|---------|----------|-------------------|
| `DEBUG` | 10 | Детальная отладочная информация |
| `INFO` | 20 | Нормальная работа программы |
| `WARNING` | 30 | Что-то неожиданное, но программа работает |
| `ERROR` | 40 | Ошибка, которая не остановила программу |
| `CRITICAL` | 50 | Критическая ошибка, программа остановлена |

#### Продвинутая конфигурация

```python
# config/logging_config.py
import logging.config
from pathlib import Path

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": (
                "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d "
                "in %(funcName)s(): %(message)s"
            ),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "myapp": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# Применение конфигурации
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("myapp")
```

### 5. `cProfile` — профилирование CPU

`cProfile` — встроенный профайлер Python. Он показывает, сколько времени тратится на каждую функцию.

```bash
# Запуск скрипта под профайлером
python -m cProfile -o output.prof my_script.py

# Вывод статистики в терминал
python -m cProfile -s cumulative my_script.py
```

```python
# profile_demo.py — код для профилирования
import time
import random


def slow_function(n: int) -> int:
    """Искусственно медленная функция."""
    result = 0
    for i in range(n):
        result += i ** 2
    return result


def fast_function(n: int) -> int:
    """Быстрая функция."""
    return sum(i ** 2 for i in range(n))


def process_data(records: list[dict]) -> list[dict]:
    """Обрабатывает записи (с задержкой для демонстрации)."""
    results = []
    for record in records:
        processed = {
            "id": record["id"],
            "value": slow_function(record["value"]),
            "extra": fast_function(record["value"] // 10),
        }
        time.sleep(0.01)  # Симуляция I/O
        results.append(processed)
    return results


def main() -> None:
    """Главная функция."""
    data = [
        {"id": i, "value": random.randint(100, 1000)}
        for i in range(100)
    ]
    result = process_data(data)
    print(f"Processed {len(result)} records")


if __name__ == "__main__":
    main()
```

```bash
# Запуск профайлера
python -m cProfile -s tottime profile_demo.py

# Вывод:
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#      100    0.852    0.009    0.852    0.009 profile_demo.py:7(slow_function)
#      100    0.001    0.000    0.001    0.000 profile_demo.py:15(fast_function)
#      100    1.003    0.010    1.856    0.019 profile_demo.py:20(process_data)
```

#### pstats — анализ результатов

```python
import pstats
from pstats import SortKey

# Загрузить результаты
p = pstats.Stats("output.prof")

# Топ-10 функций по времени
p.sort_stats(SortKey.CUMULATIVE).print_stats(10)

# Топ-10 по количеству вызовов
p.sort_stats(SortKey.CALLS).print_stats(10)

# Отфильтровать только свои функции
p.sort_stats(SortKey.TIME).print_stats("profile_demo")

# Показать вызывающих и вызываемых
p.print_callers("slow_function")
p.print_callees("process_data")
```

### 6. `snakeviz` — визуализация профайлера

`snakeviz` открывает результаты `cProfile` в браузере в виде интерактивной диаграммы.

```bash
pip install snakeviz

# Запустить профайлер
python -m cProfile -o output.prof my_script.py

# Открыть визуализацию
snakeviz output.prof
```

В браузере откроется страница с двумя представлениями:
- **Sunburst** (солнечная диаграмма) — показывает вложенность вызовов
- **Icicle** (сосулька) — плоское представление call stack

### 7. `viztracer` — трассировка выполнения

`viztracer` записывает выполнение программы и генерирует визуальный отчёт, который можно открыть в браузере (Chrome/Edge) через Perfetto.

```bash
pip install viztracer

# Запись трассировки
viztracer my_script.py

# Открыть отчёт в браузере
vizviewer result.json
```

```python
# viztracer_demo.py
import time
import random
from viztracer import log_sparse


@log_sparse
def slow_database_query(query_id: int) -> list[dict]:
    """Симуляция медленного запроса к БД."""
    time.sleep(random.uniform(0.05, 0.2))
    return [{"id": i, "value": random.random()} for i in range(query_id)]


@log_sparse
def api_call(endpoint: str) -> dict:
    """Симуляция API-запроса."""
    time.sleep(random.uniform(0.1, 0.5))
    return {"status": "ok", "data": random.randint(0, 100)}


def main() -> None:
    for i in range(10):
        data = slow_database_query(i + 1)
        result = api_call(f"/users/{i}")
        print(f"Iteration {i}: {len(data)} records, api={result['data']}")


if __name__ == "__main__":
    main()
```

```bash
viztracer viztracer_demo.py
vizviewer result.json
```

В Perfetto вы увидите временную шкалу выполнения, где каждая функция отображается как горизонтальная полоса. Сразу видно, что `api_call` занимает больше времени, чем `slow_database_query`.

### 8. `line_profiler` — построчное профилирование

`line_profiler` показывает время выполнения **каждой строки** функции, а не только функции целиком.

```bash
pip install line_profiler
```

```python
# line_profile_demo.py
@profile  # Декоратор line_profiler (не требует импорта)
def calculate_metrics(data: list[float]) -> dict[str, float]:
    """Вычисляет статистические метрики."""
    n = len(data)

    mean = sum(data) / n

    # Медленный способ вычисления дисперсии
    variance = 0.0
    for x in data:
        diff = x - mean
        variance += diff * diff
    variance /= n

    # Медиана (сортировка — дорого)
    sorted_data = sorted(data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]

    return {"mean": mean, "variance": variance, "median": median}


def main() -> None:
    import random
    data = [random.gauss(0, 1) for _ in range(100_000)]
    metrics = calculate_metrics(data)
    print(metrics)


if __name__ == "__main__":
    main()
```

```bash
# Запуск с line_profiler
kernprof -l -v line_profile_demo.py

# Вывод:
# Line #  Hits     Time  Per Hit   % Time  Line Contents
# ======================================================
#      4                                        def calculate_metrics(data):
#      5     1      3.0      3.0      0.0          n = len(data)
#      6     1    500.0    500.0      0.3          mean = sum(data) / n
#      7     1      2.0      2.0      0.0
#      8     1      2.0      2.0      0.0          variance = 0.0
#      9 100001  50000.0      0.5     25.0          for x in data:
#     10 100000  60000.0      0.6     30.0              diff = x - mean
#     11 100000  50000.0      0.5     25.0              variance += diff * diff
#     12     1      1.0      1.0      0.0          variance /= n
```

### 9. `memory_profiler` — профилирование памяти

```bash
pip install memory_profiler
```

```python
# memory_profile_demo.py
@profile
def create_large_lists() -> tuple[list[int], list[str]]:
    """Создаёт большие списки и отслеживает память."""
    # 1 миллион целых чисел
    numbers = list(range(1_000_000))

    # 1 миллион строк (гораздо больше памяти!)
    strings = [f"item_{i}" for i in range(1_000_000)]

    return numbers, strings


@profile
def memory_leak_example() -> list[object]:
    """Пример утечки памяти (глобальный кэш)."""
    cache = []
    for i in range(100_000):
        cache.append({"id": i, "data": "x" * 1000})
    return cache


if __name__ == "__main__":
    create_large_lists()
    memory_leak_example()
```

```bash
python -m memory_profiler memory_profile_demo.py
```

### 10. Сравнение с экосистемами других языков

#### C++: gdb / lldb

| Аспект | Python (pdb) | C++ (gdb/lldb) |
|--------|-------------|----------------|
| Уровень отладки | Исходный код Python | Машинный код + исходный C++ |
| Breakpoint | `breakpoint()` / `pdb.set_trace()` | `break <file>:<line>` |
| Стек вызовов | `where` / `bt` | `bt` / `backtrace` |
| Интерактивность | Высокая (REPL) | Средняя |
| Сложность | Низкая | Высокая |

```bash
# gdb (C++)
gdb ./myprogram
(gdb) break main.cpp:42
(gdb) run
(gdb) print variable
(gdb) backtrace
```

#### JavaScript: Chrome DevTools / Node.js debugger

| Аспект | Python | JavaScript |
|--------|--------|------------|
| Отладчик | pdb / ipdb / VS Code | Chrome DevTools / Node --inspect |
| Print-отладка | icecream | console.log |
| Профайлер | cProfile | Chrome DevTools Performance |
| Логирование | logging | winston / pino |
| Визуализация | snakeviz / viztracer | Chrome flame charts |

```bash
# Node.js отладка
node --inspect-brk my_script.js
# Открыть chrome://inspect
```

#### Java: JProfiler / VisualVM

| Аспект | Python | Java |
|--------|--------|------|
| CPU профайлер | cProfile | JProfiler / VisualVM |
| Memory профайлер | memory_profiler | Eclipse MAT |
| Визуализация | snakeviz / viztracer | JProfiler UI |
| Встроенный | cProfile | JVM Flight Recorder |

### 11. ✅ Идиоматичное использование

```python
# ✅ ПРАВИЛЬНО: использовать breakpoint() вместо pdb.set_trace()
def process(x: int) -> int:
    result = x * 2
    breakpoint()  # Современный способ
    return result

# ✅ ПРАВИЛЬНО: использовать logging вместо print в продакшене
import logging
logger = logging.getLogger(__name__)
logger.info("Processing data: %d items", len(data))

# ✅ ПРАВИЛЬНО: профилировать до оптимизации
# python -m cProfile -o output.prof script.py
# snakeviz output.prof

# ✅ ПРАВИЛЬНО: использовать структурное логирование
logger.info("Order processed", extra={
    "order_id": 123,
    "status": "ok",
    "duration_ms": 45,
})

# ✅ ПРАВИЛЬНО: использовать декораторы для профайлинга
@profile  # line_profiler
def critical_function() -> None: ...
```

### 12. ❌ Антипаттерны

```python
# ❌ НЕПРАВИЛЬНО: оставлять breakpoint() в production-коде
def calculate(x: int) -> int:
    breakpoint()  # Забудете убрать — программа зависнет в продакшене!
    return x * 2

# ❌ НЕПРАВИЛЬНО: использовать print() для отладки в продакшене
print("DEBUG: value =", value)  # Засоряет stdout, нет временных меток

# ❌ НЕПРАВИЛЬНО: оптимизировать без профилирования
# "Мне кажется, это медленно" — недостаточное основание для оптимизации

# ❌ НЕПРАВИЛЬНО: игнорировать уровни логирования
logger.info("Something went terribly wrong!")  # Должно быть logger.error

# ❌ НЕПРАВИЛЬНО: логировать чувствительные данные
logger.info("User %s logged in with password %s", username, password)
# Пароль в логах — катастрофа безопасности!

# ❌ НЕПРАВИЛЬНО: использовать bare except без логирования
try:
    risky_operation()
except:  # noqa: E722
    pass  # Ошибка проглочена, в логах пусто
```

### 13. Интеграция с IDE (VS Code)

```json
// .vscode/launch.json — конфигурация отладки
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false
        },
        {
            "name": "Python: Debug with args",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "args": ["--verbose", "--output", "result.json"],
            "console": "integratedTerminal"
        }
    ]
}
```

---

## Практическое задание

### Задача: найти и исправить баги и узкие места

1. **Создайте проект**:

```bash
mkdir debug-workshop
cd debug-workshop
python -m venv .venv
source .venv/bin/activate
pip install icecream snakeviz line_profiler memory_profiler
```

2. **Создайте файл `buggy_slow.py`** со встроенными багами и проблемами производительности:

```python
"""Модуль с багами и проблемами производительности — найдите и исправьте."""

import time
from dataclasses import dataclass


@dataclass
class Product:
    name: str
    price: float
    category: str


class InventoryManager:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def get_total_value(self):
        """БАГ: неправильно считает сумму (должен умножать на количество)."""
        total = 0
        for p in self.products:
            total = total + p.price  # БАГ: не умножает на количество!
        return total

    def find_by_category(self, category):
        """ПРОБЛЕМА: O(n) поиск без индекса."""
        results = []
        for p in self.products:
            if p.category == category:
                results.append(p)
        return results

    def get_most_expensive(self):
        """БАГ: не обрабатывает пустой список."""
        most_expensive = self.products[0]  # IndexError при пустом списке!
        for p in self.products:
            if p.price > most_expensive.price:
                most_expensive = p
        return most_expensive

    def calculate_discounts(self, discount_rate):
        """ПРОБЛЕМА: медленная операция с ненужным временным списком."""
        discounted = []
        for p in self.products:
            time.sleep(0.001)  # Искусственная задержка
            discounted.append(
                {"name": p.name, "new_price": p.price * (1 - discount_rate)}
            )
        return discounted


def generate_large_inventory(size: int) -> InventoryManager:
    """Генерирует большой инвентарь для профилирования."""
    import random

    categories = ["electronics", "books", "clothing", "food", "toys"]
    manager = InventoryManager()

    for i in range(size):
        product = Product(
            name=f"Product_{i}",
            price=random.uniform(1.0, 1000.0),
            category=random.choice(categories),
        )
        manager.add_product(product)

    return manager


def main():
    print("Создаём инвентарь...")
    inventory = generate_large_inventory(10_000)

    print("Считаем общую стоимость...")
    total = inventory.get_total_value()
    print(f"Total value: {total:.2f}")

    print("Ищем по категории...")
    electronics = inventory.find_by_category("electronics")
    print(f"Found {len(electronics)} electronics")

    print("Ищем самый дорогой...")
    try:
        expensive = inventory.get_most_expensive()
        print(f"Most expensive: {expensive.name} at ${expensive.price:.2f}")
    except IndexError:
        print("Inventory is empty!")

    print("Рассчитываем скидки...")
    start = time.time()
    discounted = inventory.calculate_discounts(0.15)
    elapsed = time.time() - start
    print(f"Calculated {len(discounted)} discounts in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
```

3. **Используйте pdb/breakpoint() для отладки**:

```bash
# Запустите под отладчиком и найдите баги
python -m pdb buggy_slow.py
```

4. **Используйте icecream для трассировки**:

Добавьте `ic()` в стратегические места и отследите поток данных.

5. **Запрофилируйте через cProfile и snakeviz**:

```bash
python -m cProfile -o output.prof buggy_slow.py
snakeviz output.prof
```

6. **Используйте line_profiler** для построчного анализа:

```bash
kernprof -l -v buggy_slow.py
```

7. **Исправьте ВСЕ баги** и оптимизируйте медленные участки:

```python
# Исправленная версия
class InventoryManager:
    def __init__(self) -> None:
        self.products: list[Product] = []
        self._category_index: dict[str, list[Product]] = {}  # Индекс для O(1)

    def add_product(self, product: Product) -> None:
        self.products.append(product)
        # Обновляем индекс
        self._category_index.setdefault(product.category, []).append(product)

    def get_total_value(self) -> float:
        return sum(p.price for p in self.products)

    def find_by_category(self, category: str) -> list[Product]:
        return self._category_index.get(category, [])

    def get_most_expensive(self) -> Product | None:
        if not self.products:
            return None
        return max(self.products, key=lambda p: p.price)

    def calculate_discounts(self, discount_rate: float) -> list[dict]:
        factor = 1 - discount_rate
        return [
            {"name": p.name, "new_price": p.price * factor}
            for p in self.products
        ]  # Без time.sleep!
```

8. **Проверьте исправленную версию** — она должна работать корректно и быстро.

---

## Дополнительные материалы

### 📚 Официальная документация

- [pdb — The Python Debugger](https://docs.python.org/3/library/pdb.html) — официальная документация
- [logging — Logging facility for Python](https://docs.python.org/3/library/logging.html) — модуль logging
- [cProfile — The Python Profilers](https://docs.python.org/3/library/profile.html) — встроенные профайлеры
- [breakpoint() — PEP 553](https://peps.python.org/pep-0553/) — встроенная функция breakpoint()

### 🎥 Видео и статьи

- [Python Debugging with pdb (Real Python)](https://realpython.com/python-debugging-pdb/) — гид по pdb
- [Profiling Python Code (Real Python)](https://realpython.com/python-profiling/) — обзор инструментов профилирования
- [Logging in Python (Real Python)](https://realpython.com/python-logging/) — полный гид по logging

### 🛠 Инструменты

- [ipdb](https://github.com/gotcha/ipdb) — pdb с IPython-подсветкой и автодополнением
- [icecream](https://github.com/gruns/icecream) — замена print для отладки
- [snakeviz](https://jiffyclub.github.io/snakeviz/) — визуализация профилей
- [viztracer](https://github.com/gaogaotiantian/viztracer) — трассировка с визуализацией
- [line_profiler](https://github.com/pyutils/line_profiler) — построчное профилирование
- [memory_profiler](https://github.com/pythonprofilers/memory_profiler) — профилирование памяти
- [py-spy](https://github.com/benfred/py-spy) — семплирующий профайлер для production
- [memray](https://github.com/bloomberg/memray) — профилировщик памяти от Bloomberg

### 💡 Ключевые выводы

1. **pdb / breakpoint()** — для интерактивной отладки багов
2. **icecream** — быстрая замена print для трассировки
3. **logging** — промышленное логирование для продакшена
4. **cProfile + snakeviz** — для поиска узких мест по CPU
5. **line_profiler** — когда нужно увидеть время каждой строки
6. **memory_profiler** — для поиска утечек памяти
7. **viztracer** — визуальная трассировка всего выполнения
8. **Не оптимизируйте без профилирования** — измеряйте, прежде чем менять
9. **Убирайте breakpoint() и ic() перед деплоем** — используйте PYTHONBREAKPOINT=0