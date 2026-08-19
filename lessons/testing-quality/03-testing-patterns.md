---
title: "Паттерны тестирования: Given-When-Then, AAA, тестирование исключений"
order: 3
tags:
  - паттерны
  - AAA
  - given-when-then
  - тестирование
  - property-based
prerequisites: "Урок 2"
objective: "Освоить паттерны организации тестов и продвинутые техники"
---

# Паттерны тестирования: Given-When-Then, AAA, тестирование исключений

## Введение

Хороший тест — это не просто проверка, что код работает. Хороший тест
**рассказывает историю**: что дано, что происходит, что ожидается. Паттерны
организации тестов делают эту историю понятной для каждого, кто будет читать
тест через полгода — включая вас самих.

В этом уроке мы разберём:

- **AAA (Arrange-Act-Assert)** — структурный паттерн для любого теста
- **Given-When-Then (GWT)** — BDD-стиль, понятный не-программистам
- **Тестирование исключений и предупреждений** — `pytest.raises`, `pytest.warns`
- **Захват вывода** — `capsys`, `capfd`
- **Snapshot-тестирование** — для сложных структур данных
- **Property-based testing** — когда примеров недостаточно
- **Организация тестов** — unit, integration, e2e

После этого урока вы сможете не только писать тесты, но и **проектировать**
их так, чтобы они были читаемыми, поддерживаемыми и надёжными.

---

## Основная часть

### 1. AAA: Arrange-Act-Assert

AAA — самый распространённый паттерн организации тестов. Он делит тест на
три логические секции:

```python
import pytest
from decimal import Decimal


class BankAccount:
    def __init__(self, balance: Decimal = Decimal("0")) -> None:
        self.balance = balance

    def deposit(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError("Amount must be positive")
        self.balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount


def test_bank_transfer_aaa() -> None:
    # ── Arrange (Подготовка) ──────────────────────────
    alice = BankAccount(Decimal("1000"))
    bob = BankAccount(Decimal("500"))
    transfer_amount = Decimal("200")

    # ── Act (Действие) ────────────────────────────────
    alice.withdraw(transfer_amount)
    bob.deposit(transfer_amount)

    # ── Assert (Проверка) ─────────────────────────────
    assert alice.balance == Decimal("800")
    assert bob.balance == Decimal("700")
```

✅ **Идиоматично:** отделять секции пустыми строками и комментариями `Arrange`,
`Act`, `Assert`. Каждая секция содержит ровно одну ответственность.

❌ **Антипаттерн:** «спагетти-тест» — создание объектов вперемешку с
проверками, без чёткого разделения:

```python
def test_bad_spaghetti() -> None:
    a = BankAccount(Decimal("1000"))
    a.withdraw(Decimal("200"))
    assert a.balance == Decimal("800")
    a.deposit(Decimal("50"))
    assert a.balance == Decimal("850")
    a.withdraw(Decimal("100"))
    assert a.balance == Decimal("750")
    # Что здесь Arrange, что Act, что Assert? Непонятно.
```

#### 1.1. Множественные Arrange-Act-Assert (когда это оправдано)

Иногда один тест содержит несколько циклов AAA — например, при тестировании
конечного автомата:

```python
def test_traffic_light_sequence() -> None:
    light = TrafficLight()

    # Цикл 1: красный → зелёный
    assert light.state == "red"
    light.next()
    assert light.state == "green"

    # Цикл 2: зелёный → жёлтый
    light.next()
    assert light.state == "yellow"

    # Цикл 3: жёлтый → красный
    light.next()
    assert light.state == "red"
```

Но если тест проверяет **разные сценарии**, лучше разнести их по отдельным
тестам.

### 2. Given-When-Then (BDD-стиль)

Given-When-Then пришёл из Behaviour-Driven Development (BDD) и формулирует
тест на естественном языке:

- **Given** — исходное состояние системы
- **When** — ключевое действие
- **Then** — ожидаемый результат

```python
def test_user_can_reset_password() -> None:
    """
    Given: зарегистрированный пользователь с email
    When: пользователь запрашивает сброс пароля
    Then: на email отправляется ссылка для сброса
    """
    # Given
    user = UserFactory(email="alice@example.com")
    mailer = MockMailer()

    # When
    password_service = PasswordService(mailer=mailer)
    password_service.request_reset(user)

    # Then
    assert mailer.sent_to == "alice@example.com"
    assert "reset" in mailer.last_subject.lower()
    assert mailer.call_count == 1
```

#### 2.1. Сравнение AAA и GWT

| Критерий          | AAA                          | Given-When-Then               |
| ----------------- | ---------------------------- | ----------------------------- |
| Происхождение     | Структурное программирование | BDD (Behaviour-Driven Development) |
| Аудитория         | Разработчики                 | Разработчики + бизнес         |
| Формулировка      | Техническая                  | На естественном языке         |
| Инструменты       | Любой тестовый фреймворк     | Cucumber, SpecFlow, behave    |
| Лучше всего для   | Unit-тестов                  | Интеграционных / acceptance-тестов |

✅ **Идиоматично:** использовать AAA для unit-тестов, GWT для
интеграционных и acceptance-тестов.

### 3. Тестирование исключений: `pytest.raises`

```python
import pytest


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


def test_divide_by_zero_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)

    # Проверяем сообщение исключения
    assert "Division by zero" in str(exc_info.value)
    # Проверяем тип
    assert exc_info.type is ValueError


def test_divide_by_zero_match() -> None:
    """pytest.raises с match — проверка сообщения регуляркой."""
    with pytest.raises(ValueError, match=r"Division by zero"):
        divide(10, 0)


def test_divide_no_exception() -> None:
    """Если исключения нет — тест проходит."""
    result = divide(10, 2)
    assert result == 5.0


@pytest.mark.parametrize(
    "a, b, expected_exc, match",
    [
        (10, 0, ValueError, "Division by zero"),
        (0, 0, ValueError, "Division by zero"),
        (10, 2, None, None),
    ],
)
def test_divide_parametrized(
    a: float, b: float, expected_exc: type | None, match: str | None
) -> None:
    if expected_exc is not None:
        with pytest.raises(expected_exc, match=match):
            divide(a, b)
    else:
        assert divide(a, b) == a / b
```

#### 3.1. Проверка цепочек исключений

```python
def test_exception_chaining() -> None:
    """Проверка __cause__ / __context__ исключений."""

    def read_config(path: str) -> dict:
        try:
            import json
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise RuntimeError(f"Config not found: {path}") from e

    with pytest.raises(RuntimeError, match="Config not found") as exc_info:
        read_config("/nonexistent/config.json")

    # Проверяем цепочку исключений
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
```

### 4. Тестирование предупреждений: `pytest.warns`

```python
import pytest
import warnings


def deprecated_function() -> int:
    warnings.warn("This function is deprecated", DeprecationWarning)
    return 42


def test_deprecated_warns() -> None:
    with pytest.warns(DeprecationWarning, match="deprecated"):
        result = deprecated_function()
    assert result == 42


def test_no_warnings() -> None:
    """Тест падает, если возникает НЕожидаемое предупреждение."""
    with pytest.warns(None) as record:  # None = НЕ ожидаем предупреждений
        result = 1 + 1
    assert len(record) == 0
    assert result == 2


def test_multiple_warnings() -> None:
    with pytest.warns(DeprecationWarning) as record:
        deprecated_function()
        deprecated_function()

    assert len(record) == 2
    assert all(isinstance(w.message, DeprecationWarning) for w in record)
```

### 5. Захват вывода: `capsys` и `capfd`

```python
import pytest
import sys


def greet(name: str) -> None:
    """Выводит приветствие в stdout."""
    print(f"Hello, {name}!")


def test_greet_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    greet("Alice")

    captured = capsys.readouterr()
    assert captured.out == "Hello, Alice!\n"
    assert captured.err == ""


def test_stderr_output(capsys: pytest.CaptureFixture[str]) -> None:
    import sys
    print("normal output")
    print("error output", file=sys.stderr)

    captured = capsys.readouterr()
    assert captured.out == "normal output\n"
    assert captured.err == "error output\n"


def test_interleaved_output(capsys: pytest.CaptureFixture[str]) -> None:
    """capsys захватывает вывод по мере поступления."""
    print("first")
    out1 = capsys.readouterr().out
    print("second")
    out2 = capsys.readouterr().out

    assert out1 == "first\n"
    assert out2 == "second\n"
```

| Фикстура | Что захватывает        | Когда использовать           |
| -------- | ---------------------- | ---------------------------- |
| `capsys` | `sys.stdout`, `sys.stderr` | Вывод Python (print, logging) |
| `capfd`  | Файловые дескрипторы 1, 2 | Вывод C-расширений, subprocess |

### 6. Snapshot-тестирование

Snapshot-тестирование сохраняет вывод тестируемой функции и при последующих
запусках сравнивает с сохранённым «снимком». Это полезно для сложных структур
данных, HTML-вывода, конфигураций.

Библиотека `syrupy` — самый популярный snapshot-плагин для pytest:

```bash
pip install syrupy
```

```python
import pytest


def generate_report(data: list[dict]) -> str:
    """Генерирует HTML-отчёт по данным."""
    rows = "".join(
        f"<tr><td>{d['name']}</td><td>{d['score']}</td></tr>"
        for d in data
    )
    return f"<table>{rows}</table>"


def test_report_snapshot(snapshot) -> None:
    """Snapshot-тест: первый запуск создаёт снимок, последующие — сравнивают."""
    data = [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 87},
        {"name": "Charlie", "score": 92},
    ]
    report = generate_report(data)
    assert report == snapshot


def test_dict_snapshot(snapshot) -> None:
    """Snapshot-тест для словаря."""
    config = {
        "database": {"host": "localhost", "port": 5432},
        "cache": {"backend": "redis", "ttl": 300},
        "features": {"dark_mode": True, "beta": False},
    }
    assert config == snapshot(name="app_config")


def test_snapshot_update() -> None:
    """
    Для обновления снимков:
        pytest --snapshot-update
    """
    pass
```

✅ **Идиоматично:** snapshot-тесты для сложных/объёмных ожидаемых значений.

❌ **Антипаттерн:** snapshot-тесты для простых скалярных значений (числа, строки) —
обычный `assert` проще и понятнее.

### 7. Property-based testing с Hypothesis

Property-based testing (тестирование на основе свойств) вместо конкретных
примеров проверяет **инварианты** — свойства, которые должны выполняться для
любых входных данных:

```bash
pip install hypothesis
```

```python
from hypothesis import given, strategies as st


def reverse_list(lst: list) -> list:
    return lst[::-1]


@given(st.lists(st.integers()))
def test_reverse_twice_is_identity(lst: list[int]) -> None:
    """Двойной разворот возвращает исходный список — для ЛЮБОГО списка."""
    assert reverse_list(reverse_list(lst)) == lst


@given(st.lists(st.integers()))
def test_reverse_preserves_length(lst: list[int]) -> None:
    """Разворот сохраняет длину списка."""
    assert len(reverse_list(lst)) == len(lst)


@given(st.lists(st.integers()))
def test_reverse_preserves_elements(lst: list[int]) -> None:
    """Разворот сохраняет все элементы (мультимножество)."""
    assert sorted(reverse_list(lst)) == sorted(lst)
```

Hypothesis генерирует сотни тестовых случаев, включая краевые:
пустой список, список из одного элемента, очень большой список, список с
дубликатами, список с `None` (если разрешено).

#### 7.1. Стратегии Hypothesis

```python
from hypothesis import given, strategies as st, assume


@given(
    st.integers(min_value=0, max_value=100),
    st.integers(min_value=0, max_value=100),
)
def test_addition_commutative(a: int, b: int) -> None:
    assert a + b == b + a


@given(st.text(alphabet="abcdef", min_size=1, max_size=20))
def test_string_reversal(s: str) -> None:
    reversed_twice = s[::-1][::-1]
    assert reversed_twice == s


@given(st.dictionaries(st.text(), st.integers()))
def test_dict_roundtrip(d: dict) -> None:
    """Сериализация и десериализация словаря."""
    import json
    serialized = json.dumps(d)
    deserialized = json.loads(serialized)
    assert deserialized == d


@given(st.floats(allow_nan=False, allow_infinity=False))
def test_square_is_nonnegative(x: float) -> None:
    assert x * x >= 0


@given(st.integers(), st.integers())
def test_division_property(a: int, b: int) -> None:
    assume(b != 0)  # исключаем деление на ноль
    quotient = a / b
    assert isinstance(quotient, float)
```

#### 7.2. Когда использовать property-based тесты

| Ситуация                                    | Подход               |
| ------------------------------------------- | -------------------- |
| Простая бизнес-логика с известными случаями | Примеры (parametrize) |
| Функция с математическими инвариантами      | Property-based       |
| Сериализация / десериализация               | Property-based       |
| Кодирование / декодирование                 | Property-based       |
| Сортировка, фильтрация, преобразования      | Property-based       |
| Критичная по безопасности логика            | Property-based + фаззинг |

### 8. Организация тестов: unit, integration, e2e

Тестовая пирамида — фундаментальный принцип организации тестов:

```
       /\
      /E2E\          ← Медленные, дорогие, мало
     /------\
    /Integration\    ← Средние
   /------------\
  /    Unit       \  ← Быстрые, дешёвые, много
 /----------------\
```

| Уровень       | Что проверяет              | Скорость | Количество | Пример                          |
| ------------- | -------------------------- | -------- | ---------- | ------------------------------- |
| Unit          | Одну функцию/класс         | мс       | Много      | `test_deposit`                  |
| Integration   | Взаимодействие модулей     | сек      | Средне     | `test_user_service_with_db`     |
| E2E           | Сквозной сценарий          | мин      | Мало       | `test_user_registration_flow`   |

#### 8.1. Организация каталогов

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/
│   ├── test_database.py
│   ├── test_api.py
│   └── test_cache.py
└── e2e/
    └── test_user_flow.py
```

#### 8.2. Маркеры для выборочного запуска

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests (> 1 sec)",
]
```

```bash
pytest -m unit              # только unit
pytest -m "not e2e"         # исключить e2e
pytest -m "unit or integration"  # unit + integration
```

### 9. Именование тестов и тестовых функций

✅ **Идиоматичные имена:**

```python
def test_deposit_increases_balance() -> None:
    """Что_делает_при_каком_условии."""
    ...

def test_withdraw_insufficient_funds_raises_error() -> None:
    ...

def test_empty_cart_has_zero_total() -> None:
    ...

def test_user_cannot_login_with_expired_token() -> None:
    ...
```

❌ **Антипаттерны имён:**

```python
def test1(): ...
def test_deposit(): ...           # неясно, что проверяется
def test_deposit_works(): ...     # "works" — неинформативно
def test_deposit_ok(): ...        # "ok" — неинформативно
def test_bug_1234(): ...          # лучше описать, что за баг
```

### 10. Сравнение с аналогами в других экосистемах

#### Spock (Groovy) — BDD-стиль

```groovy
// Spock: Given-When-Then встроен в синтаксис
def "deposit increases balance"() {
    given: "a bank account with 100"
    def account = new BankAccount(balance: 100)

    when: "depositing 50"
    account.deposit(50)

    then: "balance is 150"
    account.balance == 150
}
```

#### Jasmine (JavaScript) — describe/it

```javascript
// Jasmine: BDD-стиль на JavaScript
describe("BankAccount", () => {
  let account;

  beforeEach(() => {
    account = new BankAccount(100);
  });

  it("increases balance on deposit", () => {
    account.deposit(50);
    expect(account.balance).toBe(150);
  });

  it("throws on insufficient funds", () => {
    expect(() => account.withdraw(200)).toThrowError("Insufficient funds");
  });
});
```

#### Cucumber (BDD) — Gherkin-синтаксис

```gherkin
# Cucumber: тесты на естественном языке
Feature: Bank Account
  Scenario: Deposit increases balance
    Given a bank account with balance 100
    When I deposit 50
    Then the balance should be 150

  Scenario: Withdraw with insufficient funds
    Given a bank account with balance 100
    When I withdraw 200
    Then an error "Insufficient funds" should be raised
```

Python-эквивалент Cucumber — `behave`:

```python
# features/steps/bank_steps.py
from behave import given, when, then

@given("a bank account with balance {amount:d}")
def step_account(context, amount: int) -> None:
    context.account = BankAccount(balance=amount)

@when("I deposit {amount:d}")
def step_deposit(context, amount: int) -> None:
    context.account.deposit(amount)

@then("the balance should be {expected:d}")
def step_balance(context, expected: int) -> None:
    assert context.account.balance == expected
```

---

## Практическое задание

### Цель
Применить все изученные паттерны к тестированию библиотеки для работы с
JSON-конфигурациями.

### Исходный код (`src/config.py`)

```python
import json
import warnings
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """Ошибка конфигурации."""


class Config:
    """Чтение и валидация JSON-конфигураций."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            raise ConfigError(f"Config file not found: {self.path}")
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {self.path}: {e}") from e
        self._loaded = True
        self._validate()
        return self._data

    def _validate(self) -> None:
        if "version" not in self._data:
            warnings.warn("Config has no version field", UserWarning)
        if not isinstance(self._data, dict):
            raise ConfigError("Config must be a JSON object")

    def get(self, key: str, default: Any = None) -> Any:
        if not self._loaded:
            raise ConfigError("Config not loaded")
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        if not self._loaded:
            raise ConfigError("Config not loaded")
        return self._data[key]

    def to_env(self) -> dict[str, str]:
        """Преобразует конфигурацию в переменные окружения."""
        if not self._loaded:
            raise ConfigError("Config not loaded")
        return {f"APP_{k.upper()}": str(v) for k, v in self._data.items()}
```

### Задачи

1. **AAA-паттерн (2 балла):** Напишите тесты `test_load_valid_config` и
   `test_get_existing_key` с явным разделением Arrange/Act/Assert.

2. **Given-When-Then (2 балла):** Напишите acceptance-тест
   `test_config_loading_workflow` в стиле GWT с docstring-описанием.

3. **pytest.raises (3 балла):** Проверьте все исключения:
   - `ConfigError` при отсутствии файла
   - `ConfigError` при некорректном JSON
   - `ConfigError` при вызове `get()` до `load()`
   - Проверьте сообщения исключений и цепочки (`__cause__`)

4. **pytest.warns (2 балла):** Проверьте, что `UserWarning` возникает,
   когда в конфигурации нет поля `version`.

5. **capsys (2 балла):** Если добавить `print()`-логирование в `load()`,
   протестируйте вывод через `capsys`.

6. **Property-based (3 балла):** Напишите property-based тест для
   `to_env()`: проверьте, что для любого корректного словаря `to_env()`
   возвращает словарь с ключами в верхнем регистре и префиксом `APP_`.

7. **Snapshot (2 балла):** Напишите snapshot-тест для `to_env()` на
   фиксированном словаре.

### Критерии оценки
- Все тесты проходят
- Использованы AAA И GWT
- Протестированы все исключения и предупреждения
- Property-based тест использует Hypothesis
- snapshot-тест использует syrupy

---

## Дополнительные материалы

### Книги
- John Ferguson Smart, *BDD in Action*, 2nd ed. (Manning, 2022)
- Harry Percival, *Architecture Patterns with Python* (O'Reilly, 2020)
  — Глава 4 о паттернах тестирования.

### Документация
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [syrupy (Snapshot Testing)](https://github.com/syrupy-project/syrupy)
- [behave (BDD for Python)](https://behave.readthedocs.io/)
- [pytest.raises API](https://docs.pytest.org/en/stable/reference/reference.html#pytest-raises)

### Статьи
- Martin Fowler, *Given When Then* (2013), martinfowler.com
- John Hughes, *How to Specify It!* (2019) — введение в property-based testing
- Coda Hale, *Testing on the Toilet: Test Behavior, Not Implementation* (Google)

### Видео
- Zac Hatfield-Dodds, *Property-Based Testing for Python*, PyCon US 2022
- David MacIver, *Escape from Auto-manual Testing with Hypothesis*, PyCon 2019