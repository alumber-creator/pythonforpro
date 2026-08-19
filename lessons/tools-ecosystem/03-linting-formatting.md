---
title: "Линтинг и форматирование: black, ruff, mypy"
order: 3
tags: ["black", "ruff", "mypy", "pep8", "качество-кода", "pre-commit"]
prerequisites: "Базовый Python, pip"
objective: "Настроить автоматическое форматирование и линтинг для профессиональной разработки"
---

# Линтинг и форматирование: black, ruff, mypy

## Введение

### 🎯 Цель урока

Настроить полный конвейер автоматической проверки качества кода: форматирование через `black`, линтинг через `ruff`, статическую типизацию через `mypy` и автоматизацию через `pre-commit`. После этого урока ваш код всегда будет соответствовать стандартам индустрии.

### 📋 Предпосылки

- Базовый Python (функции, классы, модули)
- Умение устанавливать пакеты через pip
- Знакомство с PEP 8 (стиль кода Python)

### Почему качество кода автоматизируется

Ручное соблюдение стиля невозможно в команде из 2+ человек. Каждый разработчик имеет свои привычки: одни ставят пробелы вокруг операторов, другие нет; одни используют двойные кавычки, другие одинарные. Code review превращается в бесконечные споры о форматировании вместо обсуждения логики.

**Решение**: автоматические инструменты, которые не спорят, а просто делают.

---

## Основная часть

### 1. `black` — бескомпромиссный форматировщик

`black` автоматически форматирует Python-код в едином стиле. Его девиз: *«Любой цвет, если он чёрный»* (отсылка к Генри Форду). `black` не настраивается почти ни в чём — и это его главное преимущество. Нет споров о стиле, есть один стандарт.

```bash
pip install black

# Форматирование файла
black app.py

# Форматирование всей папки
black src/

# Проверка без изменений (для CI)
black --check src/

# Просмотр изменений без применения
black --diff src/

# Форматирование с указанием версии Python
black --target-version py310 src/

# Быстрый режим (пропускает безопасные проверки)
black --fast src/
```

#### Что меняет `black`

```python
# ДО black
def foo(x,y,z):
    return {'x':x,'y':y,'z':z,}

result=foo( 1,2,  3 )

# ПОСЛЕ black
def foo(x, y, z):
    return {"x": x, "y": y, "z": z}


result = foo(1, 2, 3)
```

Основные правила `black`:

- Двойные кавычки `"` вместо одинарных `'`
- Длина строки — 88 символов (по умолчанию)
- Висячие запятые в многострочных конструкциях
- Пробелы вокруг операторов
- Последовательные запятые в конце коллекций
- Нормализация отступов и пустых строк

#### Конфигурация в `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]
include = '\.pyi?$'
extend-exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | build
  | dist
  | migrations
)/
'''
```

#### Интеграция с IDE

```json
// VS Code settings.json
{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    }
}
```

### 2. `ruff` — сверхбыстрый линтер

`ruff` — это молниеносный линтер на Rust, который заменяет десятки инструментов: `flake8`, `isort`, `pyflakes`, `pydocstyle`, `pyupgrade`, `autoflake` и другие. Он в 10-100 раз быстрее аналогов.

```bash
pip install ruff

# Проверка кода
ruff check .

# Автоматическое исправление
ruff check --fix .

# Форматирование импортов (как isort)
ruff check --fix --select I .

# Просмотр всех правил
ruff rule E501
```

#### Правила ruff (категории)

| Префикс | Категория | Описание |
|---------|-----------|----------|
| `E` / `W` | pycodestyle | Ошибки стиля и предупреждения |
| `F` | Pyflakes | Обнаружение неиспользуемых переменных, импортов |
| `I` | isort | Порядок импортов |
| `N` | pep8-naming | Именование (PEP 8) |
| `D` | pydocstyle | Документирование (docstrings) |
| `UP` | pyupgrade | Современный синтаксис Python |
| `B` | flake8-bugbear | Потенциальные баги |
| `SIM` | flake8-simplify | Упрощение кода |
| `C4` | flake8-comprehensions | Улучшение comprehensions |
| `T20` | flake8-print | Запрет print-ов |
| `PL` | Pylint | Правила из Pylint |
| `RUF` | Ruff-specific | Специфичные для ruff правила |

#### Конфигурация в `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "W",      # pycodestyle warnings
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "SIM",    # flake8-simplify
    "C4",     # flake8-comprehensions
]
ignore = [
    "E501",   # line too long (handled by black)
]
fixable = ["ALL"]

[tool.ruff.lint.isort]
known-first-party = ["myproject"]
known-third-party = ["django", "fastapi"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
```

#### Примеры ошибок, которые находит ruff

```python
# ❌ F401: imported but unused
import os
import json  # не используется — ruff предупредит

# ❌ F841: local variable assigned but never used
def calculate(x: int) -> int:
    result = x * 2  # не используется
    return x * 2

# ❌ B006: mutable default argument
def add_item(item: str, items: list = []) -> list:
    items.append(item)
    return items

# ❌ SIM108: use ternary operator
def get_status(is_active: bool) -> str:
    if is_active:
        return "active"
    else:
        return "inactive"
# ✅ Исправление:
def get_status(is_active: bool) -> str:
    return "active" if is_active else "inactive"

# ❌ UP006: use `list` instead of `List` for type hints
from typing import List
def process(items: List[str]) -> None: ...
# ✅ Исправление (Python 3.9+):
def process(items: list[str]) -> None: ...
```

### 3. `mypy` — статическая проверка типов

`mypy` проверяет корректность type hints до запуска программы. Это третий столп качества кода после форматирования и линтинга.

```bash
pip install mypy

# Проверка файла
mypy app.py

# Проверка всего проекта
mypy src/

# Строгий режим
mypy --strict src/

# Генерация HTML-отчёта
mypy --html-report mypy-report src/
```

#### Конфигурация в `pyproject.toml`

```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
warn_unreachable = true
disallow_untyped_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
    "docs.*",
]
ignore_errors = true
```

#### Примеры ошибок mypy

```python
# ❌ Ошибка: несовместимые типы
def greet(name: str) -> str:
    return "Hello, " + name

greet(42)  # error: Argument 1 to "greet" has incompatible type "int"; expected "str"

# ❌ Ошибка: возвращаемый тип не соответствует аннотации
def get_user() -> dict[str, str]:
    return {"id": 1, "name": "Alice"}  # error: dict entry 0 has incompatible type "str": "int"

# ✅ Правильно:
def get_user() -> dict[str, str | int]:
    return {"id": 1, "name": "Alice"}
```

### 4. `pre-commit` — автоматизация проверок

`pre-commit` запускает все проверки автоматически перед каждым коммитом. Это последняя линия обороны: плохой код просто не попадёт в репозиторий.

```bash
pip install pre-commit

# Установка git-хуков
pre-commit install

# Ручной запуск всех хуков
pre-commit run --all-files

# Запуск конкретного хука
pre-commit run black --all-files

# Автообновление версий хуков
pre-commit autoupdate
```

#### `.pre-commit-config.yaml` — полный конфиг

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: detect-private-key
      - id: debug-statements
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
          - types-python-dateutil
        args: [--strict]

  - repo: https://github.com/python-poetry/poetry
    rev: 1.8.0
    hooks:
      - id: poetry-check
      - id: poetry-lock
        args: [--check]
```

#### Что происходит при коммите

```bash
$ git commit -m "Add user model"

# 1. trailing-whitespace — удаляет пробелы в конце строк
# 2. end-of-file-fixer — добавляет пустую строку в конец файла
# 3. black — форматирует код
# 4. ruff — проверяет и исправляет ошибки линтинга
# 5. mypy — проверяет типы

# Если всё зелёное — коммит проходит
# Если есть ошибки — коммит блокируется, нужно исправить
```

### 5. CI/CD интеграция (GitHub Actions)

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install black ruff mypy

      - name: Check formatting (black)
        run: black --check --diff .

      - name: Lint (ruff)
        run: ruff check .

      - name: Type check (mypy)
        run: mypy src/ --strict
```

### 6. Сравнение с экосистемами других языков

#### JavaScript: ESLint + Prettier

| Аспект | Python | JavaScript |
|--------|--------|------------|
| Форматирование | black | Prettier |
| Линтинг | ruff | ESLint |
| Порядок импортов | ruff (isort) | eslint-plugin-import |
| Типизация | mypy | TypeScript (tsc) |
| Git-хуки | pre-commit | husky + lint-staged |
| Философия | Минимум конфигурации | Максимум гибкости |

```json
// JavaScript: package.json с Prettier + ESLint
{
  "scripts": {
    "format": "prettier --write .",
    "lint": "eslint . --fix",
    "typecheck": "tsc --noEmit"
  }
}
```

```toml
# Python: pyproject.toml
[tool.black]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
```

#### Java: Checkstyle + SpotBugs + Google Java Format

| Аспект | Python | Java |
|--------|--------|------|
| Форматирование | black | google-java-format |
| Линтинг стиля | ruff | Checkstyle |
| Статический анализ | ruff | SpotBugs / PMD |
| Типизация | mypy (опционально) | Компилятор (обязательно) |
| Интеграция | pre-commit | Maven/Gradle плагины |

```xml
<!-- Maven pom.xml: Checkstyle -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>3.3.1</version>
    <configuration>
        <configLocation>google_checks.xml</configLocation>
    </configuration>
</plugin>
```

#### C++: clang-format + clang-tidy

| Аспект | Python | C++ |
|--------|--------|-----|
| Форматирование | black | clang-format |
| Линтинг | ruff | clang-tidy |
| Скорость | ruff (Rust, очень быстро) | clang-tidy (медленно) |
| Настройка | Минимальная | Детальная (`.clang-format`) |

```yaml
# .clang-format (C++)
BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 100
```

### 7. ✅ Идиоматичное использование

```bash
# ✅ ПРАВИЛЬНО: единый конфиг в pyproject.toml
# Все инструменты читают настройки из одного файла

# ✅ ПРАВИЛЬНО: проверка в CI, а не только локально
git push  # триггерит GitHub Actions с black, ruff, mypy

# ✅ ПРАВИЛЬНО: автоматическое исправление, где возможно
ruff check --fix .   # ruff исправляет многие ошибки сам
black .              # black форматирует без вопросов

# ✅ ПРАВИЛЬНО: разделение обязательных и желательных проверок
# pre-commit: black + ruff (быстро, блокирует коммит)
# CI: + mypy + тесты (медленнее, блокирует merge)
```

```python
# ✅ ПРАВИЛЬНО: использовать `# noqa` точечно и с комментарием
import legacy_module  # noqa: F401 — требуется для обратной совместимости

# ✅ ПРАВИЛЬНО: использовать `# type: ignore` только когда необходимо
result = complex_generic_function()  # type: ignore[return-value]  # mypy bug #1234
```

### 8. ❌ Антипаттерны

```bash
# ❌ НЕПРАВИЛЬНО: отключать линтер для всего файла
# flake8: noqa  # В начале файла — никогда так не делайте

# ❌ НЕПРАВИЛЬНО: игнорировать ошибки вместо исправления
ruff check --ignore ALL .

# ❌ НЕПРАВИЛЬНО: коммитить с --no-verify
git commit --no-verify  # обходит pre-commit, плохой код попадает в репу

# ❌ НЕПРАВИЛЬНО: разные конфигурации форматирования у разных разработчиков
# Используйте ОДИН pyproject.toml, закоммиченный в репозиторий

# ❌ НЕПРАВИЛЬНО: смешивать black и ручное форматирование
# Либо доверьтесь black, либо не используйте его вообще
```

```python
# ❌ НЕПРАВИЛЬНО: подавлять предупреждения бездумно
x = get_data()  # type: ignore  # Какое предупреждение? Почему игнорируем?

# ❌ НЕПРАВИЛЬНО: комментировать автоформатирование
# fmt: off
def ugly_function(  x,   y,z):return  x+y
# fmt: on
# Если функция настолько особенная — объясните почему в комментарии
```

### 9. Продвинутые техники

#### Кастомные правила ruff

```python
# myproject/rules.py
# Ruff поддерживает плагины — можно писать свои правила
```

#### pre-commit с пропуском в CI

```yaml
# .github/workflows/quality.yml
- name: Run pre-commit
  uses: pre-commit/action@v3.0.1
  # Запускает те же хуки, что и локально — единый стандарт
```

#### Интеграция с Makefile / Taskfile

```makefile
# Makefile — единая точка входа
.PHONY: format lint typecheck check

format:
	black .
	ruff check --fix .

lint:
	ruff check .

typecheck:
	mypy src/

check: format lint typecheck
	@echo "✅ All checks passed!"
```

#### Проверка в реальном времени через редактор

```json
// VS Code settings.json — полная интеграция
{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },
    "mypy-type-checker.args": ["--strict"],
    "ruff.lint.args": ["--config=pyproject.toml"]
}
```

---

## Практическое задание

### Задача: настройка полного конвейера качества кода

1. **Создайте проект** с виртуальным окружением:

```bash
mkdir quality-workshop
cd quality-workshop
python -m venv .venv
source .venv/bin/activate
```

2. **Установите инструменты**:

```bash
pip install black ruff mypy pre-commit
```

3. **Создайте `pyproject.toml`** с конфигурацией всех инструментов:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "quality-workshop"
version = "0.1.0"
requires-python = ">=3.10"

[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "C4"]

[tool.ruff.lint.isort]
known-first-party = ["quality_workshop"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.10"
strict = true
```

4. **Создайте «плохой» файл** `bad_code.py` со следующими ошибками:

```python
import os, sys, json
from typing import List, Dict, Optional

def  add_numbers(x,y,z):
    result=x+y+z
    return {'sum':result,}

def GetData( url : str, timeout : int = 30 ) -> Dict[str,str] :
    import requests
    response=requests.get(url,timeout=timeout)
    return response.json()

class user_service:
    def __init__(self,users:List[str]=[]):
        self.users=users

    def AddUser(self,name:str):
        if self.users:
            self.users.append(name)
        else:
            self.users=[name]
        return self.users

def process_items(items: Optional[List[int]]=None):
    if items==None:
        items=[]
    total=0
    for i in items:
        total=total+i
    return total

unused_variable = "this is never used"
```

5. **Запустите `black`** и посмотрите на изменения:

```bash
black --diff bad_code.py
black bad_code.py
```

6. **Запустите `ruff`** и исправьте ошибки:

```bash
ruff check bad_code.py
ruff check --fix bad_code.py
```

7. **Добавьте type hints** и запустите `mypy`:

```bash
mypy bad_code.py
```

8. **Создайте `.pre-commit-config.yaml`** и установите хуки:

```bash
pre-commit install
git add bad_code.py pyproject.toml
git commit -m "Add bad code"
# Коммит должен быть заблокирован!
```

9. **Исправьте ВСЕ ошибки, чтобы коммит прошёл**.

10. **Создайте «чистый» файл** `good_code.py`:

```python
"""Пример качественного кода, проходящего все проверки."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def calculate_statistics(data: list[float]) -> dict[str, float]:
    """Вычисляет базовую статистику для списка чисел.

    Args:
        data: Список чисел для анализа.

    Returns:
        Словарь с ключами mean, min, max, sum.

    Raises:
        ValueError: Если data пуст.
    """
    if not data:
        raise ValueError("Data list cannot be empty")

    return {
        "mean": sum(data) / len(data),
        "min": min(data),
        "max": max(data),
        "sum": sum(data),
    }


class DataProcessor:
    """Обработчик данных с поддержкой фильтрации и трансформации."""

    def __init__(self, data: list[dict[str, Any]]) -> None:
        """Инициализирует обработчик.

        Args:
            data: Список словарей с данными.
        """
        self._data = data
        self._filters: list[callable] = []

    def add_filter(self, filter_func: callable) -> None:
        """Добавляет фильтр в цепочку обработки."""
        self._filters.append(filter_func)

    def process(self) -> list[dict[str, Any]]:
        """Применяет все фильтры и возвращает результат."""
        result = self._data
        for filter_func in self._filters:
            result = [item for item in result if filter_func(item)]
        return result


def load_config(path: str | Path) -> dict[str, Any]:
    """Загружает конфигурацию из JSON-файла.

    Args:
        path: Путь к JSON-файлу.

    Returns:
        Словарь с конфигурацией.

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    import json

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    return json.loads(config_path.read_text(encoding="utf-8"))
```

11. **Проверьте, что `good_code.py` проходит все проверки без ошибок**:

```bash
black --check good_code.py
ruff check good_code.py
mypy good_code.py
```

---

## Дополнительные материалы

### 📚 Официальная документация

- [black documentation](https://black.readthedocs.io/) — официальное руководство
- [ruff documentation](https://docs.astral.sh/ruff/) — все правила и настройки
- [mypy documentation](https://mypy.readthedocs.io/) — руководство по проверке типов
- [pre-commit documentation](https://pre-commit.com/) — создание и использование хуков
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)

### 🎥 Видео и статьи

- [The Ruff Formatter](https://astral.sh/blog/the-ruff-formatter) — блог Astral о создании форматтера
- [Why you should use black](https://www.youtube.com/watch?v=wf-BqAjZb8M) — Łukasz Langa о философии black
- [Hypermodern Python](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/) — серия статей о современном Python-проекте

### 🔗 Связанные уроки

- **Урок 4**: Статическая типизация — углублённое изучение mypy, type hints, Protocols
- **Урок 5**: Документирование кода — pydocstyle правила в ruff

### 🛠 Расширения

- [ruff-lsp](https://github.com/astral-sh/ruff-lsp) — LSP-сервер для ruff
- [blacken-docs](https://github.com/adamchainz/blacken-docs) — форматирование кода в Markdown
- [darker](https://github.com/akaihola/darker) — форматирование только изменённых строк

### 💡 Ключевые выводы

1. **black** — форматирование без споров, один стиль для всей команды
2. **ruff** — единый быстрый линтер вместо десятка инструментов
3. **mypy** — статическая типизация для обнаружения багов до запуска
4. **pre-commit** — автоматический контроль качества при каждом коммите
5. Все настройки — в одном `pyproject.toml`
6. CI (GitHub Actions) — финальная проверка, которая блокирует некачественный код
7. Интеграция с IDE (VS Code) — ошибки видны сразу при написании кода