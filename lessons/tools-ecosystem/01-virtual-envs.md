---
title: "Виртуальные окружения: venv, virtualenv, Conda"
order: 1
tags: ["venv", "virtualenv", "conda", "зависимости", "изоляция"]
prerequisites: "Базовый Python, pip"
objective: "Освоить управление виртуальными окружениями для изоляции зависимостей проектов"
---

# Виртуальные окружения: venv, virtualenv, Conda

## Введение

### 🎯 Цель урока

Освоить создание, активацию и управление виртуальными окружениями Python для полной изоляции зависимостей между проектами. После этого урока вы сможете уверенно использовать `venv`, `virtualenv` и Conda-окружения, понимать их различия и выбирать правильный инструмент под задачу.

### 📋 Предпосылки

- Уверенное владение базовым синтаксисом Python
- Понимание назначения `pip` и умение устанавливать пакеты
- Знакомство с командной строкой (терминал/PowerShell)

### Проблема: ад зависимостей

Представьте два проекта на одной машине:

- **Project A** — веб-приложение на Django 3.2, требует `django==3.2.*` и `requests==2.25.*`
- **Project B** — скрипт для анализа данных, требует `django==4.2.*` и `requests==2.31.*`

Если установить всё глобально через `pip install`, пакеты перезапишут друг друга. Project A сломается, потому что Django 4.2 несовместим с его кодом. Это и есть **dependency hell** — ад зависимостей.

Решение — **виртуальные окружения**: изолированные «песочницы», где у каждого проекта свой набор пакетов и своя версия самого Python.

---

## Основная часть

### 1. `venv` — встроенное решение

Начиная с Python 3.3, модуль `venv` входит в стандартную библиотеку. Он не требует установки и покрывает 90% потребностей.

#### Создание окружения

```bash
# Linux / macOS
python3 -m venv .venv

# Windows (PowerShell)
python -m venv .venv
```

Соглашение: папка окружения называется `.venv` (с точкой), чтобы скрыть её в файловых менеджерах и не коммитить в Git.

Что создаёт `venv`:

```
.venv/
├── Include/          # Заголовочные файлы C (Windows)
├── Lib/              # Установленные пакеты (site-packages)
│   └── site-packages/
├── Scripts/          # Исполняемые файлы (Windows: python.exe, pip.exe, activate)
│   ├── activate
│   ├── activate.bat
│   ├── Activate.ps1
│   ├── python.exe
│   └── pip.exe
├── pyvenv.cfg        # Конфигурация окружения
└── .gitignore        # (если создан вручную)
```

#### Активация

```bash
# Linux / macOS (bash/zsh)
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
.venv\Scripts\activate.bat

# Windows (PowerShell — альтернатива)
.venv\Scripts\activate
```

После активации в приглашении командной строки появляется префикс `(.venv)`:

```
(.venv) user@machine:~/project$
```

Теперь `python` и `pip` указывают на версии внутри окружения:

```bash
# Проверить, какой python используется
# Linux/macOS
which python
# Windows
where python

# Проверить путь к pip
# Linux/macOS
which pip
# Windows
where pip
```

#### Деактивация

```bash
deactivate
```

#### Установка пакетов в окружение

```bash
# Активируем окружение
source .venv/bin/activate

# Устанавливаем пакеты
pip install django==4.2.0
pip install requests

# Проверяем, что установлено
pip list
pip freeze > requirements.txt
```

#### Ключевые флаги `venv`

| Флаг | Описание |
|------|----------|
| `--system-site-packages` | Дать доступ к глобальным пакетам (не рекомендуется) |
| `--symlinks` | Использовать симлинки вместо копий (по умолчанию на Linux) |
| `--copies` | Копировать файлы вместо симлинков |
| `--clear` | Очистить существующее окружение перед созданием |
| `--upgrade` | Обновить окружение до текущей версии Python |
| `--without-pip` | Не устанавливать pip (экономия места) |

```bash
# Пример: создать окружение с доступом к глобальным пакетам
python -m venv --system-site-packages .venv

# Пример: пересоздать окружение с нуля
python -m venv --clear .venv
```

### 2. `virtualenv` — расширенная альтернатива

`virtualenv` появился раньше `venv` и предлагает больше возможностей. Он не входит в стандартную библиотеку, но до сих пор популярен.

```bash
# Установка
pip install virtualenv

# Создание окружения
virtualenv .venv

# Указать конкретную версию Python
virtualenv -p python3.11 .venv

# Указать путь к интерпретатору
virtualenv -p /usr/bin/python3.12 .venv
```

#### Преимущества `virtualenv` перед `venv`

| Возможность | `venv` | `virtualenv` |
|-------------|--------|--------------|
| Встроен в Python 3.3+ | ✅ | ❌ |
| Скорость создания | Быстрее | Медленнее |
| Поддержка Python 2 | ❌ | ✅ |
| `--prompt` (кастомный префикс) | ✅ | ✅ |
| `--extra-search-dir` | ❌ | ✅ |
| Расширяемость через плагины | ❌ | ✅ |
| `--seed` (предустановка пакетов) | ❌ | ✅ |
| Встроенная поддержка активации | ✅ | ✅ |

```bash
# virtualenv: кастомный префикс в приглашении
virtualenv --prompt="(myproject)" .venv

# virtualenv: предустановить pip, setuptools, wheel
virtualenv --seed pip --seed setuptools --seed wheel .venv
```

#### Когда использовать `virtualenv`

- Нужна поддержка Python 2.7 (легаси-проекты)
- Требуется тонкая настройка поиска интерпретатора
- Вы используете плагины экосистемы `virtualenv`

Для новых проектов на Python 3 используйте `venv` — он быстрее и идёт «из коробки».

### 3. Conda-окружения для Data Science

Conda — это кроссплатформенный менеджер пакетов и окружений, изначально созданный для экосистемы Python data science. В отличие от `venv`/`virtualenv`, Conda управляет **не только Python-пакетами**, но и системными библиотеками (C, C++, Fortran).

```bash
# Создание окружения с конкретной версией Python
conda create -n myproject python=3.11

# Создание окружения с пакетами
conda create -n ds-project python=3.11 numpy pandas scipy matplotlib

# Активация
conda activate myproject

# Деактивация
conda deactivate

# Список окружений
conda env list

# Удаление окружения
conda env remove -n myproject

# Экспорт окружения в файл
conda env export > environment.yml

# Создание из файла
conda env create -f environment.yml
```

#### `environment.yml` — аналог `requirements.txt`

```yaml
name: ds-project
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy=1.26.*
  - pandas=2.1.*
  - scipy=1.11.*
  - matplotlib=3.8.*
  - pip
  - pip:
    - requests==2.31.0
    - black==24.1.0
```

#### Conda vs venv: когда что выбирать

| Критерий | `venv` | `conda` |
|----------|--------|---------|
| Размер установки | ~15 МБ | ~500 МБ+ (Miniconda) / ~3 ГБ (Anaconda) |
| Область управления | Только Python-пакеты | Python + системные библиотеки |
| Скорость разрешения зависимостей | Быстро (pip) | Медленно (SAT-решатель) |
| Научные пакеты (numpy, scipy) | Требуют компилятора | Предкомпилированные бинарники |
| Поддержка не-Python зависимостей | ❌ | ✅ |
| Кроссплатформенность | ✅ | ✅ |
| Воспроизводимость | `requirements.txt` | `environment.yml` |

**Правило выбора**: для веб-разработки и чистого Python — `venv`. Для data science, машинного обучения, проектов с C-зависимостями — Conda.

### 4. `.gitignore` и лучшие практики

#### Что НЕ коммитить

```gitignore
# Виртуальное окружение — НИКОГДА не коммитить
.venv/
venv/
env/
.env/

# Байт-код Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Переменные окружения
.env
.env.local

# Файлы IDE
.vscode/
.idea/
*.swp
*.swo
```

#### Что КОММИТИТЬ

```gitignore
# requirements.txt — всегда коммитить
!requirements.txt
!requirements-dev.txt

# pyproject.toml — всегда коммитить
!pyproject.toml

# Блокировочные файлы — всегда коммитить
!poetry.lock
!Pipfile.lock
```

#### Идиоматический workflow

```bash
# 1. Клонируем проект
git clone https://github.com/user/project.git
cd project

# 2. Создаём виртуальное окружение
python -m venv .venv

# 3. Активируем
source .venv/bin/activate  # Linux/macOS
# или .venv\Scripts\activate  # Windows

# 4. Устанавливаем зависимости
pip install -r requirements.txt

# 5. Работаем...

# 6. Деактивируем, когда закончили
deactivate
```

### 5. Сравнение с экосистемами других языков

#### Java: classpath и Maven/Gradle

В Java изоляция достигается иначе. Вместо виртуальных окружений — **classpath** и **локальные репозитории Maven** (`~/.m2/repository`). Каждый проект декларирует зависимости в `pom.xml` (Maven) или `build.gradle` (Gradle), а система сборки скачивает нужные версии JAR-файлов в общий кэш.

| Аспект | Python (`venv`) | Java (Maven/Gradle) |
|--------|-----------------|---------------------|
| Изоляция | Полная копия интерпретатора и пакетов | Версионирование JAR в общем кэше |
| Механизм | Копирование/симлинки | Локальный репозиторий + classpath |
| Размер на проект | ~20-50 МБ | Зависимости кэшируются глобально |
| Конфликт версий | Невозможен внутри окружения | Решается через dependency mediation |

```xml
<!-- Maven: зависимости декларируются в pom.xml -->
<dependencies>
    <dependency>
        <groupId>com.google.guava</groupId>
        <artifactId>guava</artifactId>
        <version>32.1.3-jre</version>
    </dependency>
</dependencies>
```

#### Node.js: `node_modules`

Node.js идёт по пути **локальных** `node_modules`: каждый проект хранит свои зависимости в папке `node_modules` внутри проекта. Это похоже на `venv` тем, что изоляция физическая. Однако `node_modules` может разрастаться до гигантских размеров (сотни мегабайт), а Python-окружения компактнее.

| Аспект | Python (`venv`) | Node.js (`npm`) |
|--------|-----------------|-----------------|
| Расположение | Отдельная папка (часто скрытая) | `node_modules/` в корне проекта |
| Совместное использование | Одно окружение на проект | Одна папка на проект |
| Размер | ~20-50 МБ | Часто 200-500 МБ+ |
| Блокировка версий | `requirements.txt` | `package-lock.json` |

```bash
# Node.js: создание проекта
npm init -y
npm install express

# node_modules появляется локально
ls node_modules/
```

#### C++: CMake и vcpkg/Conan

В C++ нет единого менеджера пакетов уровня языка. `vcpkg` (Microsoft) и `Conan` пытаются заполнить этот пробел, но изоляция окружений остаётся сложной задачей из-за системных зависимостей и ABI-несовместимости.

| Аспект | Python (`venv`) | C++ (vcpkg/Conan) |
|--------|-----------------|-------------------|
| Стандартизация | Единый механизм | Фрагментирован |
| Простота | `python -m venv .venv` | Требует настройки триплетов |
| Кроссплатформенность | Прозрачная | Зависит от компилятора и платформы |

#### Docker: изоляция уровня ОС

Docker предлагает изоляцию на уровне всей операционной системы — это «тяжёлая» альтернатива `venv`. Python-окружение внутри Docker-контейнера — распространённый паттерн для продакшена.

```dockerfile
# Dockerfile: изоляция через контейнер
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

| Аспект | `venv` | Docker |
|--------|--------|--------|
| Уровень изоляции | Python-пакеты | Полная ОС |
| Размер | ~20 МБ | ~150 МБ+ |
| Скорость запуска | Мгновенно | Секунды |
| Переносимость | Требует Python | Требует Docker |
| Продакшен | Через Docker | Нативный |

### 6. ✅ Идиоматичное использование

```bash
# ✅ ПРАВИЛЬНО: всегда создавать окружение в корне проекта
cd myproject
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ✅ ПРАВИЛЬНО: использовать .venv (с точкой) как имя папки
python -m venv .venv

# ✅ ПРАВИЛЬНО: фиксировать точные версии в requirements.txt
pip freeze > requirements.txt
# Содержимое: django==4.2.0, requests==2.31.0, ...

# ✅ ПРАВИЛЬНО: разделять production и dev зависимости
# requirements.txt      — production
# requirements-dev.txt  — pytest, black, mypy, ...
```

```python
# ✅ ПРАВИЛЬНО: проверять, что мы в виртуальном окружении
import sys

def is_venv() -> bool:
    """Проверяет, запущен ли скрипт внутри виртуального окружения."""
    return (
        hasattr(sys, 'real_prefix')          # virtualenv
        or (hasattr(sys, 'base_prefix')      # venv
            and sys.base_prefix != sys.prefix)
    )

if not is_venv():
    print("⚠️  Внимание: скрипт запущен вне виртуального окружения!")
```

### 7. ❌ Антипаттерны

```bash
# ❌ НЕПРАВИЛЬНО: глобальная установка пакетов
pip install django  # без активированного окружения

# ❌ НЕПРАВИЛЬНО: использование sudo с pip
sudo pip install flask  # может сломать системный Python

# ❌ НЕПРАВИЛЬНО: коммитить папку .venv в Git
git add .venv/  # десятки мегабайт мусора в репозитории

# ❌ НЕПРАВИЛЬНО: называть окружение venv без точки
python -m venv venv  # лучше .venv — скрытая папка

# ❌ НЕПРАВИЛЬНО: активировать чужое окружение
source ../other-project/.venv/bin/activate

# ❌ НЕПРАВИЛЬНО: устанавливать пакеты без активации
.venv/bin/pip install flask  # работает, но неидиоматично

# ❌ НЕПРАВИЛЬНО: использовать --system-site-packages без необходимости
python -m venv --system-site-packages .venv
# Глобальные пакеты «протекают» в окружение — недетерминированное поведение
```

### 8. Продвинутые техники

#### Автоматическая активация через direnv

```bash
# Установка direnv
# macOS: brew install direnv
# Linux: apt install direnv

# В корне проекта создаём .envrc
echo 'source .venv/bin/activate' > .envrc
direnv allow

# Теперь при входе в папку окружение активируется автоматически!
```

#### Скрипт-обёртка для удобства

```bash
#!/bin/bash
# setup.sh — быстрая настройка проекта

set -e

echo "🔧 Настройка виртуального окружения..."

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "✅ Готово! Активируйте окружение:"
echo "   source .venv/bin/activate"
```

#### Несколько окружений для одного проекта

```bash
# Три окружения для разных целей
python -m venv .venv-py311   # Python 3.11
python -m venv .venv-py312   # Python 3.12 (тестирование совместимости)
python -m venv .venv-dev     # С dev-инструментами

# Переключение между версиями Python для тестов
source .venv-py311/bin/activate && pytest
source .venv-py312/bin/activate && pytest
```

---

## Практическое задание

### Задача: полный цикл работы с виртуальным окружением

1. **Создайте проект** с нуля в новой папке `venv-practice`:

```bash
mkdir venv-practice
cd venv-practice
```

2. **Создайте виртуальное окружение** через `venv`:

```bash
python -m venv .venv
```

3. **Активируйте** окружение и **установите** пакеты:

```bash
source .venv/bin/activate   # Linux/macOS
# или .venv\Scripts\activate  # Windows

pip install requests==2.31.0
pip install flask==3.0.0
pip install pytest==8.0.0
```

4. **Создайте `requirements.txt`**:

```bash
pip freeze > requirements.txt
```

5. **Напишите скрипт** `app.py`, который проверяет, что он запущен в виртуальном окружении, и выводит список установленных пакетов:

```python
"""app.py — проверка виртуального окружения и установленных пакетов."""

import sys
import importlib.metadata


def check_venv() -> bool:
    """Проверяет, что скрипт запущен внутри виртуального окружения."""
    in_venv = (
        hasattr(sys, 'real_prefix')
        or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    return in_venv


def list_installed_packages() -> list[str]:
    """Возвращает отсортированный список установленных пакетов."""
    packages = [
        f"{dist.metadata['Name']}=={dist.metadata['Version']}"
        for dist in importlib.metadata.distributions()
    ]
    return sorted(packages, key=str.lower)


def main() -> None:
    if check_venv():
        print("✅ Скрипт запущен в виртуальном окружении!")
        print(f"   Путь: {sys.prefix}")
    else:
        print("❌ Скрипт запущен ГЛОБАЛЬНО. Создайте виртуальное окружение!")
        sys.exit(1)

    print("\n📦 Установленные пакеты:")
    for pkg in list_installed_packages():
        print(f"   - {pkg}")


if __name__ == "__main__":
    main()
```

6. **Запустите скрипт** внутри и вне окружения — сравните поведение.

7. **Деактивируйте** окружение и **удалите** его. Затем **пересоздайте** из `requirements.txt`:

```bash
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

8. **Создайте `.gitignore`** с правильными исключениями.

9. **(Опционально)** Повторите шаги с `virtualenv` и Conda, сравните.

---

## Дополнительные материалы

### 📚 Официальная документация

- [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html) — официальная документация Python
- [virtualenv documentation](https://virtualenv.pypa.io/en/latest/) — полное руководство по virtualenv
- [Conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) — управление Conda-окружениями

### 🎥 Видео и статьи

- [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer/) — Real Python (подробный туториал)
- [Why you should use `python -m venv`](https://snarky.ca/why-you-should-use-python-m-pip/) — Бретт Кэннон о правильном вызове инструментов Python
- [A Guide to Python's Virtual Environments](https://towardsdatascience.com/python-virtual-environments-a-primer-984b8e983d26) — сравнение всех инструментов

### 🔗 Связанные уроки

- **Урок 2**: Менеджеры пакетов: pip, Poetry и uv — что делать после активации окружения
- **Урок 3**: Линтинг и форматирование — инструменты, которые стоит установить в dev-окружение

### 🛠 Инструменты

- [direnv](https://direnv.net/) — автоматическая активация окружений при входе в папку
- [pyenv](https://github.com/pyenv/pyenv) — управление версиями Python (часто используется вместе с venv)
- [pipx](https://pipx.pypa.io/) — изолированная установка CLI-инструментов (см. Урок 2)

### 💡 Ключевые выводы

1. **Всегда** используйте виртуальные окружения — даже для маленьких скриптов
2. **Никогда** не устанавливайте пакеты глобально через `sudo pip install`
3. **`.venv`** — стандартное имя для папки окружения
4. **`requirements.txt`** или **`pyproject.toml`** — всегда коммитить
5. **`venv`** для большинства проектов, **Conda** — для data science
6. Одно окружение — один проект. Не используйте одно окружение для разных проектов