---
title: "Код-ревью и культура качества"
order: 5
tags:
  - код-ревью
  - качество
  - ревью
  - best-practices
prerequisites: "Все предыдущие уроки"
objective: "Освоить практики код-ревью и встроить качество в процесс разработки"
---

# Код-ревью и культура качества

## Введение

Код-ревью — это не просто поиск багов. Это главный механизм **распространения
знаний** в команде, **коллективного владения кодом** и **предотвращения
технического долга**. Хорошо настроенный процесс ревью окупается
многократно: согласно исследованиям (Capers Jones, *Applied Software
Measurement*), баг, найденный на ревью, стоит в 10–100 раз дешевле, чем баг,
найденный в продакшене.

В этом уроке мы разберём:

- **Что искать на код-ревью** — контрольный список (checklist)
- **Автоматизированные проверки** — линтинг, форматирование, типы
- **Pull Request templates** — как стандартизировать ревью
- **Conventional Commits и Semantic Versioning** — как версионировать код
- **ADR (Architecture Decision Records)** — как документировать решения
- **Python-специфичные аспекты** — PEP 8, идиомы, типизация

После этого урока вы сможете выстроить процесс код-ревью, который
действительно повышает качество, а не просто ставит галочку «approved».

---

## Основная часть

### 1. Зачем нужно код-ревью: цели и выгоды

| Цель                        | Как достигается                                    |
| --------------------------- | -------------------------------------------------- |
| Найти дефекты               | Второй взгляд замечает то, что пропустил автор      |
| Распространить знания       | Ревьюер учится у автора и наоборот                  |
| Обеспечить единый стиль     | Команда договаривается о стандартах                 |
| Коллективное владение кодом | Нет «авторских» модулей, за которые отвечает один   |
| Предотвратить техдолг       | Архитектурные проблемы выявляются до merge          |
| Менторство                  | Опытные разработчики помогают расти новичкам        |

### 2. Что искать на код-ревью: контрольный список

#### 2.1. Корректность (Correctness)

```python
# ❌ Ошибка: off-by-one
def get_page(items: list, page: int, per_page: int) -> list:
    start = page * per_page          # страница 0 → start = 0, ОК
    end = start + per_page           # страница 1 → start = 10, end = 20
    return items[start:end]           # но items[10:20] — это вторая страница!
```

```python
# ✅ Исправлено
def get_page(items: list, page: int, per_page: int) -> list:
    start = (page - 1) * per_page    # страница 1 → start = 0
    end = start + per_page
    return items[start:end]
```

На что обращать внимание:
- Off-by-one errors (границы срезов, циклы)
- Путаница с `None`, `0`, `False`, пустыми коллекциями
- Неправильная обработка пустых входных данных
- Гонки данных (race conditions) в многопоточном коде

#### 2.2. Читаемость (Readability)

```python
# ❌ Нечитаемо
def f(x, y, z):
    return [i for i in x if i[y] > z and i["active"] == True and i.get("deleted") != True]

# ✅ Читаемо
def filter_active_users(
    users: list[dict],
    min_age: int,
) -> list[dict]:
    """Return users who are active, not deleted, and older than min_age."""
    return [
        user
        for user in users
        if user["age"] > min_age
        and user.get("active") is True
        and not user.get("deleted", False)
    ]
```

На что обращать внимание:
- Понятные имена переменных, функций, классов
- Функции делают ровно одну вещь (не больше 20-30 строк)
- Сложные выражения разбиты на промежуточные переменные
- Комментарии объясняют «почему», а не «что»

#### 2.3. Тесты

```python
# ❌ Тест не проверяет краевые случаи
def test_divide() -> None:
    assert divide(10, 2) == 5.0
    # Нет проверки деления на ноль, отрицательных, float

# ✅ Полноценные тесты
@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5.0),
    (0, 5, 0.0),
    (-10, 2, -5.0),
    (1, 3, 1 / 3),
])
def test_divide_valid(a, b, expected) -> None:
    assert divide(a, b) == pytest.approx(expected)

def test_divide_by_zero_raises() -> None:
    with pytest.raises(ValueError, match="Division by zero"):
        divide(10, 0)
```

На что обращать внимание:
- Есть ли тесты на новый код
- Покрывают ли тесты краевые случаи
- Тесты читаемы и поддерживаемы (не хрупкие)
- Правильно ли используются моки (не перемокано)

#### 2.4. Документация

```python
# ❌ Нет документации
def process(data, opts=None):
    ...

# ✅ Документировано
def process_records(
    data: list[dict[str, Any]],
    options: ProcessingOptions | None = None,
) -> ProcessingResult:
    """
    Process raw data records and return aggregated result.

    Args:
        data: List of raw records, each a dict with string keys.
        options: Optional processing configuration. If None, defaults are used.

    Returns:
        ProcessingResult with aggregated statistics.

    Raises:
        ValueError: If data is empty or contains invalid records.
    """
    ...
```

#### 2.5. Производительность

```python
# ❌ Квадратичная сложность
def has_duplicates(items: list[int]) -> bool:
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False

# ✅ Линейная сложность
def has_duplicates(items: list[int]) -> bool:
    seen: set[int] = set()
    for item in items:
        if item in seen:
            return True
        seen.add(item)
    return False
```

На что обращать внимание:
- Алгоритмическая сложность (O(n²) там, где можно O(n))
- N+1 queries в ORM
- Блокирующие операции в асинхронном коде
- Избыточные копирования больших структур данных

### 3. Автоматизированные проверки

Всё, что можно проверить машиной, **должно** проверяться машиной. Человек на
ревью должен думать о дизайне и корректности, а не о расстановке пробелов.

#### 3.1. Уровни автоматизации

| Уровень        | Инструменты Python               | Когда запускается     |
| -------------- | -------------------------------- | --------------------- |
| Форматирование | `ruff format`, `black`           | pre-commit, CI        |
| Линтинг        | `ruff check`, `pylint`           | pre-commit, CI        |
| Типизация      | `mypy`, `pyright`                | CI                    |
| Тесты          | `pytest`                         | CI                    |
| Безопасность   | `bandit`, `safety`               | CI                    |
| Зависимости    | `pip-audit`, `dependabot`        | CI (расписание)       |

#### 3.2. Конфигурация инструментов

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]  # assert в тестах — это нормально

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]  # assert (нормально для production-кода)
```

### 4. Pull Request Templates

Стандартизированный шаблон PR экономит время и автору, и ревьюеру.

`.github/pull_request_template.md`:

```markdown
## 📝 Описание
<!-- Кратко опишите, что делает этот PR и зачем -->

Closes #ISSUE_NUMBER

## 🔍 Тип изменений
- [ ] 🐛 Исправление бага
- [ ] ✨ Новая функциональность
- [ ] 🔧 Рефакторинг
- [ ] 📚 Документация
- [ ] ⚡ Производительность

## ✅ Checklist
- [ ] Код соответствует стилю (ruff check проходит)
- [ ] Типы проверены (mypy --strict)
- [ ] Добавлены/обновлены тесты
- [ ] Все тесты проходят локально
- [ ] Покрытие не уменьшилось
- [ ] Документация обновлена (если нужно)
- [ ] CHANGELOG обновлён (если нужно)

## 🧪 Как тестировать
<!-- Шаги для воспроизведения, команды, скриншоты -->

## 📸 Скриншоты (если применимо)

## ⚠️ Breaking Changes
<!-- Если есть ломающие изменения, опишите их и путь миграции -->
```

### 5. Conventional Commits и Semantic Versioning

#### 5.1. Conventional Commits

Стандартизированный формат коммитов делает историю читаемой и позволяет
автоматически определять следующую версию:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Тип       | Когда использовать                     | Версия (semver) |
| --------- | -------------------------------------- | --------------- |
| `feat`    | Новая функциональность                 | MINOR           |
| `fix`     | Исправление бага                       | PATCH           |
| `docs`    | Только документация                    | —               |
| `style`   | Форматирование, пробелы                | —               |
| `refactor`| Рефакторинг без изменения поведения    | —               |
| `perf`    | Улучшение производительности           | PATCH           |
| `test`    | Добавление/изменение тестов            | —               |
| `chore`   | Обновление зависимостей, сборка        | —               |
| `ci`      | CI/CD изменения                        | —               |
| `BREAKING CHANGE` | Ломающие изменения (в footer)  | MAJOR           |

Примеры:

```
feat(auth): add JWT token refresh endpoint

Add POST /auth/refresh endpoint that accepts a valid refresh token
and returns a new access token with 15-minute expiry.

Closes #234
```

```
fix(api): handle empty results in pagination

Previously, requesting a page beyond the last page returned 500.
Now it returns an empty list with 200.

BREAKING CHANGE: Pagination response format changed from
{items: [...]} to {data: [...], meta: {page, total_pages}}.
```

#### 5.2. Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  │     │     └── Исправления багов (обратно совместимые)
  │     └──────── Новая функциональность (обратно совместимая)
  └────────────── Ломающие изменения (несовместимые)
```

| Версия    | Что изменилось                              |
| --------- | ------------------------------------------- |
| 1.0.0     | Первый стабильный релиз                     |
| 1.0.1     | Исправлен баг                               |
| 1.1.0     | Добавлена новая функция (без ломания старого)|
| 2.0.0     | Ломающее изменение API                      |

### 6. Архитектурные решения: ADR

Architecture Decision Records (ADR) — лёгкий способ документировать
архитектурные решения. Это текстовые файлы в репозитории, которые отвечают
на вопрос «почему мы сделали так, а не иначе».

`docs/adr/0001-use-pytest-for-testing.md`:

```markdown
# ADR-0001: Использовать pytest для тестирования

## Статус
Принято (2024-01-15)

## Контекст
Нужно выбрать тестовый фреймворк для нового проекта на Python.
Рассматривались: unittest (stdlib), pytest, nose (deprecated).

## Решение
Использовать pytest.

## Альтернативы
- **unittest**: встроен, не требует установки. Но многословный,
  требует наследования от TestCase, меньше возможностей.
- **nose**: устарел, не поддерживается.

## Последствия
- Нужна установка pytest (добавить в dev-зависимости)
- Можно использовать богатую экосистему плагинов (pytest-cov, pytest-mock, ...)
- Команда должна изучить фикстуры и параметризацию
- Положительно: тесты короче и читаемее на 30-40%
```

Шаблон ADR:

```markdown
# ADR-NNNN: Краткое название

## Статус
[Предложено | Принято | Отклонено | Заменено ADR-NNNN]

## Контекст
Почему мы вообще об этом думаем?

## Решение
Что мы решили сделать?

## Альтернативы
Какие ещё варианты мы рассматривали и почему отклонили?

## Последствия
Что теперь станет проще, а что — сложнее?
```

### 7. Python-специфичные аспекты код-ревью

#### 7.1. PEP 8 и современные идиомы

```python
# ❌ Старый стиль
class MyClass(object):            # не нужно наследовать object в Python 3
    def __init__(self, x):
        super(MyClass, self).__init__()  # многословный super
        self._x = x

    def get_x(self):               # геттеры без причины
        return self._x

    def set_x(self, value):        # сеттеры без валидации
        self._x = value

# ✅ Современный идиоматичный Python
from dataclasses import dataclass


@dataclass
class MyClass:
    x: int

    # Геттеры/сеттеры не нужны, если нет логики
    # Если логика нужна — используем @property
```

#### 7.2. Типизация

```python
# ❌ Без типов или с примитивными типами
def get_users(status=None):
    users = db.query("SELECT * FROM users")
    if status:
        return [u for u in users if u["status"] == status]
    return users

# ✅ С полной типизацией
from typing import TypedDict, Literal


class User(TypedDict):
    id: int
    name: str
    email: str
    status: Literal["active", "inactive", "banned"]


def get_users(
    status: Literal["active", "inactive", "banned"] | None = None,
) -> list[User]:
    """Fetch users, optionally filtered by status."""
    users: list[User] = db.query("SELECT * FROM users")
    if status is not None:
        return [u for u in users if u["status"] == status]
    return users
```

#### 7.3. Правильное использование стандартной библиотеки

```python
# ❌ Изобретение велосипеда
def flatten(nested: list[list[int]]) -> list[int]:
    result = []
    for sublist in nested:
        for item in sublist:
            result.append(item)
    return result

# ✅ Использование itertools
from itertools import chain


def flatten(nested: list[list[int]]) -> list[int]:
    return list(chain.from_iterable(nested))
```

```python
# ❌ Ручная работа с временными файлами
import os
import tempfile

def process_temp() -> None:
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, "w") as f:
            f.write("data")
    finally:
        os.unlink(path)

# ✅ pathlib + tempfile.TemporaryDirectory
from pathlib import Path
from tempfile import TemporaryDirectory


def process_temp() -> None:
    with TemporaryDirectory() as tmp:
        file = Path(tmp) / "data.txt"
        file.write_text("data")
        # файл автоматически удалится
```

#### 7.4. Безопасность

```python
# ❌ Уязвимость: SQL-инъекция
def get_user(cursor, user_id: str) -> dict | None:
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return cursor.fetchone()

# ❌ Уязвимость: command injection
def run_command(user_input: str) -> str:
    import subprocess
    return subprocess.getoutput(f"echo {user_input}")

# ✅ Безопасно: параметризованные запросы
def get_user(cursor, user_id: str) -> dict | None:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()

# ✅ Безопасно: список аргументов
def run_command(user_input: str) -> str:
    import subprocess
    result = subprocess.run(
        ["echo", user_input],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
```

### 8. Эффективное ревью: практические советы

#### 8.1. Для автора PR

✅ **Идиоматично:**
- Делайте маленькие PR (200-400 строк). Большие PR никто не хочет ревьюить.
- Пишите понятное описание: что, зачем, как тестировать.
- Проверяйте свой PR сами перед отправкой: пройдите diff, уберите отладочный код.
- Отвечайте на комментарии быстро, даже если просто «fixed in commit X».
- Разбивайте большие изменения на цепочку PR от feature-ветки к feature-ветке.

❌ **Антипаттерны:**
- PR на 2000 строк с описанием «fixes».
- Оставлять закомментированный код «на всякий случай».
- Смешивать рефакторинг и новую функциональность в одном PR.
- Force-push после того, как ревью началось (ломает историю комментариев).
- Принимать ревью лично: «этот код — не я, это моя работа».

#### 8.2. Для ревьюера

✅ **Идиоматично:**
- Начинайте с позитивного: отметьте хорошие решения.
- Различайте блокеры (must fix) и предложения (nice to have).
- Объясняйте «почему», а не просто «переделай».
- Если не понимаете код — спрашивайте, а не предполагайте.
- Ревьюйте в течение 24 часов (в идеале — в тот же день).

❌ **Антипаттерны:**
- «LGTM» (Looks Good To Me) без реального просмотра.
- Придирки к стилю, которые ловит линтер (настройте автоматику!).
- «Я бы написал по-другому» без объективных причин.
- Затягивание ревью на недели.
- Ревью как демонстрация превосходства.

### 9. Сравнение с практиками крупных компаний

#### Google's Code Review Practices

Google — одна из компаний, наиболее известных своей культурой код-ревью:

- **Readability:** для каждого языка есть сертифицированные «ревьюеры по
  читаемости». Их одобрение обязательно для любого кода.
- **Маленькие CL (changelist):** средний размер CL в Google — около 24 строк.
  Большие изменения разбиваются на цепочки.
- **Инструменты:** Critique — внутренний инструмент ревью с богатой
  аналитикой (время ревью, количество комментариев, «горячие» файлы).
- **Статистика:** в Google медианное время ревью — менее 4 часов.

#### GitHub Flow

```
main ← feature-branch
  │         │
  │    ┌────┴────┐
  │    │ commits  │
  │    └────┬────┘
  │         │
  │    ┌─ PR ─┐
  │    │ revw │
  │    └──┬───┘
  │       │
  └─── merge ──→ deploy
```

Подходит для проектов с непрерывной доставкой (веб-сервисы).

#### GitLab Flow

```
main ← pre-production ← production
  │         │               │
  └─── feature branches ────┘
```

Добавляет ветки окружений (staging, production) поверх GitHub Flow. Подходит
для проектов с релизным циклом.

### 10. Культура качества: внедрение в команде

#### 10.1. Definition of Done

```
✅ Код написан и проходит все тесты
✅ Код проходит линтер (ruff) и проверку типов (mypy)
✅ Покрытие не уменьшилось
✅ PR прошёл код-ревью (минимум 1 approve)
✅ Документация обновлена
✅ Изменения задокументированы в CHANGELOG
✅ Ветка синхронизирована с main (rebase)
```

#### 10.2. Метрики качества

| Метрика                     | Что измеряет                         | Целевое значение     |
| --------------------------- | ------------------------------------ | -------------------- |
| Time to review              | Время от создания PR до первого ревью| < 24 часов           |
| Time to merge               | Время от создания PR до merge        | < 48 часов           |
| PR size                     | Количество изменённых строк          | < 400 строк          |
| Review depth                | Комментариев на PR                   | > 0 (не «LGTM»)      |
| Rework rate                 | Коммитов после первого ревью         | < 3                  |
| Code coverage               | Процент покрытия                     | > 80%                |
| Bug escape rate             | Багов в продакшене / всего багов     | < 5%                 |

#### 10.3. Ретроспектива качества

Каждые 2-4 недели команда отвечает на вопросы:

1. Какие баги попали в продакшен? Почему?
2. Какие PR долго висели без ревью? Почему?
3. Какие тесты «зелёные, но бесполезные»?
4. Есть ли код, который никто не понимает?
5. Что мы можем улучшить в процессе на следующей итерации?

---

## Практическое задание

### Цель
Провести код-ревью учебного проекта и настроить все автоматизированные
проверки.

### Структура проекта

```
review_demo/
├── src/
│   ├── __init__.py
│   └── user_service.py
├── tests/
│   ├── __init__.py
│   └── test_user_service.py
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       └── quality.yml
├── docs/
│   └── adr/
│       └── 0001-use-sqlite-for-storage.md
├── pyproject.toml
├── .pre-commit-config.yaml
├── CHANGELOG.md
└── README.md
```

### Исходный код для ревью (`src/user_service.py`)

```python
import sqlite3
import hashlib
from datetime import datetime


class UserService:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                created_at TEXT
            )
        """)

    def create_user(self, username, password, email):
        # Хешируем пароль (НЕПРАВИЛЬНО — нужен bcrypt/argon2!)
        pw_hash = hashlib.md5(password.encode()).hexdigest()
        now = datetime.now().isoformat()
        try:
            self.conn.execute(
                f"INSERT INTO users (username, password_hash, email, created_at) "
                f"VALUES ('{username}', '{pw_hash}', '{email}', '{now}')"
            )
            self.conn.commit()
            return {"id": self.conn.execute("SELECT last_insert_rowid()").fetchone()[0],
                    "username": username, "email": email}
        except sqlite3.IntegrityError:
            return None

    def get_user(self, user_id):
        cur = self.conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "email": row[3],
                "created_at": row[4],
            }
        return None

    def delete_user(self, user_id):
        self.conn.execute(f"DELETE FROM users WHERE id = {user_id}")
        self.conn.commit()

    def list_users(self):
        cur = self.conn.execute("SELECT * FROM users")
        return [{"id": r[0], "username": r[1], "email": r[3]} for r in cur.fetchall()]
```

### Задачи

1. **Код-ревью (3 балла):** Проведите ревью `user_service.py` по
   контрольному списку (корректность, читаемость, тесты, безопасность).
   Опишите минимум 5 проблем и предложите исправления.

2. **Исправление (3 балла):** Исправьте все найденные проблемы:
   - SQL-инъекции: перейдите на параметризованные запросы
   - Хеширование паролей: замените MD5 на bcrypt (или хотя бы hashlib.pbkdf2_hmac)
   - Типизация: добавьте аннотации типов
   - Документация: добавьте docstrings
   - Ресурсы: метод `__init__` не должен создавать подключение без явного вызова

3. **Pull Request Template (2 балла):** Создайте
   `.github/pull_request_template.md` с checklist'ом.

4. **CI/CD (3 балла):** Настройте `.github/workflows/quality.yml`:
   - ruff (линтер + форматтер)
   - mypy
   - pytest с покрытием
   - bandit (проверка безопасности)

5. **ADR (2 балла):** Напишите ADR о выборе SQLite как хранилища для
   учебного проекта (в `docs/adr/0001-use-sqlite-for-storage.md`).

6. **Conventional Commits (2 балла):** Оформите исправления как серию
   коммитов в стиле Conventional Commits.

### Критерии оценки
- Ревью содержит минимум 5 конкретных проблем с объяснениями
- Исправленный код безопасен, типизирован и документирован
- Все CI-проверки проходят
- PR template и ADR созданы
- Коммиты следуют Conventional Commits

---

## Дополнительные материалы

### Книги
- Michaela Greiler, *Code Review Matters and Manners* (самоиздание, 2020)
  — Практическое руководство по код-ревью.
- Titus Winters, Tom Manshreck, Hyrum Wright, *Software Engineering at Google*
  (O'Reilly, 2020) — Глава 9: «Code Review».
- Michael Feathers, *Working Effectively with Legacy Code* (Prentice Hall, 2004)
  — Классика о рефакторинге и тестировании легаси.

### Документация
- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning Specification](https://semver.org/)
- [Google's Engineering Practices: Code Review](https://google.github.io/eng-practices/review/)
- [ADR GitHub Organization](https://adr.github.io/)

### Статьи
- Google Testing Blog, *Code Review Best Practices*
- Michaela Greiler, *Better Code Review*, michaelagreiler.com
- Gergely Orosz, *The Pragmatic Engineer's Code Review Checklist*, pragmaticengineer.com
- Joel Spolsky, *The Joel Test: 12 Steps to Better Code* (2000), joelonsoftware.com

### Инструменты
- [ruff](https://docs.astral.sh/ruff/) — быстрый линтер и форматтер
- [mypy](https://mypy-lang.org/) — статическая проверка типов
- [bandit](https://bandit.readthedocs.io/) — поиск уязвимостей в Python-коде
- [commitlint](https://commitlint.js.org/) — проверка формата коммитов
- [semantic-release](https://semantic-release.gitbook.io/) — автоматическое версионирование
- [Reviewable](https://reviewable.io/) — альтернативный UI для GitHub PR review
- [Danger](https://danger.systems/) — автоматизация правил ревью («не забудь CHANGELOG»)