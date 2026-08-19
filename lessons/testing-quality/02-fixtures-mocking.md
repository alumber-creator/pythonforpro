---
title: "Фикстуры, моки и monkeypatching"
order: 2
tags:
  - фикстуры
  - моки
  - monkeypatch
  - unittest.mock
  - pytest-mock
prerequisites: "Урок 1"
objective: "Освоить продвинутые техники тестирования: сложные фикстуры, мокирование и изоляцию"
---

# Фикстуры, моки и monkeypatching

## Введение

В реальных проектах тестируемый код редко живёт в вакууме. Он вызывает
внешние API, читает базу данных, отправляет email, работает с файловой
системой, зависит от текущего времени. Чтобы тесты оставались **быстрыми**,
**детерминированными** и **изолированными**, мы должны уметь подменять
зависимости. Этот урок посвящён трём механизмам подмены в pytest:

1. **Фикстуры** — для подготовки и очистки ресурсов (БД, файлы, серверы).
2. **Моки (unittest.mock / pytest-mock)** — для подмены объектов и их поведения.
3. **Monkeypatching** — для подмены атрибутов, переменных окружения и
   глобальных объектов «на лету».

После этого урока вы сможете тестировать код с внешними зависимостями без
подключения к реальным сервисам и с полным контролем над окружением.

---

## Основная часть

### 1. Продвинутые фикстуры: композиция и внедрение зависимостей

#### 1.1. Цепочки фикстур

Фикстуры могут зависеть от других фикстур, образуя ориентированный граф
зависимостей. pytest разрешает его автоматически:

```python
import pytest
from pathlib import Path


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Корень временного проекта."""
    return tmp_path / "project"


@pytest.fixture
def config_file(project_dir: Path) -> Path:
    """Конфигурационный файл внутри проекта."""
    project_dir.mkdir()
    cfg = project_dir / "config.yaml"
    cfg.write_text("debug: true\n")
    return cfg


@pytest.fixture
def app_config(config_file: Path) -> dict:
    """Прочитанная конфигурация."""
    import yaml  # pip install pyyaml
    return yaml.safe_load(config_file.read_text())


def test_config_debug(app_config: dict) -> None:
    assert app_config["debug"] is True
```

Граф зависимостей: `tmp_path` → `project_dir` → `config_file` → `app_config`.
pytest создаёт их в правильном порядке и очищает в обратном.

#### 1.2. Фикстуры-фабрики

Иногда тесту нужен не один объект, а возможность создавать много похожих
объектов с разными параметрами. Вместо того чтобы параметризовать саму
фикстуру, верните **фабричную функцию**:

```python
import pytest
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True


@pytest.fixture
def make_user() -> callable:
    """Фабрика пользователей: каждый тест создаёт нужных ему."""
    created: list[User] = []

    def _make(**kwargs) -> User:
        defaults = {"id": 1, "name": "Alice", "email": "alice@example.com"}
        defaults.update(kwargs)
        user = User(**defaults)
        created.append(user)
        return user

    yield _make
    # teardown: очистка, если нужно
    for user in created:
        print(f"  [teardown] Удаляю пользователя {user.id}")


def test_create_users(make_user) -> None:
    alice = make_user()
    bob = make_user(id=2, name="Bob", email="bob@example.com")
    assert alice.name == "Alice"
    assert bob.name == "Bob"
    assert alice.is_active is True
```

✅ **Идиоматично:** фабричная фикстура, когда тестам нужна гибкость.

❌ **Антипаттерн:** десятки узкоспециализированных фикстур
(`user_alice`, `user_bob`, `user_charlie_inactive`, ...).

#### 1.3. Временные файлы и каталоги: `tmp_path` и `tmpdir`

pytest предоставляет две встроенные фикстуры для временных файлов:

| Фикстура   | Тип возврата           | Когда использовать                     |
| ---------- | ---------------------- | -------------------------------------- |
| `tmp_path` | `pathlib.Path`         | Современный код (рекомендуется)         |
| `tmpdir`   | `py.path.local` (legacy)| Старый код, совместимость              |

```python
import pytest
from pathlib import Path


def test_write_and_read(tmp_path: Path) -> None:
    """Запись и чтение временного файла."""
    file = tmp_path / "output.txt"
    file.write_text("Hello, pytest!")

    assert file.exists()
    assert file.read_text() == "Hello, pytest!"


def test_directory_structure(tmp_path: Path) -> None:
    """Создание структуры каталогов."""
    src = tmp_path / "src" / "package"
    src.mkdir(parents=True)
    (src / "__init__.py").touch()
    (src / "module.py").write_text("def f(): pass\n")

    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_module.py").write_text("def test_f(): pass\n")

    # Проверка структуры
    py_files = list(tmp_path.rglob("*.py"))
    assert len(py_files) == 3
```

Все файлы в `tmp_path` автоматически удаляются после каждого теста (scope
`function`). Для сохранения между тестами используйте scope `"session"`:

```python
@pytest.fixture(scope="session")
def session_tmp(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Временный каталог на всю сессию."""
    return tmp_path_factory.mktemp("session_data")
```

### 2. Встроенные моки: `unittest.mock`

Стандартная библиотека Python включает мощный модуль `unittest.mock`, который
отлично работает с pytest:

```python
from unittest.mock import Mock, MagicMock, patch, call


def test_mock_basics() -> None:
    """Базовые возможности Mock."""
    mock = Mock()
    mock.some_method(1, 2, key="value")
    mock.some_method(3, 4, key="other")

    # Проверка вызовов
    mock.some_method.assert_called()
    assert mock.some_method.call_count == 2
    mock.some_method.assert_has_calls([
        call(1, 2, key="value"),
        call(3, 4, key="other"),
    ])
```

#### 2.1. `Mock` vs `MagicMock`

| Класс       | Особенности                                              |
| ----------- | -------------------------------------------------------- |
| `Mock`      | Простой мок: атрибуты и вызовы                           |
| `MagicMock` | `Mock` + все магические методы (`__len__`, `__iter__`, ...) |

```python
from unittest.mock import Mock, MagicMock


def test_mock_vs_magicmock() -> None:
    plain = Mock()
    # plain[0] = 1  # AttributeError: у Mock нет __setitem__

    magic = MagicMock()
    magic[0] = 1          # работает __setitem__
    assert len(magic) == 0  # работает __len__ (возвращает другой MagicMock)
    assert 0 in magic       # работает __contains__
```

#### 2.2. `patch` — подмена объектов в контексте

```python
from unittest.mock import patch
import os


def test_patch_context_manager() -> None:
    """Подмена os.getcwd через контекстный менеджер."""
    original = os.getcwd()
    with patch("os.getcwd", return_value="/fake/path"):
        assert os.getcwd() == "/fake/path"
    assert os.getcwd() == original  # восстановлено


@patch("os.getcwd", return_value="/fake/path")
def test_patch_decorator(mock_getcwd) -> None:
    """Подмена os.getcwd через декоратор."""
    assert os.getcwd() == "/fake/path"
    mock_getcwd.assert_called_once()
```

#### 2.3. Тестирование внешнего API с моками

```python
import json
from unittest.mock import Mock, patch
from urllib.request import urlopen


def fetch_user_repos(username: str) -> list[dict]:
    """Получает список репозиториев пользователя GitHub."""
    url = f"https://api.github.com/users/{username}/repos"
    with urlopen(url) as response:
        return json.loads(response.read())


@patch("urllib.request.urlopen")
def test_fetch_user_repos(mock_urlopen) -> None:
    # Настраиваем мок
    mock_response = Mock()
    mock_response.read.return_value = json.dumps([
        {"name": "repo1", "stars": 10},
        {"name": "repo2", "stars": 5},
    ])
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=False)
    mock_urlopen.return_value = mock_response

    repos = fetch_user_repos("octocat")

    assert len(repos) == 2
    assert repos[0]["name"] == "repo1"
    mock_urlopen.assert_called_once_with(
        "https://api.github.com/users/octocat/repos"
    )
```

> ⚠️ Такой код работает, но он хрупкий: если `urlopen` изменится, тесты
> сломаются. Лучше использовать библиотеки `responses` или `aioresponses`
> (см. раздел 4).

### 3. `pytest-mock` — плагин для удобного мокирования

Плагин `pytest-mock` добавляет фикстуру `mocker` — обёртку над
`unittest.mock` с удобным API и автоматической очисткой:

```bash
pip install pytest-mock
```

```python
import pytest
from unittest.mock import Mock


def test_mocker_spy(mocker: "pytest_mock.MockerFixture") -> None:
    """mocker.spy: обёртка, которая отслеживает вызовы без подмены."""
    obj = Mock()
    obj.method = Mock(return_value=42)

    spy = mocker.spy(obj, "method")
    result = obj.method("arg")

    assert result == 42
    spy.assert_called_once_with("arg")


def test_mocker_patch(mocker: "pytest_mock.MockerFixture") -> None:
    """mocker.patch: подмена с автоматической очисткой."""
    mocker.patch("os.getenv", return_value="test_value")
    import os
    assert os.getenv("DB_HOST") == "test_value"


def test_mocker_stub(mocker: "pytest_mock.MockerFixture") -> None:
    """mocker.stub: создаёт заглушку с заданным поведением."""
    stub = mocker.stub(name="database")
    stub.connect.return_value = True
    stub.query.return_value = [{"id": 1}]

    assert stub.connect() is True
    assert stub.query("SELECT *") == [{"id": 1}]
```

#### 3.1. Сравнение: `unittest.mock.patch` vs `mocker.patch`

| Аспект               | `unittest.mock.patch`         | `mocker.patch`              |
| -------------------- | ----------------------------- | --------------------------- |
| Очистка              | Вручную или через декоратор   | Автоматически после теста   |
| Синтаксис            | `with patch("path"):`         | `mocker.patch("path")`      |
| Вложенность          | Вложенные `with`              | Плоские вызовы              |
| Stop-all             | `patch.stopall()`             | Не требуется                |

✅ **Идиоматично:** использовать `mocker.patch` в pytest-проектах.

❌ **Антипаттерн:** смешивать `mocker.patch` и `unittest.mock.patch` в одном
тесте без причины.

### 4. `monkeypatch` — встроенная фикстура pytest

`monkeypatch` позволяет подменять атрибуты, элементы словарей и переменные
окружения без дополнительных библиотек:

```python
import pytest
import os


def test_monkeypatch_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Подмена переменных окружения."""
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.delenv("NOT_SET", raising=False)

    assert os.getenv("DB_HOST") == "localhost"
    assert os.getenv("DB_PORT") == "5432"
    assert os.getenv("NOT_SET") is None


def test_monkeypatch_attr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Подмена атрибутов объекта."""

    class Config:
        debug = True
        database_url = "postgresql://prod:5432/db"

    config = Config()
    monkeypatch.setattr(config, "database_url", "sqlite:///:memory:")
    assert config.database_url == "sqlite:///:memory:"
    assert config.debug is True  # не тронуто


def test_monkeypatch_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    """Подмена элемента словаря."""
    settings = {"host": "prod.example.com", "port": 443}
    monkeypatch.setitem(settings, "host", "localhost")
    monkeypatch.setitem(settings, "port", 8080)

    assert settings["host"] == "localhost"
    assert settings["port"] == 8080
```

#### 4.1. Когда monkeypatch, а когда mock?

| Ситуация                                   | Инструмент    |
| ------------------------------------------ | ------------- |
| Подмена переменной окружения               | `monkeypatch` |
| Подмена атрибута объекта                   | `monkeypatch` |
| Подмена глобальной переменной модуля       | `monkeypatch` |
| Подмена функции с проверкой вызовов        | `mocker.patch` |
| Подмена сложного объекта с состоянием      | `Mock` / `MagicMock` |
| Подмена HTTP-запросов                      | `responses` / `aioresponses` |

### 5. Тестирование внешних API: `responses` и `aioresponses`

Мокировать `urlopen` вручную утомительно. Библиотека `responses` делает это
элегантно:

```bash
pip install responses
```

```python
import responses
import requests


@responses.activate
def test_fetch_data() -> None:
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.example.com/users/2",
        json={"error": "not found"},
        status=404,
    )

    r1 = requests.get("https://api.example.com/users/1")
    assert r1.status_code == 200
    assert r1.json()["name"] == "Alice"

    r2 = requests.get("https://api.example.com/users/2")
    assert r2.status_code == 404


@responses.activate
def test_unmatched_request_raises() -> None:
    """Любой незарегистрированный URL вызывает ошибку."""
    with pytest.raises(responses.ConnectionError):
        requests.get("https://unknown.example.com/api")
```

Для асинхронного кода (aiohttp, httpx) используйте `aioresponses`:

```bash
pip install aioresponses
```

```python
import pytest
from aioresponses import aioresponses
import aiohttp


@pytest.mark.asyncio
async def test_async_fetch() -> None:
    with aioresponses() as mocked:
        mocked.get(
            "https://api.example.com/data",
            payload={"key": "value"},
            status=200,
        )

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.example.com/data") as resp:
                data = await resp.json()
                assert data == {"key": "value"}
```

### 6. Тестирование базы данных

#### 6.1. Подход 1: SQLite in-memory

```python
import pytest
import sqlite3


@pytest.fixture
def in_memory_db() -> sqlite3.Connection:
    """Создаёт временную БД в памяти для каждого теста."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.execute("INSERT INTO users (name) VALUES ('Bob')")
    conn.commit()
    yield conn
    conn.close()


def test_query_users(in_memory_db: sqlite3.Connection) -> None:
    cursor = in_memory_db.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 2
```

#### 6.2. Подход 2: `factory_boy` для генерации тестовых данных

```bash
pip install factory_boy
```

```python
import factory
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    email: str
    is_active: bool = True


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda u: f"{u.username}@example.com")
    is_active = True


def test_factory_generates_users() -> None:
    user = UserFactory()
    assert user.id == 1
    assert "@example.com" in user.email

    users = UserFactory.build_batch(5)
    assert len(users) == 5
    assert all(u.is_active for u in users)
```

#### 6.3. Подход 3: `testcontainers` для реалистичных тестов

```bash
pip install testcontainers[pytest]
```

```python
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="module")
def postgres_container() -> PostgresContainer:
    """Запускает реальный PostgreSQL в Docker-контейнере."""
    with PostgresContainer("postgres:16") as postgres:
        yield postgres


def test_postgres_connection(postgres_container: PostgresContainer) -> None:
    import psycopg2
    conn = psycopg2.connect(postgres_container.get_connection_url())
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        assert cur.fetchone() == (1,)
    conn.close()
```

### 7. Сравнение с аналогами в других языках

#### Mockito (Java)

```java
// Java + Mockito: аннотации и статические методы
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    UserRepository repository;

    @InjectMocks
    UserService service;

    @Test
    void testFindUser() {
        when(repository.findById(1L))
            .thenReturn(Optional.of(new User("Alice")));

        User user = service.findUser(1L);
        assertEquals("Alice", user.getName());
        verify(repository).findById(1L);
    }
}
```

#### Sinon (JavaScript)

```javascript
// Sinon.js: spies, stubs, mocks
const sinon = require("sinon");

describe("UserService", () => {
  let repository, service;

  beforeEach(() => {
    repository = { findById: sinon.stub() };
    service = new UserService(repository);
  });

  it("finds user by id", () => {
    repository.findById.withArgs(1).returns({ name: "Alice" });
    const user = service.findUser(1);
    assert.equal(user.name, "Alice");
    sinon.assert.calledWith(repository.findById, 1);
  });
});
```

#### Google Mock (C++)

```cpp
// C++ Google Mock: макросы и строгая типизация
class MockUserRepository : public UserRepository {
public:
    MOCK_METHOD(std::optional<User>, findById, (long id), (override));
};

TEST(UserServiceTest, FindUser) {
    MockUserRepository repo;
    EXPECT_CALL(repo, findById(1))
        .WillOnce(Return(std::make_optional(User{"Alice"})));

    UserService service(&repo);
    auto user = service.findUser(1);
    ASSERT_TRUE(user.has_value());
    EXPECT_EQ(user->name, "Alice");
}
```

Python с `pytest-mock` и `unittest.mock` выигрывает в лаконичности: нет
необходимости в отдельных классах-моках (как в C++) или аннотациях (как в
Java). Всё делается функциями и контекстными менеджерами.

---

## Практическое задание

### Цель
Написать тесты для сервиса уведомлений с внешними зависимостями, используя
моки, фикстуры и monkeypatch.

### Исходный код (`src/notification.py`)

```python
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone


class NotificationService:
    """Отправляет уведомления пользователям."""

    def __init__(self, smtp_host: str | None = None) -> None:
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "1025"))

    def send_email(self, to: str, subject: str, body: str) -> bool:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["To"] = to
        msg["From"] = "noreply@example.com"

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.send_message(msg)
        return True

    def send_welcome(self, email: str, username: str) -> bool:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        body = f"Welcome, {username}!\nRegistered at: {now}"
        return self.send_email(email, "Welcome!", body)


class NotificationLogger:
    """Логирует все отправленные уведомления."""

    def __init__(self, log_file: str) -> None:
        self.log_file = log_file

    def log(self, email: str, subject: str) -> None:
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()}"
                    f" | {email} | {subject}\n")

    def get_count(self) -> int:
        try:
            with open(self.log_file) as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0
```

### Задачи

1. **Мокирование SMTP (4 балла):** Протестируйте `send_email` и
   `send_welcome` с моками `smtplib.SMTP`. Проверьте:
   - Что `send_message` вызывается ровно один раз
   - Что `MIMEText` содержит правильный `body`
   - Что тема письма корректна

2. **Monkeypatch (3 балла):** Протестируйте `NotificationService` с
   подменой переменных окружения `SMTP_HOST` и `SMTP_PORT` через
   `monkeypatch`. Проверьте, что используются значения по умолчанию,
   когда переменные не заданы.

3. **Фикстуры + tmp_path (3 балла):** Протестируйте `NotificationLogger`:
   - Запись в лог-файл
   - Подсчёт количества записей
   - Поведение при отсутствии файла

4. **Фикстура-фабрика (2 балла):** Создайте фабрику, генерирующую тестовые
   письма с разными параметрами.

5. **Интеграционный тест (3 балла):** Свяжите `NotificationService` и
   `NotificationLogger` вместе. Проверьте, что после отправки письма в
   лог-файле появляется запись.

### Критерии оценки
- Все тесты проходят
- Моки используются для `smtplib.SMTP`
- `monkeypatch` используется для переменных окружения
- `tmp_path` используется для временных файлов
- Код соответствует PEP 8

---

## Дополнительные материалы

### Книги
- Harry Percival, *Architecture Patterns with Python* (O'Reilly, 2020)
  — Глава 6: «Unit of Work» и тестирование с моками.
- Brian Okken, *Python Testing with pytest* (Pragmatic, 2022)
  — Глава 7: «Mocking» и глава 8: «Testing Strategy».

### Документация
- [unittest.mock — Python Official Docs](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-mock Plugin](https://github.com/pytest-dev/pytest-mock)
- [responses Library](https://github.com/getsentry/responses)
- [factory_boy Documentation](https://factoryboy.readthedocs.io/)
- [testcontainers-python](https://testcontainers-python.readthedocs.io/)

### Статьи
- Martin Fowler, *Mocks Aren't Stubs* (2007)
  — классическая статья о различии между моками и стабами.
- Testing on the Toilet (Google Blog):
  *«Don't Overuse Mocks»*, *«Test Behavior, Not Implementation»*.

### Инструменты
- `pytest --setup-show` — показать порядок создания/очистки фикстур
- `pytest --trace` — запустить отладчик в точке падения теста
- `responses._default_mock._matches` — отладка незарегистрированных URL