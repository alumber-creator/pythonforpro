---
title: "Что нового в Python 3.12 и 3.13: обзор для профессионалов"
date: "2025-03-15"
author: "Команда Python for Professionals"
tags: ["python", "python-3.12", "python-3.13", "новые-возможности"]
summary: "Обзор ключевых нововведений Python 3.12 и 3.13: улучшенная обработка ошибок, новые возможности f-строк, JIT-компилятор, улучшения asyncio и многое другое."
---

## Python 3.12: что изменилось

Python 3.12 вышел в октябре 2024 и принёс ряд значительных улучшений. Вот что важно знать профессионалу.

### 1. Улучшенные сообщения об ошибках

Python 3.12 продолжает тренд на улучшение сообщений об ошибках, начатый в 3.10 и 3.11. Теперь интерпретатор ещё точнее указывает на проблему:

```python
# Python 3.11 и ранее:
# NameError: name 'x' is not defined

# Python 3.12:
# NameError: name 'x' is not defined. Did you mean: 'y'?
```

Особенно впечатляет обработка ошибок импорта:

```python
# Python 3.12
from collections import ordereddict
# ImportError: cannot import name 'ordereddict' from 'collections'.
# Did you mean: 'OrderedDict'?
```

### 2. F-строки: больше никаких ограничений

Python 3.12 снимает многие ограничения на f-строки, которые существовали со времён Python 3.6:

```python
# Теперь можно использовать кавычки внутри f-строк без конфликтов
text = f"Словарь: { {"key": "value"} }"

# Многострочные f-строки стали проще
msg = f"""
Привет, {name}!
Твой баланс: {balance:.2f}
"""

# Повторное использование кавычек внутри выражений
result = f"Результат: {data["key"]}"
```

### 3. Новый синтаксис для типов-параметров (PEP 695)

```python
# Старый способ (Python 3.11-)
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Новый способ (Python 3.12+)
class Stack[T]:
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...
```

Это делает generic-код значительно чище и ближе к TypeScript/Java/C# синтаксису.

### 4. Улучшения asyncio

- `asyncio.TaskGroup` — теперь стабильный API для управления группами задач.
- `asyncio.Runner` — новый способ запуска асинхронного кода.
- Улучшенная производительность event loop.

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("url1"))
        task2 = tg.create_task(fetch_data("url2"))
    # Обе задачи завершены (или одна из них отменена при ошибке)

asyncio.run(main())
```

### 5. Perf-профилировщик

Python 3.12 интегрируется с профилировщиком `perf` в Linux, позволяя профилировать Python-код на уровне системы без модификации кода:

```bash
perf record python my_script.py
perf report
```

## Python 3.13: взгляд в будущее

Python 3.13 (октябрь 2024) принёс ещё более амбициозные изменения.

### 1. Экспериментальный JIT-компилятор (PEP 744)

Самое громкое изменение: экспериментальный JIT-компилятор на основе copy-and-patch техники. Включается флагом:

```bash
python -X jit my_script.py
```

Пока это экспериментальная функция, но она обещает значительное ускорение в будущих версиях.

### 2. Новый интерактивный интерпретатор

Python 3.13 включает новый REPL с:
- Подсветкой синтаксиса
- Многострочным редактированием
- Сохранением истории между сессиями
- Автодополнением

```bash
# Новый REPL включается автоматически в Python 3.13+
python
>>> def greet(name):
...     return f"Hello, {name}!"
>>> greet("World")
'Hello, World!'
```

### 3. Отказ от GIL (PEP 703)

Python 3.13 включает экспериментальную сборку без GIL:

```bash
# Установка free-threaded версии
pyenv install 3.13t
```

Это позволяет настоящий параллелизм в потоках — огромный шаг для Python.

### 4. Улучшения типизации

- `TypeIs` (PEP 742) — более точный type narrowing.
- `ReadOnly` (PEP 705) — для TypedDict.
- Новые возможности в `typing` модуле.

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

items: list[object] = ["a", "b", "c"]
if is_str_list(items):
    # Здесь items имеет тип list[str]
    print(", ".join(items))
```

## Стратегия миграции

1. **Начинайте с тестов**: запустите тесты на новой версии Python.
2. **Используйте CI-матрицу**: тестируйте на нескольких версиях Python.
3. **Постепенное обновление**: не обновляйте production сразу после выхода.
4. **Следите за deprecated warnings**: исправляйте предупреждения заранее.

## Заключение

Python продолжает эволюционировать, становясь быстрее и удобнее. JIT-компилятор и отказ от GIL — самые значительные изменения в рантайме со времён Python 3.0. Если вы профессионал, следите за этими изменениями — они изменят то, как мы пишем высокопроизводительный Python-код.