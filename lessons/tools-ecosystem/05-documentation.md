---
title: "Документирование кода: docstrings, Sphinx и MkDocs"
order: 5
tags: ["документация", "docstrings", "sphinx", "mkdocs", "read-the-docs"]
prerequisites: "Базовый Python, модули"
objective: "Освоить инструменты документирования Python-кода"
---

# Документирование кода: docstrings, Sphinx и MkDocs

## Введение

### 🎯 Цель урока

Освоить полный цикл документирования Python-проекта: от docstrings в коде до генерации статического сайта документации через Sphinx и MkDocs и публикации на Read the Docs. После этого урока вы сможете создавать профессиональную документацию, которая живёт рядом с кодом.

### 📋 Предпосылки

- Уверенный Python: функции, классы, модули, пакеты
- Понимание структуры Python-проекта
- Базовое знание Markdown

### Почему документация важна

> «Код говорит как, комментарии говорят почему.» — Джефф Этвуд

Хорошая документация отвечает на три вопроса:
1. **Что** делает этот код? (docstrings, описание модуля)
2. **Как** его использовать? (примеры, туториалы)
3. **Почему** он написан именно так? (комментарии к сложным решениям)

---

## Основная часть

### 1. Docstrings: PEP 257 и стили

Docstring — это строковый литерал, который идёт сразу после определения функции, класса, метода или модуля. Он доступен через `help()` и `.__doc__`.

```python
def add(a: int, b: int) -> int:
    """Складывает два целых числа и возвращает результат."""
    return a + b

# Доступ к docstring
print(add.__doc__)  # "Складывает два целых числа и возвращает результат."
help(add)           # Интерактивная справка
```

#### PEP 257 — базовые правила

```python
# Однострочный docstring: ТОЧКА в конце, ОДНА строка
def is_even(n: int) -> bool:
    """Возвращает True, если число чётное."""
    return n % 2 == 0

# Многострочный docstring: однострочное резюме, пустая строка, детали
def connect_to_database(
    host: str,
    port: int = 5432,
    database: str = "postgres",
    user: str = "postgres",
    password: str = "",
) -> object:
    """Устанавливает соединение с базой данных PostgreSQL.

    Использует psycopg2 для подключения. При ошибке соединения
    повторяет попытку до 3 раз с экспоненциальной задержкой.

    Args:
        host: Адрес сервера базы данных.
        port: Порт сервера (по умолчанию 5432).
        database: Имя базы данных.
        user: Имя пользователя.
        password: Пароль пользователя.

    Returns:
        Объект соединения psycopg2.

    Raises:
        ConnectionError: Если не удалось подключиться после 3 попыток.
    """
    ...
```

#### Google Style — самый популярный

```python
def process_data(
    data: list[dict[str, object]],
    *,
    filters: list[str] | None = None,
    sort_by: str | None = None,
    limit: int | None = None,
) -> list[dict[str, object]]:
    """Обрабатывает список записей с фильтрацией, сортировкой и лимитом.

    Применяет фильтры, затем сортирует, затем обрезает до limit.
    Фильтры имеют формат "field=value" и поддерживают простые
    операторы сравнения: =, >, <, >=, <=.

    Args:
        data: Список словарей с данными для обработки.
        filters: Список фильтров в формате "field=value".
            Если None — фильтрация не применяется.
        sort_by: Имя поля для сортировки. Если None — без сортировки.
        limit: Максимальное количество возвращаемых записей.
            Если None — возвращаются все.

    Returns:
        Обработанный список словарей.

    Raises:
        ValueError: Если формат фильтра некорректен.

    Examples:
        >>> process_data(
        ...     [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}],
        ...     filters=["age>25"],
        ...     sort_by="name",
        ... )
        [{"name": "Alice", "age": 30}]
    """
    ...
```

```python
class DataPipeline:
    """Конвейер обработки данных с настраиваемыми стадиями.

    Каждая стадия — это функция, принимающая данные и возвращающая
    обработанные данные. Стадии выполняются последовательно.

    Attributes:
        stages: Список функций-стадий.
        name: Имя конвейера для логирования.

    Example:
        >>> pipeline = DataPipeline("etl")
        >>> pipeline.add_stage(extract)
        >>> pipeline.add_stage(transform)
        >>> pipeline.add_stage(load)
        >>> pipeline.run(raw_data)
    """

    def __init__(self, name: str) -> None:
        """Инициализирует конвейер.

        Args:
            name: Имя конвейера.
        """
        self.name = name
        self.stages: list[callable] = []

    def add_stage(self, stage: callable) -> None:
        """Добавляет стадию в конвейер.

        Args:
            stage: Функция-обработчик. Должна принимать один аргумент
                (данные) и возвращать обработанные данные.
        """
        self.stages.append(stage)

    def run(self, data: object) -> object:
        """Запускает конвейер на данных.

        Args:
            data: Входные данные любого типа.

        Returns:
            Результат обработки после всех стадий.
        """
        result = data
        for stage in self.stages:
            result = stage(result)
        return result
```

#### NumPy/SciPy Style — для научных проектов

```python
def calculate_statistics(
    values: list[float],
    axis: int | None = None,
    ddof: int = 1,
) -> dict[str, float]:
    """Вычисляет описательную статистику для массива значений.

    Parameters
    ----------
    values : list of float
        Входные значения для анализа.
    axis : int or None, optional
        Ось, по которой вычисляется статистика. None означает все значения.
    ddof : int, optional
        Дельта степеней свободы для стандартного отклонения (по умолчанию 1).

    Returns
    -------
    dict
        Словарь с ключами:
            * "mean" : float — среднее арифметическое
            * "std" : float — стандартное отклонение
            * "median" : float — медиана
            * "min" : float — минимальное значение
            * "max" : float — максимальное значение

    Raises
    ------
    ValueError
        Если values пуст.

    See Also
    --------
    numpy.mean, numpy.std, numpy.median : Аналогичные функции NumPy.

    Notes
    -----
    Использует Welford's algorithm для численной стабильности.

    Examples
    --------
    >>> calculate_statistics([1.0, 2.0, 3.0, 4.0, 5.0])
    {"mean": 3.0, "std": 1.58, "median": 3.0, "min": 1.0, "max": 5.0}
    """
    ...
```

#### Sphinx Style — для использования с Sphinx

```python
def authenticate(username: str, password: str) -> dict[str, str]:
    """Аутентифицирует пользователя по логину и паролю.

    :param username: Имя пользователя.
    :type username: str
    :param password: Пароль (не хэшированный).
    :type password: str
    :returns: Словарь с токеном и информацией о пользователе.
    :rtype: dict
    :raises AuthenticationError: Если логин или пароль неверны.
    :raises ConnectionError: Если сервер недоступен.

    .. code-block:: python

        result = authenticate("alice", "secret123")
        print(result["token"])
    """
    ...
```

#### Сравнение стилей docstrings

| Критерий | Google Style | NumPy Style | Sphinx Style |
|----------|:---:|:---:|:---:|
| Читаемость в коде | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Поддержка Sphinx | ✅ (napoleon) | ✅ (napoleon) | ✅ (нативная) |
| Поддержка MkDocs | ✅ (mkdocstrings) | ✅ (mkdocstrings) | ⚠️ (частично) |
| Популярность | Очень высокая | Научное сообщество | Легаси-проекты |
| Многострочные описания | Удобно | Удобно | Неудобно |
| Рекомендация | **Для новых проектов** | Data Science | Sphinx-проекты |

### 2. Sphinx — генератор документации

Sphinx — стандарт де-факто для документации Python-проектов. Он используется для документации самого Python, Django, Flask, SQLAlchemy и тысяч других проектов.

#### Установка и инициализация

```bash
pip install sphinx sphinx-rtd-theme

# Создание структуры документации
mkdir docs
cd docs
sphinx-quickstart

# Интерактивные вопросы:
# > Separate source and build directories? yes
# > Project name: MyProject
# > Author: Your Name
# > Version: 0.1.0
# > Language: ru
```

#### Структура после `sphinx-quickstart`

```
docs/
├── source/
│   ├── _static/          # CSS, изображения
│   ├── _templates/       # Кастомные шаблоны
│   ├── conf.py           # Конфигурация
│   └── index.rst         # Главная страница
├── build/                # Сгенерированный HTML
├── Makefile              # Linux/macOS
└── make.bat              # Windows
```

#### `conf.py` — настройка Sphinx

```python
# docs/source/conf.py
import os
import sys
sys.path.insert(0, os.path.abspath("../.."))

project = "MyProject"
copyright = "2024, Your Name"
author = "Your Name"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",       # Автоматическая генерация из docstrings
    "sphinx.ext.napoleon",      # Google/NumPy стиль docstrings
    "sphinx.ext.viewcode",      # Ссылки на исходный код
    "sphinx.ext.intersphinx",   # Перекрёстные ссылки на другие проекты
    "sphinx.ext.autosummary",   # Автоматические summary-таблицы
    "sphinx.ext.todo",          # Поддержка .. todo:: директив
    "sphinx.ext.coverage",      # Проверка покрытия документации
]

# Napoleon settings (Google/NumPy style)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# Intersphinx — ссылки на документацию других проектов
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("https://docs.djangoproject.com/en/stable/", None),
}

# Тема
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Порядок элементов в документации
autodoc_member_order = "bysource"  # или "alphabetical"
autodoc_typehints = "description"  # типы в описании, а не в сигнатуре
```

#### reStructuredText (RST) — базовый синтаксис

```rst
Главная страница
===============

.. toctree::
   :maxdepth: 2
   :caption: Содержание

   installation
   usage
   api
   contributing

Введение
--------

Добро пожаловать в документацию **MyProject**!

.. code-block:: python

    from myproject import DataPipeline

    pipeline = DataPipeline("etl")
    pipeline.run(data)

.. warning::

    Это альфа-версия. API может измениться.

.. note::

    Полный список изменений в :doc:`changelog`.

.. seealso::

    - :ref:`installation-guide`
    - `Python Packaging Guide <https://packaging.python.org>`_
```

#### Автодокументирование кода

```rst
API Reference
=============

.. automodule:: myproject.data
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: myproject.DataPipeline
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: myproject.process_data
```

#### Сборка документации

```bash
# Linux/macOS
cd docs
make html

# Windows
cd docs
.\make.bat html

# Открыть результат
# docs/build/html/index.html
```

### 3. MkDocs + mkdocstrings — лёгкая альтернатива

MkDocs — генератор статической документации на Markdown. С `mkdocstrings` он может извлекать документацию прямо из docstrings, как Sphinx.

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]

# Создание проекта
mkdocs new myproject-docs
cd myproject-docs
```

#### `mkdocs.yml` — конфигурация

```yaml
site_name: MyProject
site_description: "Документация MyProject"
site_author: "Your Name"
repo_url: "https://github.com/user/myproject"
repo_name: "user/myproject"

theme:
  name: material
  language: ru
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Тёмная тема
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Светлая тема
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [../src]
          options:
            show_source: true
            show_root_heading: true
            heading_level: 2
            show_category_heading: true
            docstring_style: google
            members_order: source
            separate_signature: true
            show_signature_annotations: true
            signature_crossrefs: true
            merge_init_into_class: true

markdown_extensions:
  - admonition
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.details
  - toc:
      permalink: true

nav:
  - Главная: index.md
  - Установка: installation.md
  - Руководство:
      - Быстрый старт: guide/quickstart.md
      - Конфигурация: guide/configuration.md
  - API:
      - Обзор: api/index.md
      - DataPipeline: api/pipeline.md
      - Хранилище: api/store.md
  - Разработка: contributing.md
```

#### Markdown с автодокументацией

````markdown
# API Reference

## DataPipeline

::: myproject.pipeline.DataPipeline
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - __init__
        - add_stage
        - run

## Функции обработки

::: myproject.processing
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - filter_by
        - group_by
        - transform
````

#### Запуск

```bash
# Локальный сервер с горячей перезагрузкой
mkdocs serve

# Сборка статического сайта
mkdocs build

# Публикация на GitHub Pages
mkdocs gh-deploy
```

### 4. Doctest — тесты в документации

Doctest проверяет, что примеры кода в docstrings действительно работают. Это документация, которая не устаревает.

```python
def fibonacci(n: int) -> list[int]:
    """Генерирует последовательность Фибоначчи до n.

    >>> fibonacci(0)
    []
    >>> fibonacci(1)
    [0]
    >>> fibonacci(5)
    [0, 1, 1, 2, 3]
    >>> fibonacci(10)
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    Отрицательные числа не поддерживаются:
    >>> fibonacci(-1)
    Traceback (most recent call last):
        ...
    ValueError: n must be non-negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return []
    if n == 1:
        return [0]

    result = [0, 1]
    for _ in range(2, n):
        result.append(result[-1] + result[-2])
    return result
```

Запуск doctest:

```bash
# Запуск doctest для модуля
python -m doctest mymodule.py

# Детальный вывод
python -m doctest -v mymodule.py

# В pytest
pytest --doctest-modules
```

### 5. Read the Docs — хостинг документации

Read the Docs (RTD) бесплатно хостит документацию для open-source проектов. Он автоматически пересобирает документацию при каждом push в репозиторий.

#### `.readthedocs.yaml`

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```

### 6. Сравнение с экосистемами других языков

#### Java: Javadoc

| Аспект | Python | Java (Javadoc) |
|--------|--------|----------------|
| Синтаксис | docstrings (строки) | `/** ... */` комментарии |
| Теги | Google/NumPy/Sphinx стили | `@param`, `@return`, `@throws` |
| Генератор | Sphinx / MkDocs | javadoc |
| Вывод | HTML / PDF | HTML |
| Примеры в доке | Doctest | Нет встроенного |

```java
/**
 * Вычисляет последовательность Фибоначчи.
 *
 * @param n  количество чисел в последовательности
 * @return   список чисел Фибоначчи
 * @throws   IllegalArgumentException если n отрицательное
 */
public List<Integer> fibonacci(int n) {
    ...
}
```

#### C++: Doxygen

| Аспект | Python | C++ (Doxygen) |
|--------|--------|---------------|
| Синтаксис | docstrings | `///` или `/** */` |
| Поддержка языков | Python | C++, C, Java, Python, ... |
| Диаграммы | Через расширения | Встроенные (Graphviz) |
| Сложность настройки | Низкая | Средняя |

```cpp
/// @brief Вычисляет последовательность Фибоначчи.
/// @param n Количество чисел.
/// @return Вектор чисел Фибоначчи.
/// @throws std::invalid_argument если n < 0.
std::vector<int> fibonacci(int n) {
    ...
}
```

#### JavaScript: JSDoc

| Аспект | Python | JavaScript (JSDoc) |
|--------|--------|-------------------|
| Синтаксис | docstrings | `/** ... */` |
| Теги | Google Style | `@param`, `@returns`, `@throws` |
| Генератор | Sphinx / MkDocs | JSDoc / TypeDoc |
| Типы | Type hints | JSDoc types / TypeScript |

```javascript
/**
 * Вычисляет последовательность Фибоначчи.
 * @param {number} n - Количество чисел.
 * @returns {number[]} Массив чисел Фибоначчи.
 * @throws {Error} Если n отрицательное.
 */
function fibonacci(n) {
    ...
}
```

### 7. ✅ Идиоматичное использование

```python
# ✅ ПРАВИЛЬНО: docstring для КАЖДОЙ публичной функции/класса/модуля
"""Модуль для обработки пользовательских данных.

Предоставляет классы и функции для загрузки, валидации
и сохранения пользовательских профилей.
"""

# ✅ ПРАВИЛЬНО: Google Style для новых проектов
def validate_email(email: str) -> bool:
    """Проверяет корректность email-адреса.

    Args:
        email: Email-адрес для проверки.

    Returns:
        True, если email корректен, иначе False.

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid")
        False
    """
    ...

# ✅ ПРАВИЛЬНО: примеры в docstrings, проверяемые через doctest
# ✅ ПРАВИЛЬНО: типы в docstrings, даже если есть type hints
# ✅ ПРАВИЛЬНО: документировать исключения (Raises)
```

### 8. ❌ Антипаттерны

```python
# ❌ НЕПРАВИЛЬНО: нет docstring
def process(x):
    return x * 2

# ❌ НЕПРАВИЛЬНО: docstring повторяет сигнатуру
def add(a: int, b: int) -> int:
    """Принимает a и b, возвращает int."""
    return a + b

# ❌ НЕПРАВИЛЬНО: устаревшие примеры
def get_user(user_id: int) -> dict:
    """Возвращает пользователя.

    >>> get_user(1)
    {"name": "Alice", "age": 25}  # Код изменился, пример — нет
    """
    return {"id": 1, "name": "Alice"}  # Не совпадает с примером!

# ❌ НЕПРАВИЛЬНО: docstring только на английском в русскоязычном проекте
# Если команда русскоязычная — пишите документацию на русском

# ❌ НЕПРАВИЛЬНО: документировать очевидное
def get_name(self) -> str:
    """Получает имя. Возвращает имя. Это геттер для имени."""
    return self._name
```

### 9. Инструменты проверки документации

```bash
# pydocstyle — проверка наличия и формата docstrings
pip install pydocstyle
pydocstyle src/

# interrogate — проверка покрытия документации
pip install interrogate
interrogate src/ --fail-under 80

# ruff — включает правила pydocstyle (D)
ruff check --select D src/
```

```toml
# pyproject.toml — настройка проверки документации
[tool.ruff.lint]
select = [
    "D",  # pydocstyle rules
]

[tool.ruff.lint.pydocstyle]
convention = "google"  # или "numpy", "pep257"

[tool.interrogate]
ignore-init-module = true
ignore-init-method = true
fail-under = 80
```

---

## Практическое задание

### Задача: полный цикл документирования

1. **Создайте проект** с кодом для документирования:

```bash
mkdir docs-workshop
cd docs-workshop
python -m venv .venv
source .venv/bin/activate
```

2. **Создайте структуру пакета**:

```bash
mkdir -p src/taskmanager
touch src/taskmanager/__init__.py
```

3. **Напишите модуль `src/taskmanager/core.py`** с полными docstrings:

```python
"""Модуль ядра TaskManager — системы управления задачами.

Предоставляет основные классы и функции для создания,
обновления и отслеживания задач.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TypedDict


class Priority(Enum):
    """Приоритет задачи."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskDict(TypedDict, total=False):
    """Словарь с данными задачи."""

    id: int
    title: str
    description: str
    priority: Priority
    created_at: datetime
    completed: bool


class Task:
    """Задача в системе управления.

    Представляет одну задачу с заголовком, описанием,
    приоритетом и статусом выполнения.

    Attributes:
        id: Уникальный идентификатор задачи.
        title: Заголовок задачи.
        description: Подробное описание.
        priority: Приоритет (LOW, MEDIUM, HIGH, CRITICAL).
        created_at: Дата и время создания.
        completed: Статус выполнения.

    Example:
        >>> task = Task("Написать тесты", priority=Priority.HIGH)
        >>> task.title
        'Написать тесты'
        >>> task.completed
        False
        >>> task.mark_completed()
        >>> task.completed
        True
    """

    _id_counter: int = 0

    def __init__(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
    ) -> None:
        """Создаёт новую задачу.

        Args:
            title: Заголовок задачи (не может быть пустым).
            description: Подробное описание.
            priority: Приоритет задачи.

        Raises:
            ValueError: Если title пуст.
        """
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        Task._id_counter += 1
        self.id: int = Task._id_counter
        self.title: str = title
        self.description: str = description
        self.priority: Priority = priority
        self.created_at: datetime = datetime.now()
        self.completed: bool = False

    def mark_completed(self) -> None:
        """Отмечает задачу как выполненную."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Отмечает задачу как невыполненную."""
        self.completed = False

    def to_dict(self) -> TaskDict:
        """Сериализует задачу в словарь.

        Returns:
            Словарь с данными задачи.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at,
            "completed": self.completed,
        }

    def __repr__(self) -> str:
        """Возвращает строковое представление задачи."""
        status = "✓" if self.completed else "☐"
        return f"Task({self.id}, {status} {self.title!r})"


class TaskManager:
    """Менеджер задач.

    Управляет коллекцией задач: создание, удаление, фильтрация,
    сортировка и поиск.

    Attributes:
        tasks: Список всех задач.

    Example:
        >>> manager = TaskManager()
        >>> manager.add_task("Написать документацию", priority=Priority.HIGH)
        >>> manager.add_task("Написать тесты")
        >>> len(manager.get_pending())
        2
    """

    def __init__(self) -> None:
        """Инициализирует пустой менеджер задач."""
        self.tasks: list[Task] = []

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
    ) -> Task:
        """Добавляет новую задачу.

        Args:
            title: Заголовок задачи.
            description: Описание задачи.
            priority: Приоритет.

        Returns:
            Созданная задача.

        Raises:
            ValueError: Если title пуст.
        """
        task = Task(title, description, priority)
        self.tasks.append(task)
        return task

    def remove_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID.

        Args:
            task_id: Идентификатор задачи.

        Returns:
            True, если задача удалена; False, если не найдена.
        """
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_task(self, task_id: int) -> Task | None:
        """Находит задачу по ID.

        Args:
            task_id: Идентификатор задачи.

        Returns:
            Задача или None, если не найдена.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_pending(self) -> list[Task]:
        """Возвращает список невыполненных задач.

        Returns:
            Список невыполненных задач, отсортированный по приоритету (по убыванию).
        """
        return sorted(
            [t for t in self.tasks if not t.completed],
            key=lambda t: t.priority.value,
            reverse=True,
        )

    def get_completed(self) -> list[Task]:
        """Возвращает список выполненных задач.

        Returns:
            Список выполненных задач.
        """
        return [t for t in self.tasks if t.completed]

    def get_by_priority(self, priority: Priority) -> list[Task]:
        """Фильтрует задачи по приоритету.

        Args:
            priority: Приоритет для фильтрации.

        Returns:
            Список задач с указанным приоритетом.
        """
        return [t for t in self.tasks if t.priority == priority]

    def to_dict_list(self) -> list[TaskDict]:
        """Сериализует все задачи в список словарей.

        Returns:
            Список словарей с данными задач.
        """
        return [task.to_dict() for task in self.tasks]

    def __len__(self) -> int:
        """Возвращает количество задач."""
        return len(self.tasks)

    def __repr__(self) -> str:
        """Возвращает строковое представление менеджера."""
        return f"TaskManager({len(self)} tasks)"
```

4. **Добавьте doctest-примеры** и запустите их:

```bash
python -m doctest src/taskmanager/core.py -v
```

5. **Настройте Sphinx**:

```bash
mkdir docs
cd docs
sphinx-quickstart
# Настройте conf.py с autodoc и napoleon
```

Создайте `docs/source/api.rst`:

```rst
API Reference
=============

.. automodule:: taskmanager.core
   :members:
   :undoc-members:
   :show-inheritance:
```

Соберите и откройте документацию:

```bash
make html
# Откройте build/html/index.html
```

6. **(Опционально)** Настройте MkDocs с Material и сравните:

```bash
mkdocs new mkdocs-docs
# Настройте mkdocs.yml с mkdocstrings
mkdocs serve
```

---

## Дополнительные материалы

### 📚 Официальная документация

- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/) — базовые правила
- [Sphinx documentation](https://www.sphinx-doc.org/) — официальное руководство
- [MkDocs documentation](https://www.mkdocs.org/) — генератор на Markdown
- [mkdocstrings](https://mkdocstrings.github.io/) — автодокументация для MkDocs
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) — стиль Google
- [NumPy Style Guide](https://numpydoc.readthedocs.io/en/latest/format.html) — стиль NumPy

### 🎥 Видео и статьи

- [Documenting Python Code (Real Python)](https://realpython.com/documenting-python-code/) — полный гид
- [Write the Docs](https://www.writethedocs.org/) — сообщество документаторов

### 🔗 Связанные уроки

- **Урок 3**: Линтинг и форматирование — pydocstyle правила в ruff
- **Урок 4**: Статическая типизация — типы в документации

### 💡 Ключевые выводы

1. **Docstrings** — первоисточник документации, пишите их сразу
2. **Google Style** — лучший выбор для новых проектов
3. **Sphinx** — стандарт для крупных проектов (Python, Django, Flask)
4. **MkDocs + Material** — лучший выбор для небольших/средних проектов
5. **Doctest** — документация, которая не устаревает
6. **Read the Docs** — бесплатный хостинг для open-source
7. Документируйте **почему**, а не **что** (это видно из кода)
8. Примеры в документации — самый ценный раздел для пользователей