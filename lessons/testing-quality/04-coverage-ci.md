---
title: "Покрытие кода и CI/CD"
order: 4
tags:
  - покрытие
  - coverage
  - CI
  - CD
  - GitHub-Actions
prerequisites: "Урок 3, git"
objective: "Настроить измерение покрытия кода и непрерывную интеграцию"
---

# Покрытие кода и CI/CD

## Введение

Тесты бесполезны, если их никто не запускает. В этом уроке мы настроим два
ключевых элемента современного процесса разработки:

1. **Измерение покрытия кода** — чтобы знать, какие части кода не тестируются.
2. **Непрерывную интеграцию (CI)** — чтобы тесты запускались автоматически
   при каждом push и pull request.

После этого урока вы сможете настроить GitHub Actions для автоматического
запуска тестов с матрицей версий Python, измерением покрытия и генерацией
бейджей, а также подключить pre-commit-хуки для локальной проверки качества.

---

## Основная часть

### 1. Покрытие кода: `coverage.py`

`coverage.py` — стандартный инструмент для измерения покрытия в Python.
Он отслеживает, какие строки (и ветки) кода выполняются во время тестов.

```bash
pip install coverage
```

#### 1.1. Базовое использование

```bash
# Запуск тестов с измерением покрытия
coverage run -m pytest tests/

# Текстовый отчёт в терминале
coverage report

# HTML-отчёт (открыть htmlcov/index.html)
coverage html
```

Пример вывода `coverage report`:

```
Name                    Stmts   Miss  Cover
-------------------------------------------
src/__init__.py             0      0   100%
src/bank.py                24      2    92%
src/services.py            35      8    77%
src/utils.py               12      0   100%
-------------------------------------------
TOTAL                      71     10    86%
```

| Колонка | Значение                                      |
| ------- | --------------------------------------------- |
| Stmts   | Количество исполняемых инструкций (statements) |
| Miss    | Невыполненные строки                           |
| Cover   | Процент покрытия                               |

#### 1.2. Конфигурация `pyproject.toml`

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_also = [
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "@(abc\\.)?abstractmethod",
]
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

Ключевые опции:

| Опция          | Значение                                         |
| -------------- | ------------------------------------------------ |
| `source`       | Измерять покрытие только в указанных каталогах    |
| `branch`       | Измерять покрытие веток (а не только строк)        |
| `omit`         | Исключить файлы по шаблонам                       |
| `exclude_also` | Строки, которые не считаются «пропущенными»        |
| `show_missing` | Показывать номера непокрытых строк                 |

#### 1.3. Покрытие строк vs покрытие веток

```python
def get_discount(age: int, is_student: bool) -> float:
    if age < 18 or age > 65:          # ветка 1: True
        return 0.5                     # ветка 2: False
    if is_student:                     # ветка 3: True
        return 0.3                     # ветка 4: False
    return 0.0
```

| Вид покрытия        | Что измеряет                             |
| ------------------- | ---------------------------------------- |
| Line coverage       | Каждая ли строка выполнена?               |
| Branch coverage     | Каждая ли ветка (if/else, цикл) выполнена? |

Один тест `get_discount(16, False)` даст 100% line coverage (все строки
выполнены), но только 50% branch coverage (ветки `is_student` True и
`age >= 18 and age <= 65` не проверены).

```python
def test_get_discount_line_coverage() -> None:
    """Только 50% branch coverage!"""
    assert get_discount(16, False) == 0.5  # строка сработала
    assert get_discount(70, False) == 0.5  # та же строка, снова

def test_get_discount_branch_coverage() -> None:
    """100% branch coverage."""
    assert get_discount(16, False) == 0.5   # age < 18
    assert get_discount(30, True) == 0.3    # is_student
    assert get_discount(30, False) == 0.0   # default
```

✅ **Идиоматично:** всегда включать `branch = true` в конфигурации coverage.

❌ **Антипаттерн:** гнаться за 100% line coverage, игнорируя branch coverage.

### 2. `pytest-cov` — интеграция pytest и coverage

```bash
pip install pytest-cov
```

```bash
# Запуск тестов с покрытием (одна команда)
pytest --cov=src --cov-report=term-missing --cov-report=html
```

Настройка в `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-branch",
    "--cov-fail-under=80",
]
```

| Флаг                     | Назначение                                       |
| ------------------------ | ------------------------------------------------ |
| `--cov=src`              | Измерять покрытие в каталоге `src`                |
| `--cov-report=term-missing` | Отчёт в терминал с номерами пропущенных строк  |
| `--cov-report=html`      | HTML-отчёт в `htmlcov/`                           |
| `--cov-report=xml`       | XML-отчёт для CI-систем (cobertura-формат)        |
| `--cov-branch`           | Включить branch coverage                          |
| `--cov-fail-under=80`    | Упасть, если покрытие ниже 80%                    |

### 3. Какой процент покрытия считать хорошим?

Это религиозный вопрос, но вот практические ориентиры:

| Проект                          | Рекомендуемое покрытие | Почему                          |
| ------------------------------- | ---------------------- | ------------------------------- |
| Стартап, MVP                    | 60-70%                 | Скорость важнее полноты          |
| Бизнес-логика, финтех           | 90-95%                 | Цена ошибки высока               |
| Библиотека с открытым кодом     | 90-100%                | Доверие сообщества               |
| Инфраструктурный код            | 80-90%                 | Критично для стабильности        |
| Легаси-проект (без тестов)      | 0 → 50% за полгода     | Постепенно, начиная с критичных  |

> **Важно:** Покрытие — не цель, а индикатор. 100% покрытие с плохими тестами
> хуже, чем 70% с тестами, проверяющими реальное поведение. Не тестируйте
> геттеры, сеттеры и тривиальный код ради процента.

### 4. CI/CD с GitHub Actions

#### 4.1. Базовый workflow

Создайте `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-branch --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: true
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

#### 4.2. Матричное тестирование

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, windows-latest, macos-latest]
    exclude:
      - os: windows-latest
        python-version: "3.10"
```

Это создаст 3 × 3 − 1 = 8 параллельных job'ов. Матрица проверяет, что код
работает на всех поддерживаемых платформах и версиях Python.

#### 4.3. Кэширование зависимостей

```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

#### 4.4. Расширенный workflow: lint + test + type-check

```yaml
name: Quality

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: "check ."

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install mypy
      - run: mypy src/

  test:
    needs: [lint, type-check]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src --cov-report=xml --cov-branch --cov-fail-under=80
```

#### 4.5. Бейджи (Badges)

Добавьте в `README.md`:

```markdown
[![Tests](https://github.com/USER/REPO/actions/workflows/tests.yml/badge.svg)](https://github.com/USER/REPO/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/USER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/USER/REPO)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
```

### 5. Pre-commit хуки

Pre-commit запускает проверки ДО коммита, блокируя «грязный» код:

```bash
pip install pre-commit
```

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [pytest, types-requests]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/ -x --tb=short
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```

```bash
pre-commit install              # хук на pre-commit
pre-commit install --hook-type pre-push  # хук на pre-push
pre-commit run --all-files      # запустить все хуки вручную
```

### 6. Сравнение с аналогами в других языках

#### JaCoCo (Java) — аналог coverage.py

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.12</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

JaCoCo генерирует отчёты в формате HTML/XML/CSV, аналогично coverage.py.
Настройка через XML, а не TOML/INI — типично для Java-экосистемы.

#### Istanbul/nyc (JavaScript) — аналог coverage.py

```json
{
  "scripts": {
    "test": "jest --coverage"
  },
  "jest": {
    "collectCoverageFrom": ["src/**/*.js"],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

Istanbul/nyc измеряет покрытие на уровне statements, branches, functions и
lines. В pytest-cov — statements и branches.

#### gcov/lcov (C/C++) — аналог coverage.py

```bash
# Сборка с флагами покрытия
g++ -fprofile-arcs -ftest-coverage -o test test.cpp

# Запуск тестов
./test

# Генерация отчёта
gcov test.cpp
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory lcov_html
```

Многошаговый процесс: отдельная сборка с флагами, запуск, генерация отчёта.
В Python это одна команда `pytest --cov`.

#### GitHub Actions vs GitLab CI vs Jenkins

| Аспект               | GitHub Actions          | GitLab CI              | Jenkins                |
| -------------------- | ----------------------- | ---------------------- | ---------------------- |
| Хостинг              | Облачный (бесплатно для OSS) | Облачный + self-hosted | Self-hosted            |
| Конфигурация         | YAML в `.github/`       | `.gitlab-ci.yml`       | Jenkinsfile (Groovy)   |
| Матрица              | `strategy: matrix:`     | `parallel: matrix:`    | Требует плагинов       |
| Интеграция с VCS     | Нативная                | Нативная               | Через плагины          |
| Рынок плагинов       | GitHub Marketplace      | GitLab CI Catalog      | Огромный               |
| Сложность настройки  | Низкая                  | Средняя                | Высокая                |

### 7. Пример полного CI/CD пайплайна

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [published]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/

  test:
    needs: quality
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov=src --cov-report=xml --cov-branch --cov-fail-under=80
      - uses: codecov/codecov-action@v4
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
        with:
          file: ./coverage.xml
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

  publish:
    needs: test
    if: github.event_name == 'release'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```

---

## Практическое задание

### Цель
Настроить полный CI/CD-пайплайн для учебного проекта с измерением покрытия,
матричным тестированием и pre-commit-хуками.

### Структура проекта

```
ci_demo/
├── src/
│   ├── __init__.py
│   └── math_utils.py
├── tests/
│   ├── __init__.py
│   └── test_math_utils.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

### Исходный код (`src/math_utils.py`)

```python
"""Mathematical utility functions."""

from __future__ import annotations

import math
from typing import TypeVar

T = TypeVar("T", int, float)


def factorial(n: int) -> int:
    """Compute factorial of n."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n > 1000:
        raise ValueError("Input too large")
    return math.factorial(n)


def is_prime(n: int) -> bool:
    """Check if n is a prime number."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def gcd(a: int, b: int) -> int:
    """Compute greatest common divisor."""
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """Compute least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def mean(values: list[T]) -> float:
    """Compute arithmetic mean."""
    if not values:
        raise ValueError("Cannot compute mean of empty list")
    return sum(values) / len(values)
```

### Задачи

1. **coverage.py (3 балла):** Настройте `pyproject.toml` для измерения
   покрытия с `branch = true` и `source = ["src"]`. Запустите тесты с
   покрытием и добейтесь минимум 90% branch coverage.

2. **pytest-cov (2 балла):** Настройте `--cov-fail-under=90` в
   `pyproject.toml`.

3. **GitHub Actions (5 баллов):** Создайте `.github/workflows/ci.yml`:
   - Матричное тестирование на Python 3.10, 3.11, 3.12
   - Линтинг ruff
   - Проверка типов mypy
   - Загрузка покрытия на Codecov (или вывод в summary)
   - Бейдж в README.md

4. **Pre-commit (3 балла):** Настройте `.pre-commit-config.yaml` с:
   - `trailing-whitespace`, `end-of-file-fixer`
   - `ruff` (линтер + форматтер)
   - `mypy`
   - Локальный хук с `pytest` на pre-push

5. **Тесты (3 балла):** Напишите тесты для всех функций из `math_utils.py`
   с параметризацией, включая краевые случаи (пустой список, отрицательные
   числа, ноль).

### Критерии оценки
- Все тесты проходят
- Покрытие ≥ 90% (branch)
- CI-файл валиден и содержит матрицу версий Python
- Pre-commit хуки настроены и проходят
- README.md содержит бейджи

---

## Дополнительные материалы

### Книги
- David Farley, *Modern Software Engineering* (Addison-Wesley, 2021)
  — Глава 13: «Continuous Integration».
- Jez Humble, David Farley, *Continuous Delivery* (Addison-Wesley, 2010)
  — Классическая книга о CI/CD.

### Документация
- [coverage.py Documentation](https://coverage.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pre-commit Documentation](https://pre-commit.com/)
- [Codecov Documentation](https://docs.codecov.com/)

### Статьи
- Martin Fowler, *Continuous Integration* (2006, updated 2024), martinfowler.com
- Brian Okken, *Why 100% Code Coverage is Not the Goal*, pragmaticbooks.com
- Hynek Schlawack, *Python Testing with pytest and CI*, hynek.me

### Инструменты
- `coverage xml` — экспорт в формат Cobertura для CI
- `coverage json --pretty-print` — JSON-отчёт
- `coverage report --fail-under=80` — падать при низком покрытии
- `act` — локальный запуск GitHub Actions: `act push`
- [Codecov](https://codecov.io/) — бесплатный хостинг отчётов покрытия для OSS
- [Coveralls](https://coveralls.io/) — альтернатива Codecov