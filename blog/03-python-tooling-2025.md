---
title: "Python-инструменты в 2025: uv, ruff, pyproject.toml и конец requirements.txt"
date: "2025-03-05"
author: "Команда Python for Professionals"
tags: ["python", "инструменты", "uv", "ruff", "pyproject.toml", "poetry"]
summary: "Как изменился ландшафт Python-инструментов: uv как замена pip, ruff как замена flake8, и почему pyproject.toml — новый стандарт."
---

Мир Python-инструментов пережил революцию. В 2025 году стек профессионала выглядит иначе, чем два года назад. Давайте разберёмся, что изменилось и как на этом сэкономить время.

## Эволюция управления зависимостями

```
requirements.txt  →  Pipfile/Pipfile.lock  →  pyproject.toml + poetry.lock  →  pyproject.toml + uv.lock
(2010)               (2017)                    (2019)                          (2024)
```

### uv: pip на стероидах

`uv` — это менеджер пакетов, написанный на Rust компанией Astral (создатели ruff). Он в 10-100 раз быстрее pip:

```bash
# Установка uv
pip install uv

# Создание виртуального окружения (мгновенно)
uv venv

# Установка зависимостей (в 10-100x быстрее pip)
uv pip install -r requirements.txt

# Или с pyproject.toml
uv sync

# Добавление зависимости
uv add pandas

# Запуск скрипта в окружении
uv run python my_script.py
```

Сравнение скорости (установка pandas + numpy + scikit-learn):

| Инструмент | Время |
|------------|-------|
| pip | 45.2 сек |
| pip-tools | 42.1 сек |
| poetry | 38.7 сек |
| **uv** | **3.2 сек** |

### pyproject.toml: единый конфиг

`pyproject.toml` (PEP 517/518/621) — универсальный файл конфигурации для Python-проекта:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Отличный проект"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.2.0",
    "mypy>=1.8",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.11"
strict = true
```

## ruff: линтинг и форматирование

`ruff` — молниеносный линтер и форматер на Rust, заменяющий flake8, isort, pyflakes и десятки плагинов:

```bash
# Линтинг
ruff check .

# Автофикс
ruff check --fix .

# Форматирование (замена black)
ruff format .
```

Сравнение скорости (линт 1000 файлов):

| Инструмент | Время |
|------------|-------|
| flake8 + isort | 18.3 сек |
| pylint | 32.1 сек |
| **ruff** | **0.2 сек** |

### Конфигурация ruff в pyproject.toml:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## mypy: статическая типизация

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

Запуск:

```bash
mypy src/
```

## pre-commit: автоматизация проверок

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Установка:

```bash
pre-commit install
pre-commit run --all-files  # ручная проверка
```

## Полный современный стек

```bash
# Создание проекта
mkdir my-project && cd my-project
uv venv
source .venv/bin/activate  # или .venv\Scripts\activate на Windows

# Установка инструментов
uv add --dev ruff mypy pytest pre-commit

# Настройка pyproject.toml (см. выше)
# Настройка .pre-commit-config.yaml

# Первый запуск
uv run ruff check .
uv run mypy src/
uv run pytest
```

## Миграция с requirements.txt

```bash
# 1. Создайте pyproject.toml с зависимостями
# 2. Установите uv
pip install uv

# 3. Сгенерируйте lock-файл
uv lock

# 4. Установите зависимости
uv sync

# 5. Удалите старые файлы
rm requirements.txt requirements-dev.txt
```

## Заключение

Современный стек Python-разработчика в 2025:

| Задача | Инструмент | Замена |
|--------|-----------|--------|
| Управление зависимостями | **uv** | pip, poetry, pipenv |
| Линтинг | **ruff** | flake8, isort, pylint |
| Форматирование | **ruff format** | black |
| Типизация | **mypy** / **pyright** | — |
| Тестирование | **pytest** | unittest |
| Git hooks | **pre-commit** | — |
| Конфигурация | **pyproject.toml** | setup.cfg, .flake8, .isort.cfg |

Этот стек экономит часы времени разработчика и делает Python-проекты более стандартизированными и производительными.