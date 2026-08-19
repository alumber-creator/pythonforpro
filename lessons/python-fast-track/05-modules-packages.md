---
title: "Модули, пакеты и импорты"
order: 5
tags: ["модули", "пакеты", "import", "pip"]
prerequisites: "Урок 4"
objective: "Освоить систему модулей Python, организацию кода в пакеты и установку сторонних библиотек"
---

## Введение

Одно из главных преимуществ Python — **система модулей и пакетов**. Она одновременно проще, чем Java-пакеты с их сложной иерархией директорий и `classpath`, и мощнее, чем C++ `#include` с его проблемами двойного включения и порядком компиляции.

В Python каждый `.py`-файл — это модуль. Директория с `__init__.py` — это пакет. Импорт делается одной строкой. `pip install` устанавливает любую из 450 000+ библиотек из PyPI.

Этот урок охватывает: систему импорта, организацию кода в пакеты, `__name__ == "__main__"`, `pip` и виртуальные окружения.

### 🎯 Цель урока

Освоить систему модулей Python, организацию кода в пакеты и установку сторонних библиотек. После этого урока вы сможете структурировать Python-проект любого размера и управлять зависимостями.

### 📋 Предпосылки

Вы уверенно владеете функциями, структурами данных и базовым синтаксисом Python (Уроки 1–4).

---

## Основная часть

### 1. Модули: каждый .py файл — это модуль

В Python **модуль** — это просто файл с расширением `.py`. Никаких специальных объявлений, никаких `package` или `namespace` — просто файл.

```python
# utils.py — это модуль
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
```

```python
# main.py — импорт модуля
import utils

print(utils.add(3, 4))       # 7
print(utils.multiply(5, 6))  # 30
print(utils.PI)              # 3.14159
```

**Сравнение с другими языками:**

| Концепция | Python | Java | C++ | JavaScript (ES6) |
|-----------|--------|------|-----|-----------------|
| Единица кода | `.py` файл | `.java` файл (класс) | `.cpp`/`.h` файлы | `.js`/`.mjs` файл |
| Импорт | `import module` | `import package.Class;` | `#include "file.h"` | `import {x} from "./module.js"` |
| Объявление модуля | Не требуется | `package com.example;` | Не требуется | `export` |
| Разрешение имён | `sys.path` | `classpath` | Include path | `node_modules`, paths |

### 2. Способы импорта

Python предлагает несколько способов импорта — от самого явного до самого лаконичного.

```python
# Пусть у нас есть модуль math_utils.py:
# def add(a, b): return a + b
# def subtract(a, b): return a - b
# PI = 3.14159

# Способ 1: Импорт модуля (пространство имён)
import math_utils
print(math_utils.add(3, 4))  # Явно, понятно откуда функция

# Способ 2: Импорт конкретных имён
from math_utils import add, PI
print(add(3, 4))             # Коротко, но потерян контекст
print(PI)

# Способ 3: Импорт с псевдонимом
import math_utils as mu
print(mu.add(3, 4))          # Компромисс: коротко + контекст

# Способ 4: Импорт всего (НЕ ДЕЛАЙТЕ ТАК!)
from math_utils import *     # ❌ Загрязняет пространство имён!
print(add(3, 4))             # Откуда add? Непонятно!
```

**Выбор способа импорта:**

| Способ | Когда использовать | Пример |
|--------|-------------------|--------|
| `import module` | Стандартная библиотека, собственные модули | `import os`, `import json` |
| `import module as alias` | Длинные имена, общепринятые сокращения | `import numpy as np`, `import pandas as pd` |
| `from module import name` | 1–2 конкретных имени из модуля | `from pathlib import Path` |
| `from module import *` | **Никогда** (кроме интерактивного режима) | — |

**Общепринятые алиасы в экосистеме Python:**

```python
import numpy as np            # Научные вычисления
import pandas as pd           # Анализ данных
import matplotlib.pyplot as plt  # Визуализация
import tensorflow as tf       # Deep Learning
import torch                  # PyTorch (обычно без алиаса)
```

### 3. `__name__ == "__main__"`: скрипт и модуль одновременно

Один и тот же `.py`-файл может быть и **скриптом** (запускаться напрямую), и **модулем** (импортироваться). Конструкция `if __name__ == "__main__"` позволяет разделить эти два режима.

```python
# calculator.py
"""Модуль для математических операций."""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def main():
    """Точка входа при запуске как скрипта."""
    print("Calculator started")
    print(f"3 + 4 = {add(3, 4)}")
    print(f"10 - 5 = {subtract(10, 5)}")

if __name__ == "__main__":
    main()
```

```bash
# Запуск как скрипт:
$ python calculator.py
# Calculator started
# 3 + 4 = 7
# 10 - 5 = 5
```

```python
# Импорт как модуль:
import calculator
print(calculator.add(10, 20))  # 30
# main() НЕ вызывается!
```

**Как это работает:**

| Переменная | Значение | Когда |
|-----------|----------|-------|
| `__name__` | `"__main__"` | Файл запущен напрямую: `python file.py` |
| `__name__` | `"module_name"` | Файл импортирован: `import module_name` |

**Сравнение с другими языками:**

```python
# Python
if __name__ == "__main__":
    main()
```

```java
// Java: точка входа — всегда метод main класса
public class Calculator {
    public static int add(int a, int b) { return a + b; }
    public static void main(String[] args) {
        System.out.println("3 + 4 = " + add(3, 4));
    }
}
```

```cpp
// C++: main() — глобальная функция
int add(int a, int b) { return a + b; }
int main() {
    std::cout << "3 + 4 = " << add(3, 4) << std::endl;
    return 0;
}
```

```javascript
// Node.js: require.main === module
function add(a, b) { return a + b; }
if (require.main === module) {
    console.log("3 + 4 =", add(3, 4));
}
module.exports = { add };
```

### 4. Пакеты: организация кода в директории

**Пакет** — это директория, содержащая модули и специальный файл `__init__.py`.

```
my_project/
├── __init__.py          # Делает my_project пакетом
├── core/
│   ├── __init__.py
│   ├── models.py
│   └── services.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── formatters.py
└── main.py
```

#### `__init__.py`: что это и зачем

```python
# my_project/core/__init__.py
"""Core package — содержит основные модели и сервисы."""

# Экспорт публичного API пакета
from .models import User, Product
from .services import UserService, ProductService

# Теперь при импорте core доступны User, Product, UserService, ProductService
```

```python
# main.py
from my_project.core import User, UserService

user = User("Alice")
service = UserService()
```

**Три подхода к `__init__.py`:**

| Подход | `__init__.py` | Пример использования |
|--------|--------------|---------------------|
| Пустой | `# пустой файл` | Простые пакеты, где импорт всегда явный |
| С документацией | `"""Docstring."""` | Документирование предназначения пакета |
| С реэкспортом | `from .module import Class` | Определение публичного API пакета |

#### Абсолютные и относительные импорты

```python
# В файле my_project/core/services.py

# Абсолютный импорт (от корня проекта)
from my_project.utils.validators import validate_email

# Относительный импорт (относительно текущего модуля)
from .models import User              # Из того же пакета (core)
from ..utils.formatters import format # Из соседнего пакета (utils)

# .  — текущий пакет
# .. — родительский пакет
# ... — прародительский пакет (и т.д.)
```

**Абсолютные vs относительные импорты:**

| Критерий | Абсолютный | Относительный |
|----------|-----------|---------------|
| Читаемость | Понятно откуда | Нужно знать структуру |
| Рефакторинг | Сложнее переименовывать | Легче переименовывать пакет |
| Перемещение модуля | Ломается | Может остаться рабочим |
| Рекомендация PEP 8 | ✅ Рекомендуется | Допустимо внутри пакета |

**Анти-паттерн: циклические импорты**

```python
# ❌ Циклический импорт!
# module_a.py
from module_b import func_b
def func_a():
    return func_b()

# module_b.py
from module_a import func_a  # Ошибка! Циклическая зависимость
def func_b():
    return func_a()
```

```python
# ✅ Решение: импорт внутри функции (lazy import)
# module_a.py
def func_a():
    from module_b import func_b  # Импорт только при вызове
    return func_b()
```

### 5. Пространства имён и `sys.path`

Python ищет модули в списке директорий, хранящемся в `sys.path`:

```python
import sys
for path in sys.path:
    print(path)

# Типичный вывод:
# ''                              (текущая директория)
# /usr/lib/python312.zip
# /usr/lib/python3.12
# /usr/lib/python3.12/lib-dynload
# /home/user/.local/lib/python3.12/site-packages  (pip-пакеты)
# /usr/local/lib/python3.12/dist-packages
```

**Порядок поиска модуля:**
1. Текущая директория
2. `PYTHONPATH` (переменная окружения)
3. Стандартная библиотека
4. `site-packages` (сторонние пакеты из pip)

**Важно:** не называйте свои модули так же, как модули стандартной библиотеки! Файл `json.py` в вашем проекте «затенит» стандартный `json` — и `import json` будет импортировать ваш файл, а не стандартную библиотеку.

### 6. `pip`: менеджер пакетов Python

`pip` — это стандартный менеджер пакетов Python. Он устанавливает пакеты из **PyPI** (Python Package Index).

```bash
# Установка пакета
pip install requests

# Установка конкретной версии
pip install requests==2.28.0

# Установка с ограничением версии
pip install "requests>=2.25,<3.0"

# Установка нескольких пакетов из файла
pip install -r requirements.txt

# Обновление пакета
pip install --upgrade requests

# Удаление пакета
pip uninstall requests

# Просмотр установленных пакетов
pip list
pip show requests  # Детальная информация

# Заморозка зависимостей
pip freeze > requirements.txt
```

**Файл `requirements.txt`:**

```
# requirements.txt
requests>=2.28,<3.0
flask==3.0.*
numpy>=1.24
pandas>=2.0
sqlalchemy~=2.0  # ~= означает совместимую версию (>=2.0, <3.0)
```

**Сравнение с другими экосистемами:**

| Действие | Python (pip) | JavaScript (npm) | Java (Maven/Gradle) | Rust (Cargo) |
|----------|-------------|-----------------|--------------------| -------------|
| Установка | `pip install pkg` | `npm install pkg` | Добавить в `pom.xml` | `cargo add pkg` |
| Файл зависимостей | `requirements.txt` | `package.json` | `pom.xml` | `Cargo.toml` |
| Lock-файл | `requirements.txt` (заморозка) | `package-lock.json` | `pom.xml` (плагины) | `Cargo.lock` |
| Глобальная установка | `pip install` (не рекомендуется) | `npm install -g` | `mvn install` | `cargo install` |
| Реестр пакетов | [PyPI](https://pypi.org/) | [npm](https://www.npmjs.com/) | [Maven Central](https://central.sonatype.com/) | [crates.io](https://crates.io/) |

### 7. Виртуальные окружения: изоляция зависимостей

**Виртуальное окружение** (virtual environment, venv) — это изолированная среда Python со своим набором пакетов. Это решает проблему «dependency hell»: когда проект A требует `requests==2.25`, а проект B — `requests==2.30`.

```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Windows)
.venv\Scripts\activate

# Активация (Linux/macOS)
source .venv/bin/activate

# После активации — pip устанавливает пакеты в .venv
pip install flask

# Деактивация
deactivate
```

**Структура проекта с виртуальным окружением:**

```
my_project/
├── .venv/                # Виртуальное окружение (НЕ коммитить в Git!)
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── core/
│       └── utils/
├── tests/
├── requirements.txt      # Зависимости проекта
├── requirements-dev.txt  # Зависимости для разработки (pytest, black, ...)
├── pyproject.toml        # Современная конфигурация проекта (Python 3.11+)
└── README.md
```

**Современные альтернативы `venv` + `pip`:**

| Инструмент | Описание | Когда использовать |
|-----------|----------|-------------------|
| **venv + pip** | Стандартный подход | Простые проекты, обучение |
| **Poetry** | Управление зависимостями + упаковка | Серьёзные проекты с публикацией |
| **uv** (by Astral) | Ультрабыстрый менеджер пакетов на Rust | Скорость, современные проекты |
| **pipenv** | Pipfile + виртуальное окружение | Средние проекты |
| **conda** | Кроссплатформенный менеджер пакетов | Data science, научные вычисления |

### 8. `pyproject.toml`: современный способ описания проекта

Начиная с Python 3.11, `pyproject.toml` становится стандартным способом описания проекта и его зависимостей.

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
description = "Мой первый Python-пакет"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28",
    "flask>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=23.0",
    "ruff>=0.1.0",
]

[project.scripts]
my-cli = "my_project.cli:main"
```

### 9. Сравнение систем модулей: Python vs Java vs C++ vs JavaScript

Рассмотрим одну и ту же задачу: создать модуль с математическими функциями, импортировать и использовать.

#### Python

```python
# math_utils.py — модуль
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# main.py — использование
from math_utils import add, multiply
print(add(3, 4))       # 7
print(multiply(5, 6))  # 30
```

#### Java

```java
// MathUtils.java — класс в пакете
package com.example.utils;

public class MathUtils {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int multiply(int a, int b) {
        return a * b;
    }
}

// Main.java — использование
package com.example;

import com.example.utils.MathUtils;

public class Main {
    public static void main(String[] args) {
        System.out.println(MathUtils.add(3, 4));       // 7
        System.out.println(MathUtils.multiply(5, 6));  // 30
    }
}
```

#### C++

```cpp
// math_utils.h — заголовочный файл
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

int add(int a, int b);
int multiply(int a, int b);

#endif

// math_utils.cpp — реализация
#include "math_utils.h"

int add(int a, int b) { return a + b; }
int multiply(int a, int b) { return a * b; }

// main.cpp — использование
#include <iostream>
#include "math_utils.h"

int main() {
    std::cout << add(3, 4) << std::endl;       // 7
    std::cout << multiply(5, 6) << std::endl;  // 30
    return 0;
}
```

#### JavaScript (ES6)

```javascript
// math_utils.js — модуль
export function add(a, b) {
    return a + b;
}

export function multiply(a, b) {
    return a * b;
}

// main.js — использование
import { add, multiply } from './math_utils.js';
console.log(add(3, 4));       // 7
console.log(multiply(5, 6));  // 30
```

#### Сравнительная таблица

| Аспект | Python | Java | C++ | JavaScript |
|--------|--------|------|-----|------------|
| Файлов | 2 | 2 | 3 (.h + .cpp + main) | 2 |
| Строк кода | ~10 | ~25 | ~20 | ~10 |
| Объявление namespace | Не нужно | `package com.example.utils;` | Не нужно | Не нужно |
| Объявление экспорта | Не нужно (всё публичное) | `public` | Объявление в `.h` | `export` |
| Импорт | `from module import name` | `import package.Class;` | `#include "file.h"` | `import {name} from "path"` |
| Компиляция | Не нужна | `javac` → `.class` | `g++` → executable | Не нужна |
| Защита от двойного включения | Автоматически | Автоматически | `#ifndef` / `#pragma once` | Автоматически |

Python и JavaScript выигрывают в простоте: один файл — один модуль, без ceremony. Java и C++ требуют значительно больше boilerplate-кода.

### 10. Анти-паттерны и идиоматический код

#### Анти-паттерн 1: Звёздный импорт

```python
# ❌ Плохо: загрязнение пространства имён
from math import *
from os import *

print(sin(pi))  # Откуда sin? Откуда pi? Непонятно!
# Более того, os.path переопределит math.path!
```

```python
# ✅ Идиоматично
import math
import os

print(math.sin(math.pi))
print(os.path.join("a", "b"))
```

#### Анти-паттерн 2: Импорты в середине файла

```python
# ❌ Плохо: импорты разбросаны по коду
def process_data(filename):
    import json  # Импорт внутри функции — почему?
    import csv   # Ещё один?
    ...
```

```python
# ✅ Идиоматично: все импорты в начале файла (PEP 8)
import json
import csv

def process_data(filename):
    ...
```

**Исключение:** lazy import для разрешения циклических зависимостей — допустим, но это признак проблем с архитектурой.

#### Анти-паттерн 3: Импорт неиспользуемых модулей

```python
# ❌ Плохо: импортировано то, что не используется
import os
import sys
import json
import csv
import re
import datetime  # Ни один из этих модулей не используется!

def greet(name):
    return f"Hello, {name}!"
```

#### Анти-паттерн 4: Смешивание абсолютных и относительных импортов

```python
# ❌ Непоследовательно
from my_project.utils.validators import validate_email  # Абсолютный
from .models import User                                 # Относительный
from ..services import UserService                       # Относительный
import my_project.core.config                            # Абсолютный
```

```python
# ✅ Идиоматично: выберите один стиль
# Вариант A: только абсолютные импорты
from my_project.utils.validators import validate_email
from my_project.core.models import User
from my_project.core.services import UserService
import my_project.core.config

# Вариант B: только относительные (внутри пакета)
from .models import User
from .services import UserService
from ..utils.validators import validate_email
```

### 11. Namespace packages (Python 3.3+)

Начиная с Python 3.3, `__init__.py` **не обязателен** для создания пакета. Это называется **namespace package** — пакет, который может быть распределён по нескольким директориям.

```
# Структура без __init__.py (namespace package)
plugins/
├── auth/
│   └── plugin.py
├── logging/
│   └── plugin.py
└── cache/
    └── plugin.py
```

```python
# Импорт работает без __init__.py
from plugins.auth import plugin
from plugins.logging import plugin as log_plugin
```

**Когда использовать namespace packages:**
- Большие проекты, где пакет распределён по нескольким репозиториям
- Плагинные системы

**Когда НЕ использовать:**
- Обычные проекты — явный `__init__.py` лучше документирует структуру
- Если вам нужен код инициализации пакета

---

## Практическое задание

### Задание 1: Создайте структуру проекта

Создайте следующую структуру файлов и папок:

```
todo_app/
├── __init__.py
├── models.py       # Классы Task, Project
├── services.py     # Функции add_task(), complete_task(), list_tasks()
├── utils.py        # Вспомогательные функции
└── __main__.py     # Точка входа: python -m todo_app
```

Требования:
- `__init__.py` должен реэкспортировать публичное API: `Task`, `add_task`, `complete_task`, `list_tasks`
- `__main__.py` должен предоставлять CLI-интерфейс (через `argparse` или просто `if __name__ == "__main__"`)
- Используйте относительные импорты внутри пакета
- Каждый модуль должен иметь docstring

### Задание 2: Виртуальное окружение и зависимости

1. Создайте виртуальное окружение: `python -m venv .venv`
2. Активируйте его
3. Установите пакеты: `requests`, `rich` (для красивого вывода в терминале)
4. Создайте `requirements.txt` через `pip freeze`
5. Напишите скрипт, который:
   - Использует `requests` для запроса к публичному API (например, `https://api.github.com/users/python`)
   - Использует `rich` для красивого вывода JSON-ответа

### Задание 3: Исправьте импорты

Дан проект с неправильными импортами. Исправьте:

```python
# config.py
class Config:
    DEBUG = True

# db.py
from config import Config  # ❌ может быть проблемой
import models  # ❌ неоднозначно

# models.py
from db import *  # ❌ звёздный импорт

# main.py
import sys, os, json, csv, re, datetime, collections, itertools  # ❌ слишком много в одной строке
from models import User
from models import Post
from models import Comment
```

### Задание 4: Конвертер температур (пакет)

Создайте пакет `temperature`:

```
temperature/
├── __init__.py
├── celsius.py      # to_fahrenheit, to_kelvin
├── fahrenheit.py   # to_celsius, to_kelvin
├── kelvin.py       # to_celsius, to_fahrenheit
└── cli.py          # CLI: python -m temperature 100 C F
```

Требования:
- Каждый модуль содержит функции конвертации в две другие шкалы
- `__init__.py` реэкспортирует все функции
- `cli.py` парсит аргументы командной строки и выводит результат
- Код должен работать при запуске `python -m temperature 100 C F`

---

## Дополнительные материалы

### 📖 Книги

- **«Fluent Python»** (глава 24) — Luciano Ramalho. Модули и пакеты в Python.
- **«Effective Python»** (советы 52–55) — Brett Slatkin. Развёртывание и пакетирование.
- **«Python Packaging User Guide»** — официальное руководство по упаковке Python-проектов.

### 🎥 Видео

- **«Modules and Packages: Live and Let Die!»** — David Beazley (PyCon 2015). Глубокое погружение в систему импорта.
- **«Packaging Python Projects»** — Mariatta Wijaya (PyCon 2019). Как упаковать и опубликовать проект на PyPI.

### 🔗 Ссылки

- [Python 3 Tutorial: Modules](https://docs.python.org/3/tutorial/modules.html)
- [Python 3: The import system](https://docs.python.org/3/reference/import.html)
- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 8: Imports](https://peps.python.org/pep-0008/#imports)
- [PyPI — Python Package Index](https://pypi.org/)
- [pip documentation](https://pip.pypa.io/)

### 🛠 Инструменты

- **pip** — стандартный менеджер пакетов (идёт в комплекте с Python)
- **venv** — стандартный модуль для виртуальных окружений (идёт в комплекте)
- **Poetry** — современный менеджер зависимостей и упаковки: `pip install poetry`
- **uv** — ультрабыстрый менеджер пакетов на Rust: `pip install uv`
- **pip-tools** — компиляция зависимостей с pinning: `pip install pip-tools`
- **pipx** — установка Python-приложений в изолированных окружениях: `pip install pipx`

### 💡 Интересные факты

- Система импорта Python полностью переписана в Python 3.3 (PEP 302, PEP 420). До этого был сложный C-код, теперь это чистый Python в `importlib`.
- `__init__.py` может быть пустым, но его наличие — это явный сигнал «здесь пакет». В Python 3.3+ namespace packages позволяют обойтись без него, но явный `__init__.py` всё ещё рекомендуется.
- `pip` — это рекурсивный акроним: «Pip Installs Packages». До `pip` использовался `easy_install`.
- 7 сентября 2022 года PyPI достиг 400 000 пакетов. На октябрь 2024 года — уже более 530 000.
- `import antigravity` — это пасхальное яйцо Python, которое открывает комикс xkcd про Python.