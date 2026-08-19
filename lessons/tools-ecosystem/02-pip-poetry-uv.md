---
title: "Менеджеры пакетов: pip, Poetry и uv"
order: 2
tags: ["pip", "poetry", "uv", "зависимости", "pyproject.toml"]
prerequisites: "Урок 1"
objective: "Освоить современные инструменты управления зависимостями: pip, Poetry, uv"
---

# Менеджеры пакетов: pip, Poetry и uv

## Введение

### 🎯 Цель урока

Освоить весь спектр инструментов управления зависимостями в Python: от классического `pip` до современного `uv` и полнофункционального `poetry`. После этого урока вы сможете выбирать правильный менеджер пакетов под задачу, понимать `pyproject.toml` и управлять сложными деревьями зависимостей.

### 📋 Предпосылки

- Урок 1: Виртуальные окружения
- Понимание семантического версионирования (`MAJOR.MINOR.PATCH`)
- Уверенная работа с терминалом

### Эволюция управления зависимостями в Python

```
2008: pip (easy_install replacement)
2011: virtualenv + pip становится стандартом
2016: Pipfile/pipenv (неудачная попытка)
2017: PEP 517/518 — pyproject.toml
2018: Poetry (lock-файлы, как в npm/Cargo)
2019: pip-tools (pip-compile + pip-sync)
2020: PEP 621 — метаданные в pyproject.toml
2023: uv (Rust-based, в 10-100x быстрее pip)
2024: uv становится мейнстримной альтернативой pip
```

---

## Основная часть

### 1. `pip` — классика

`pip` (Pip Installs Packages) — стандартный менеджер пакетов Python. Устанавливается вместе с Python и не требует дополнительных действий.

#### Основные команды

```bash
# Установка пакета
pip install requests

# Установка конкретной версии
pip install flask==3.0.0

# Установка диапазона версий
pip install "django>=4.2,<5.0"

# Установка из файла
pip install -r requirements.txt

# Удаление
pip uninstall requests

# Просмотр установленных пакетов
pip list
pip list --outdated       # устаревшие
pip list --format=json    # машиночитаемый вывод

# Информация о пакете
pip show requests

# Поиск пакетов (устарело, используйте pypi.org)
pip search requests  # отключено на PyPI

# Заморозка точных версий
pip freeze > requirements.txt

# Проверка целостности установленных пакетов
pip check
```

#### `requirements.txt` — формат и лучшие практики

```
# requirements.txt — production зависимости
django>=4.2,<5.0          # диапазон версий
requests==2.31.0          # точная версия (заморожена)
gunicorn~=21.2.0          # совместимый релиз (>=21.2.0, <22.0)
psycopg2-binary==2.9.9; platform_system != "Windows"  # условная зависимость
uvicorn[standard]==0.27.0  # с extras

# Зависимости из Git
git+https://github.com/user/repo.git@v1.0.0#egg=package

# Локальный пакет
-e ./local-package
```

#### Структура проекта с `requirements`

```
myproject/
├── .venv/
├── requirements/
│   ├── base.txt          # общие зависимости
│   ├── production.txt    # продакшен
│   ├── development.txt   # разработка
│   └── test.txt          # тестирование
├── src/
│   └── myproject/
└── pyproject.toml
```

Пример наследования через `-r`:

```
# requirements/production.txt
-r base.txt
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

```
# requirements/development.txt
-r production.txt
black==24.1.0
ruff==0.2.0
mypy==1.8.0
pytest==8.0.0
```

### 2. `pip-tools` — детерминированные зависимости

`pip-tools` решает главную проблему `pip freeze`: он генерирует точный lock-файл из высокоуровневых зависимостей.

```bash
pip install pip-tools
```

#### Workflow

```bash
# 1. Описываем верхнеуровневые зависимости в requirements.in
cat > requirements.in << 'EOF'
django>=4.2,<5.0
requests
gunicorn
EOF

# 2. Генерируем точный requirements.txt
pip-compile requirements.in

# Результат в requirements.txt:
# django==4.2.11
# requests==2.31.0
# gunicorn==21.2.0
# ... все транзитивные зависимости с точными версиями

# 3. Синхронизируем окружение с lock-файлом
pip-sync requirements.txt
# Установит только то, что в requirements.txt, удалит лишнее!
```

#### Многослойная структура

```bash
# requirements/base.in
django>=4.2,<5.0
requests

# requirements/dev.in
-c base.txt
black
ruff
pytest

# Генерация
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt

# Установка
pip-sync requirements/dev.txt
```

### 3. `pyproject.toml` — новый стандарт (PEP 517/518/621)

`pyproject.toml` — это единый файл конфигурации для Python-проекта. Он заменяет `setup.py`, `setup.cfg`, `requirements.txt`, `MANIFEST.in`, конфигурацию инструментов и многое другое.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myproject"
version = "0.1.0"
description = "Пример проекта с pyproject.toml"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "you@example.com"},
]
keywords = ["example", "tutorial"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "django>=4.2,<5.0",
    "requests>=2.31,<3.0",
    "gunicorn>=21.2,<22.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pytest>=8.0",
    "pre-commit>=3.6",
]
test = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "factory-boy>=3.3",
]
docs = [
    "sphinx>=7.2",
    "furo>=2024.1",
]

[project.urls]
Homepage = "https://github.com/user/myproject"
Documentation = "https://myproject.readthedocs.io"
Repository = "https://github.com/user/myproject.git"
Issues = "https://github.com/user/myproject/issues"

[project.scripts]
myproject-cli = "myproject.cli:main"

[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
```

Установка из `pyproject.toml`:

```bash
# Установка production зависимостей
pip install .

# Установка с dev зависимостями
pip install ".[dev]"

# Установка всех опциональных зависимостей
pip install ".[dev,test,docs]"
```

### 4. Poetry — управление зависимостями и публикация

Poetry — это менеджер зависимостей и пакетов с детерминированными сборками через `poetry.lock`. Вдохновлён `npm`/`yarn` (JS) и `Cargo` (Rust).

```bash
# Установка Poetry
# Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Проверка
poetry --version
```

#### Создание проекта

```bash
# Новый проект
poetry new myproject

# Структура:
# myproject/
# ├── myproject/
# │   └── __init__.py
# ├── tests/
# │   └── __init__.py
# ├── pyproject.toml
# └── README.md

# Инициализация в существующем проекте
cd existing-project
poetry init
```

#### Управление зависимостями

```bash
# Добавление production зависимости
poetry add django requests

# Добавление dev зависимости
poetry add --group dev black ruff mypy pytest

# Добавление опциональной группы
poetry add --group docs sphinx

# Удаление
poetry remove django

# Установка всех зависимостей (по lock-файлу)
poetry install

# Установка без dev-зависимостей
poetry install --only main

# Обновление зависимостей
poetry update
poetry update django  # только один пакет

# Просмотр дерева зависимостей
poetry show --tree

# Блокировка зависимостей
poetry lock
```

#### `pyproject.toml` с Poetry

```toml
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "Пример Poetry-проекта"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "myproject"}]

[tool.poetry.dependencies]
python = "^3.10"
django = "^4.2"
requests = "^2.31"

[tool.poetry.group.dev.dependencies]
black = "^24.0"
ruff = "^0.2.0"
mypy = "^1.8.0"
pytest = "^8.0"

[tool.poetry.group.test.dependencies]
pytest-cov = "^4.1"
factory-boy = "^3.3"

[tool.poetry.scripts]
myproject-cli = "myproject.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### Публикация пакета

```bash
# Сборка
poetry build

# Публикация на PyPI
poetry publish

# Публикация на тестовый PyPI
poetry publish -r test-pypi
```

### 5. `uv` — новый сверхбыстрый менеджер пакетов

`uv` — это молниеносный менеджер пакетов и виртуальных окружений на Rust от создателей `ruff`. Он в 10-100 раз быстрее `pip`.

```bash
# Установка uv
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Или через pip
pip install uv
```

#### Основные команды

```bash
# Создание виртуального окружения (как python -m venv)
uv venv

# Установка пакетов (как pip install)
uv pip install requests flask

# Установка из requirements
uv pip install -r requirements.txt

# Компиляция requirements.in (как pip-compile)
uv pip compile requirements.in -o requirements.txt

# Синхронизация (как pip-sync)
uv pip sync requirements.txt

# Просмотр установленных пакетов
uv pip list

# Заморозка
uv pip freeze
```

#### Сравнение скорости

```bash
# Тест: установка django + зависимости
# pip
time pip install django  # ~5-10 секунд

# uv
time uv pip install django  # ~0.5-1 секунда
```

#### Управление проектом через uv

```bash
# Инициализация проекта
uv init myproject

# Добавление зависимостей
uv add django requests

# Добавление dev-зависимостей
uv add --dev black ruff pytest

# Установка по lock-файлу
uv sync

# Запуск скрипта в окружении
uv run python app.py

# Запуск инструмента без установки
uvx ruff check .
uvx black --check .
```

### 6. `pipx` — изолированные CLI-инструменты

`pipx` устанавливает Python-приложения в изолированные окружения и делает их доступными глобально.

```bash
# Установка pipx
pip install pipx
pipx ensurepath

# Установка инструментов
pipx install black
pipx install ruff
pipx install poetry
pipx install httpie

# Теперь доступны глобально:
black --version
ruff --version

# Запуск без установки
pipx run pycowsay "Hello, Python!"

# Список установленных инструментов
pipx list

# Обновление
pipx upgrade-all

# Удаление
pipx uninstall black
```

### 7. Сравнение менеджеров пакетов

| Критерий | pip | pip-tools | Poetry | uv |
|----------|-----|-----------|--------|-----|
| Скорость | Базовая | Базовая | Средняя | **Очень высокая** |
| Lock-файл | ❌ | ✅ | ✅ | ✅ |
| Разрешение зависимостей | Простое | Полное | Полное (SAT) | Полное |
| Управление окружением | ❌ (нужен venv) | ❌ | ✅ | ✅ |
| Публикация пакетов | ✅ (twine) | ❌ | ✅ | ❌ (пока) |
| pyproject.toml | PEP 621 | ❌ | Свой формат | PEP 621 |
| Кривая обучения | Низкая | Средняя | Средняя | Низкая |
| Зрелость | 15+ лет | 8+ лет | 6+ лет | 1+ год |

### 8. Сравнение с экосистемами других языков

#### JavaScript: npm / yarn / pnpm

| Аспект | Python | JavaScript |
|--------|--------|------------|
| Стандартный менеджер | pip | npm |
| Lock-файл | poetry.lock / uv.lock | package-lock.json / yarn.lock |
| Быстрый аналог | uv | pnpm |
| Изоляция CLI | pipx | npx |
| Манифест | pyproject.toml | package.json |
| Реестр | PyPI | npm registry |

```bash
# npm (JavaScript): инициализация и установка
npm init -y
npm install express
npm install --save-dev jest

# poetry (Python): то же самое
poetry init
poetry add fastapi
poetry add --group dev pytest
```

#### Java: Maven / Gradle

| Аспект | Python | Java |
|--------|--------|------|
| Декларация зависимостей | pyproject.toml | pom.xml / build.gradle |
| Репозиторий | PyPI | Maven Central |
| Транзитивные зависимости | ✅ | ✅ |
| Scope (compile/test/runtime) | ✅ (optional-deps) | ✅ (Maven scopes) |
| Сборка проекта | Разные инструменты | Maven/Gradle — и сборка, и зависимости |

```xml
<!-- Maven: зависимости с scope -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>
```

```toml
# Python pyproject.toml: то же через optional-dependencies
[project.optional-dependencies]
test = ["pytest>=8.0"]
```

#### Rust: Cargo

| Аспект | Python (uv) | Rust (Cargo) |
|--------|-------------|--------------|
| Манифест | pyproject.toml | Cargo.toml |
| Lock-файл | uv.lock | Cargo.lock |
| Скорость | Очень быстрая (Rust) | Очень быстрая (Rust) |
| Встроенное управление | uv (новый) | Cargo (всегда был) |

```toml
# Cargo.toml (Rust)
[package]
name = "myproject"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }
```

```toml
# pyproject.toml (Python, uv)
[project]
name = "myproject"
version = "0.1.0"
dependencies = ["fastapi>=0.109", "uvicorn>=0.27"]
```

#### C#: NuGet

| Аспект | Python | C# (NuGet) |
|--------|--------|------------|
| Манифест | pyproject.toml | .csproj / packages.config |
| Пакетный менеджер | pip/poetry/uv | nuget / dotnet CLI |
| Lock-файл | poetry.lock / uv.lock | packages.lock.json |
| Транзитивные зависимости | ✅ | ✅ |

### 9. ✅ Идиоматичное использование

```bash
# ✅ ПРАВИЛЬНО: использовать pyproject.toml для новых проектов
[project]
name = "myproject"
dependencies = ["django>=4.2,<5.0"]

# ✅ ПРАВИЛЬНО: фиксировать точные версии через lock-файл
poetry.lock  # Всегда коммитить
uv.lock      # Всегда коммитить

# ✅ ПРАВИЛЬНО: разделять production и dev зависимости
poetry add --group dev pytest
uv add --dev pytest

# ✅ ПРАВИЛЬНО: использовать pipx для CLI-инструментов
pipx install black  # вместо pip install black

# ✅ ПРАВИЛЬНО: проверять безопасность зависимостей
pip-audit
# или
safety check
```

```python
# ✅ ПРАВИЛЬНО: указывать минимальные зависимости в pyproject.toml
# вместо точных версий
dependencies = [
    "django>=4.2,<5.0",     # диапазон, совместимый с проектом
    "requests>=2.31,<3.0",  # не фиксируем патч-версию
]
```

### 10. ❌ Антипаттерны

```bash
# ❌ НЕПРАВИЛЬНО: pip freeze без структуры
pip freeze > requirements.txt
# Проблема: все транзитивные зависимости в одном файле,
# непонятно, какие — прямые, какие — транзитивные

# ❌ НЕПРАВИЛЬНО: не коммитить lock-файл
# poetry.lock и uv.lock ДОЛЖНЫ быть в Git
# Без них сборка недетерминирована

# ❌ НЕПРАВИЛЬНО: устанавливать пакеты без версий
pip install django
# Что установилось? 4.2? 5.0? Никто не знает

# ❌ НЕПРАВИЛЬНО: смешивать pip install и poetry add
# Выберите ОДИН менеджер пакетов и придерживайтесь его

# ❌ НЕПРАВИЛЬНО: жёстко фиксировать версии в pyproject.toml
dependencies = ["django==4.2.11"]  # слишком строго
# Правильно: ["django>=4.2,<5.0"]

# ❌ НЕПРАВИЛЬНО: игнорировать обновления безопасности
# Регулярно проверяйте: pip list --outdated
# Или используйте: safety check / pip-audit
```

### 11. Миграция между менеджерами

#### Из pip в Poetry

```bash
# Установить Poetry
pipx install poetry

# Создать pyproject.toml из requirements.txt
poetry init
# Или вручную добавить зависимости:
cat requirements.txt | sed 's/==/>=/' | xargs -I {} poetry add "{}"

# Сгенерировать lock-файл
poetry lock
```

#### Из pip в uv

```bash
# Установить uv
pipx install uv

# Инициализировать проект
uv init .

# Перенести зависимости из requirements.txt
uv add $(cat requirements.txt | sed 's/==.*//')

# Сгенерировать lock-файл
uv lock
```

---

## Практическое задание

### Задача: сравнение pip, Poetry и uv

1. **Создайте три идентичных проекта** в разных папках:

```bash
mkdir pkg-manager-test
cd pkg-manager-test
```

2. **Проект A — pip + pip-tools**:

```bash
mkdir pip-project && cd pip-project
python -m venv .venv && source .venv/bin/activate

# Создайте requirements.in
cat > requirements.in << 'EOF'
fastapi>=0.109
uvicorn[standard]>=0.27
pydantic>=2.5
EOF

# Скомпилируйте
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt

# Создайте main.py
cat > main.py << 'EOF'
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="pip-project")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def read_root():
    return {"manager": "pip + pip-tools"}

@app.post("/items/")
def create_item(item: Item):
    return item
EOF
```

3. **Проект B — Poetry**:

```bash
cd ../ && mkdir poetry-project && cd poetry-project
poetry init --no-interaction
poetry add fastapi "uvicorn[standard]" pydantic
poetry add --group dev pytest

# Создайте такой же main.py
```

4. **Проект C — uv**:

```bash
cd ../ && mkdir uv-project && cd uv-project
uv init
uv add fastapi "uvicorn[standard]" pydantic
uv add --dev pytest

# Создайте такой же main.py
```

5. **Сравните** для каждого проекта:

```bash
# Время установки (очистите кэш перед каждым тестом)
time pip install -r requirements.txt    # для pip
time poetry install                     # для Poetry
time uv sync                            # для uv

# Размер папки проекта
du -sh .

# Содержимое lock-файла
cat requirements.txt     # pip
cat poetry.lock          # Poetry
cat uv.lock              # uv
```

6. **Запустите приложение** в каждом проекте:

```bash
uvicorn main:app --reload
# Откройте http://127.0.0.1:8000/docs
```

7. **Задокументируйте** различия в скорости, удобстве и размере.

---

## Дополнительные материалы

### 📚 Официальная документация

- [pip documentation](https://pip.pypa.io/en/stable/) — официальное руководство по pip
- [Poetry documentation](https://python-poetry.org/docs/) — полное руководство по Poetry
- [uv documentation](https://docs.astral.sh/uv/) — документация uv
- [pyproject.toml specification (PEP 621)](https://peps.python.org/pep-0621/) — стандарт pyproject.toml
- [pip-tools documentation](https://pip-tools.readthedocs.io/) — руководство по pip-tools

### 🎥 Видео и статьи

- [Why Python's pip is not enough](https://hynek.me/articles/python-app-deps/) — Хайнек Шлавак о проблемах pip
- [uv: Python packaging in Rust](https://astral.sh/blog/uv) — блог Astral о создании uv
- [Python Dependency Management Compared](https://modelpredict.com/python-dependency-management-tools/) — сравнение инструментов

### 🔗 Связанные уроки

- **Урок 1**: Виртуальные окружения — основа для любого менеджера пакетов
- **Урок 3**: Линтинг и форматирование — инструменты, которые стоит добавить в dev-зависимости

### 🛠 Инструменты безопасности

- [pip-audit](https://pypi.org/project/pip-audit/) — аудит зависимостей на уязвимости
- [safety](https://pyup.io/safety/) — проверка безопасности пакетов
- [dependabot](https://github.com/dependabot) — автоматические PR для обновления зависимостей

### 💡 Ключевые выводы

1. **pip** — базовый инструмент, подходит для простых проектов
2. **pip-tools** — добавляет детерминизм через `pip-compile` / `pip-sync`
3. **Poetry** — полнофункциональный менеджер: зависимости + окружения + публикация
4. **uv** — сверхбыстрая альтернатива pip и pip-tools от создателей ruff
5. **pyproject.toml** — современный стандарт для всех Python-проектов
6. **pipx** — правильный способ установки CLI-инструментов
7. Всегда используйте lock-файлы и коммитите их в Git
8. Регулярно проверяйте зависимости на уязвимости