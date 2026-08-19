---
title: "pytest: философия, фикстуры и параметризация"
order: 1
tags:
  - pytest
  - тестирование
  - фикстуры
  - параметризация
prerequisites: "Функции, декораторы, модули"
objective: "Освоить pytest: от простых тестов до фикстур и параметризованных тестов"
---

# pytest: философия, фикстуры и параметризация

## Введение

pytest — самый популярный тестовый фреймворк в экосистеме Python. Он заменил
собой встроенный модуль `unittest` благодаря минималистичному синтаксису,
мощной системе плагинов и богатой функциональности «из коробки». После
прохождения этого урока вы сможете писать тесты быстрее, тратить меньше
времени на отладку и организовывать тестовый код так, чтобы он оставался
читаемым даже в больших проектах.

### Почему не unittest?

Встроенный модуль `unittest` создавался по образцу JUnit (Java) и унаследовал
его многословность: наследование от `TestCase`, методы `setUp` / `tearDown`,
`self.assertEqual(...)`. Это работает, но заставляет писать больше кода, чем
нужно, и затрудняет чтение тестов. pytest устраняет этот шум:

| Аспект                 | unittest                          | pytest                                  |
| ---------------------- | --------------------------------- | --------------------------------------- |
| Обнаружение тестов     | Классы-наследники `TestCase`      | Любая функция `test_*` или класс `Test*` |
| Проверка (assertion)   | `self.assertEqual(a, b)`          | `assert a == b`                         |
| Подготовка контекста   | `setUp` / `tearDown`              | Фикстуры `@pytest.fixture`              |
| Параметризация        | `@parameterized` (сторонняя)       | `@pytest.mark.parametrize` (встроенная)  |
| Пропуск тестов         | `@unittest.skip`                  | `@pytest.mark.skip` / `skipif` / `xfail`|
| Плагины                | Ограниченные                      | Более 1000+ плагинов                    |
| Вывод при падении      | Минимальный                       | Подробный diff, locals, самые длинные строки |

### Сравнение с другими экосистемами

| Язык / Фреймворк   | Подход                          | Сложность интеграции |
| ------------------ | ------------------------------- | -------------------- |
| Python / pytest    | Функции + фикстуры + плагины    | Низкая               |
| Java / JUnit 5     | Аннотации + Extensions          | Средняя              |
| JavaScript / Jest  | Функции + моки + снапшоты       | Низкая               |
| C++ / Google Test  | Макросы + фикстуры              | Высокая              |
| Rust / встроенные  | `#[test]` + `assert!`           | Низкая               |

JUnit 5 требует аннотаций `@Test`, `@BeforeEach`, `@ParameterizedTest` и
расширений. Jest похож на pytest функциональным стилем, но фикстуры
заменяются `beforeEach`/`afterEach` в блоках `describe`. Google Test построен
на макросах `TEST()`, `EXPECT_EQ()` и классах-фикстурах — это самый
многословный вариант.

pytest выигрывает за счёт автоматического обнаружения тестов (discovery), assert
интроспекции и экосистемы плагинов. Этим трём темам и посвящён данный урок.

---

## Основная часть

### 1. Установка и первый запуск

```bash
pip install pytest
```

Создайте файл `test_first.py`:

```python
def add(a: int, b: int) -> int:
    return a + b


def test_add_positive():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, -1) == -2


def test_add_zero():
    assert add(0, 5) == 5
    assert add(5, 0) == 5
```

Запуск:

```bash
pytest test_first.py -v
```

Вывод покажет три пройденных теста. Флаг `-v` включает verbose-режим с
названиями тестов. Флаг `-s` показывает вывод `print()`, `-x` останавливается
после первой ошибки, `--lf` перезапускает только упавшие тесты из предыдущего
запуска.

### 2. Автоматическое обнаружение тестов (Test Discovery)

pytest находит тесты по следующим правилам:

- Файлы с именем `test_*.py` или `*_test.py` в текущем каталоге и подкаталогах.
- Функции с именем `test_*` внутри этих файлов.
- Классы с именем `Test*` (без метода `__init__`), содержащие методы `test_*`.

```python
# test_discovery.py

class TestCalculator:
    def test_add(self):
        assert 1 + 1 == 2

    def test_subtract(self):
        assert 3 - 1 == 2

    # Этот метод НЕ будет обнаружен — имя не начинается с test_
    def helper(self):
        return 42
```

Структура каталога типового проекта:

```
project/
├── src/
│   └── calculator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_calculator.py
│   └── test_integration.py
└── pyproject.toml
```

### 3. `assert` против `self.assertEqual`

Ключевое преимущество pytest — использование встроенного оператора `assert`.
pytest перехватывает `AssertionError` и выводит развёрнутый diff:

```python
def test_assert_introspection():
    result = {"a": 1, "b": [2, 3, 4]}
    expected = {"a": 1, "b": [2, 3, 5]}
    assert result == expected
```

Вывод:
```
E   AssertionError: assert {'a': 1, 'b': [2, 3, 4]} == {'a': 1, 'b': [2, 3, 5]}
E     Differing items:
E     {'b': [2, 3, 4]} != {'b': [2, 3, 5]}
E     Full diff:
E       {
E        'a': 1,
E     -  'b': [2, 3, 5],
E     ?              ^
E     +  'b': [2, 3, 4],
E     ?              ^
E       }
```

Сравните с `unittest`:

```python
import unittest

class TestOld(unittest.TestCase):
    def test_assert(self):
        self.assertEqual({"a": 1, "b": [2, 3, 4]}, {"a": 1, "b": [2, 3, 5]})
```

В `unittest` diff тоже есть, но он менее наглядный, а синтаксис многословный.
Кроме того, `assert` работает с любым выражением, а `self.assert*` требует
запоминания десятков методов (`assertDictEqual`, `assertListEqual`, ...).

✅ **Идиоматично (pytest):**

```python
def test_idiomatic():
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
    assert [1, 2, 3] == [1, 2, 3]
    assert {"a": 1} == {"a": 1}
    assert 0.1 + 0.2 == pytest.approx(0.3)    # сравнение float
    assert None is None
    assert "abc" in "abcdef"
```

❌ **Антипаттерн (унаследованный unittest-стиль):**

```python
import unittest

class TestAntiPattern(unittest.TestCase):
    def test_everything(self):
        self.assertEqual(1 + 1, 2)
        self.assertIn("abc", "abcdef")
        self.assertAlmostEqual(0.1 + 0.2, 0.3)
        self.assertIsNone(None)
```

### 4. Фикстуры: `@pytest.fixture`

Фикстура — это функция, которая подготавливает контекст для теста: данные,
подключения, временные файлы. pytest внедряет фикстуры в тесты через имена
параметров:

```python
import pytest


@pytest.fixture
def sample_user() -> dict:
    """Фикстура, возвращающая тестового пользователя."""
    return {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "is_active": True,
    }


def test_user_name(sample_user: dict) -> None:
    assert sample_user["name"] == "Alice"


def test_user_active(sample_user: dict) -> None:
    assert sample_user["is_active"] is True
```

pytest автоматически вызывает `sample_user` и передаёт результат в тесты,
которые запрашивают его по имени параметра.

#### 4.1. Область видимости (scope)

Фикстуры создаются заново для каждого теста по умолчанию (scope=`"function"`).
Это гарантирует изоляцию. Но дорогие фикстуры (подключение к БД) можно
переиспользовать:

```python
import pytest
import time


@pytest.fixture(scope="module")
def expensive_resource() -> list[int]:
    """Создаётся ОДИН раз на весь модуль."""
    print("\n[setup] Создаю дорогой ресурс...")
    time.sleep(0.1)  # имитация затрат
    return [1, 2, 3]


@pytest.fixture(scope="session")
def db_connection() -> str:
    """Создаётся ОДИН раз на всю сессию."""
    print("\n[setup] Подключаюсь к БД...")
    return "db_connection_string"


def test_a(expensive_resource: list[int]) -> None:
    assert len(expensive_resource) == 3


def test_b(expensive_resource: list[int]) -> None:
    expensive_resource.append(4)
    assert len(expensive_resource) == 4  # мутация повлияет на test_a, если
                                         # он запустится после test_b!
```

> ⚠️ **Важно:** фикстуры с scope `"module"` или `"session"` не должны
> мутировать состояние — это нарушает изоляцию тестов. Если тест изменяет
> данные, используйте scope `"function"` (по умолчанию).

| scope      | Создаётся                   | Пример использования            |
| ---------- | --------------------------- | ------------------------------- |
| `function` | На каждый тест (по умолч.)  | Большинство фикстур             |
| `class`    | На каждый тестовый класс    | Общий контекст для группы тестов|
| `module`   | На каждый модуль (.py файл) | Дорогое вычисление, read-only   |
| `session`  | На всю тестовую сессию      | Подключение к БД, запуск сервера|

#### 4.2. `autouse` — автоматическое применение

```python
import pytest
import time


@pytest.fixture(autouse=True)
def measure_time() -> None:
    """Автоматически замеряет время каждого теста."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"\n[autouse] Тест занял {elapsed:.4f} сек")


def test_fast() -> None:
    assert 1 + 1 == 2


def test_slow() -> None:
    time.sleep(0.2)
    assert True
```

#### 4.3. Очистка с `yield` (teardown)

```python
import pytest
from pathlib import Path


@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Создаёт временный файл и удаляет его после теста."""
    file = tmp_path / "data.txt"
    file.write_text("hello")
    yield file          # тест выполняется здесь
    # код после yield — teardown
    file.unlink(missing_ok=True)
    print(f"\n[teardown] Файл {file} удалён")


def test_read_file(temp_file: Path) -> None:
    content = temp_file.read_text()
    assert content == "hello"
```

#### 4.4. Композиция фикстур

Фикстуры могут зависеть от других фикстур:

```python
import pytest


@pytest.fixture
def base_url() -> str:
    return "https://api.example.com"


@pytest.fixture
def auth_token() -> str:
    return "Bearer secret-token"


@pytest.fixture
def api_client(base_url: str, auth_token: str) -> dict:
    """Составная фикстура: клиент с URL и токеном."""
    return {
        "base_url": base_url,
        "headers": {"Authorization": auth_token},
        "timeout": 10,
    }


def test_api_client(api_client: dict) -> None:
    assert api_client["base_url"] == "https://api.example.com"
    assert "Authorization" in api_client["headers"]
    assert api_client["timeout"] == 10
```

### 5. `conftest.py` — общие фикстуры

Фикстуры, определённые в `conftest.py`, автоматически доступны всем тестам в
том же каталоге и подкаталогах. Это механизм наследования фикстур:

```
tests/
├── conftest.py          # фикстуры уровня всего проекта
├── unit/
│   ├── conftest.py      # фикстуры только для unit-тестов
│   └── test_core.py
└── integration/
    ├── conftest.py      # фикстуры только для integration-тестов
    └── test_api.py
```

```python
# tests/conftest.py
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_data() -> list[dict]:
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]
```

✅ **Идиоматично:** конфигурация в `conftest.py` + `pyproject.toml`.

❌ **Антипаттерн:** копирование одной и той же фикстуры в каждый тестовый файл.

### 6. Параметризация: `@pytest.mark.parametrize`

Параметризация позволяет запустить один тест с разными входными данными:

```python
import pytest


def is_palindrome(s: str) -> bool:
    """Проверяет, является ли строка палиндромом."""
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("radar", True),
        ("hello", False),
        ("A man a plan a canal Panama", True),
        ("", True),
        ("a", True),
        ("ab", False),
        ("racecar", True),
        ("Python", False),
    ],
    ids=[
        "radar",
        "hello",
        "panama",
        "empty",
        "single_char",
        "two_different",
        "racecar",
        "python",
    ],
)
def test_is_palindrome(input_str: str, expected: bool) -> None:
    assert is_palindrome(input_str) == expected
```

Запуск покажет 8 отдельных тестов с понятными именами. Параметр `ids` задаёт
человеко-читаемые суффиксы; без него pytest генерирует имена автоматически.

#### 6.1. Комбинаторная параметризация

Несколько декораторов `@pytest.mark.parametrize` перемножаются:

```python
import pytest


def multiply(a: int, b: int) -> int:
    return a * b


@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", [10, 100])
def test_multiply_commutative(a: int, b: int) -> None:
    assert multiply(a, b) == multiply(b, a)
    assert multiply(a, b) == a * b
```

Это породит 3 × 2 = 6 тестов: (1,10), (1,100), (2,10), (2,100), (3,10), (3,100).

#### 6.2. Параметризация фикстур

```python
import pytest


@pytest.fixture(params=["sqlite", "postgresql", "mongodb"])
def db_backend(request) -> str:
    """Фикстура, которая параметризует все тесты, использующие её."""
    backend = request.param
    # Здесь можно инициализировать реальное подключение
    yield backend
    # Здесь — очистка


def test_db_connect(db_backend: str) -> None:
    assert db_backend in {"sqlite", "postgresql", "mongodb"}
```

### 7. Маркеры: `skip`, `skipif`, `xfail`

```python
import pytest
import sys


@pytest.mark.skip(reason="Функционал ещё не реализован")
def test_future_feature() -> None:
    pass


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Требуется Python 3.10+")
def test_pattern_matching() -> None:
    match 42:
        case int():
            assert True
        case _:
            pytest.fail("Недостижимо")


@pytest.mark.xfail(reason="Известный баг #1234", strict=True)
def test_known_bug() -> None:
    assert 1 / 0 == 0  # упадёт, но тест будет помечен как xfail (ожидаемо)


@pytest.mark.xfail(sys.platform == "win32", reason="Не работает на Windows")
def test_unix_only() -> None:
    import os
    assert os.getuid() == 0  # упадёт на Windows, но это ожидаемо
```

| Маркер        | Поведение                                                   |
| ------------- | ----------------------------------------------------------- |
| `skip`        | Всегда пропускает тест                                       |
| `skipif`      | Пропускает, если условие истинно                             |
| `xfail`       | Ожидает падение: если тест упал — `xfail`, если прошёл — `xpass` |
| `xfail(strict=True)` | Если тест неожиданно прошёл — ошибка                  |

✅ **Идиоматично:** `xfail` для известных багов с `reason` и ссылкой на тикет.

❌ **Антипаттерн:** `xfail` без `reason` или `strict=True` — скрывает реальные
регрессии.

### 8. Конфигурация: `pytest.ini` и `pyproject.toml`

```ini
; pytest.ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: медленные тесты (deselect with '-m "not slow"')
    integration: интеграционные тесты
    smoke: дымовые тесты для быстрой проверки
```

Или в `pyproject.toml` (рекомендуется для современных проектов):

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
addopts = ["-v", "--tb=short", "--strict-markers"]
markers = [
    "slow: медленные тесты",
    "integration: интеграционные тесты",
    "smoke: дымовые тесты",
]
```

Запуск с фильтрацией по маркерам:

```bash
pytest -m "not slow"          # исключить медленные
pytest -m "integration"       # только интеграционные
pytest -m "smoke or unit"     # smoke ИЛИ unit
```

### 9. Сравнение с JUnit 5, Jest и Google Test

#### JUnit 5 (Java) — аналог параметризации

```java
// JUnit 5: многословно, но типобезопасно
@ParameterizedTest
@CsvSource({
    "radar, true",
    "hello, false",
    "A man a plan a canal Panama, true"
})
void testIsPalindrome(String input, boolean expected) {
    assertEquals(expected, Palindrome.isPalindrome(input));
}
```

#### Jest (JavaScript) — аналог фикстур

```javascript
// Jest: beforeEach/afterEach вместо фикстур
describe("Calculator", () => {
  let calculator;

  beforeEach(() => {
    calculator = new Calculator();  // аналог фикстуры
  });

  test.each([
    [1, 2, 3],
    [-1, -1, -2],
    [0, 5, 5],
  ])("add(%i, %i) = %i", (a, b, expected) => {
    expect(calculator.add(a, b)).toBe(expected);
  });
});
```

#### Google Test (C++) — аналог тестовой функции

```cpp
// Google Test: макросы и фикстуры-классы
TEST(CalculatorTest, AddPositive) {
    Calculator calc;
    EXPECT_EQ(calc.add(2, 3), 5);
}

class CalculatorFixture : public ::testing::Test {
protected:
    void SetUp() override {
        calc = Calculator{};
    }
    Calculator calc;
};

TEST_F(CalculatorFixture, AddNegative) {
    EXPECT_EQ(calc.add(-1, -1), -2);
}
```

Ключевое преимущество pytest — **минимальный boilerplate**: тестовая функция
выглядит как обычная функция Python с `assert`, а не как метод класса с
макросами или аннотациями.

---

## Практическое задание

### Цель
Написать тесты для модуля работы с банковским счётом, используя все изученные
инструменты: фикстуры, параметризацию, маркеры, `conftest.py`.

### Исходный код (сохраните как `src/bank.py`)

```python
from dataclasses import dataclass
from decimal import Decimal


class InsufficientFundsError(Exception):
    """Недостаточно средств на счёте."""
    pass


@dataclass
class BankAccount:
    account_id: str
    owner: str
    balance: Decimal = Decimal("0.00")

    def deposit(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError("Сумма депозита должна быть положительной")
        self.balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Недостаточно средств: баланс {self.balance}, "
                f"запрошено {amount}"
            )
        self.balance -= amount

    def transfer(self, target: "BankAccount", amount: Decimal) -> None:
        self.withdraw(amount)
        target.deposit(amount)
```

### Задачи

1. **Фикстуры (3 балла):** Создайте `conftest.py` с фикстурами:
   - `empty_account` — счёт с нулевым балансом
   - `funded_account` — счёт с балансом 1000.00
   - `two_accounts` — два счёта для тестирования переводов

2. **Базовые тесты (3 балла):** Проверьте `deposit`, `withdraw`, `transfer`
   с корректными данными. Используйте `pytest.approx` для сравнения Decimal.

3. **Параметризация (4 балла):** Параметризуйте тесты:
   - `test_deposit` с разными суммами (положительные, включая копейки)
   - `test_withdraw_insufficient_funds` с разными комбинациями баланс/запрос
   - `test_invalid_amounts` с нулевыми и отрицательными суммами

4. **Маркеры (2 балла):** Пометьте медленные тесты маркером `slow` и
   настройте `pyproject.toml` для регистрации этого маркера.

5. **Исключения (3 балла):** Проверьте, что `withdraw` и `deposit`
   выбрасывают правильные исключения с правильными сообщениями.

### Ожидаемая структура проекта

```
bank_project/
├── src/
│   ├── __init__.py
│   └── bank.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_bank.py
└── pyproject.toml
```

### Критерии оценки
- Все тесты проходят: `pytest tests/ -v`
- Не менее 15 тестовых сценариев
- Использованы фикстуры, параметризация и маркеры
- Код соответствует PEP 8

---

## Дополнительные материалы

### Книги
- Brian Okken, *Python Testing with pytest*, 2nd ed. (Pragmatic Bookshelf, 2022)
  — исчерпывающее руководство от простого к сложному.
- Harry Percival, *Architecture Patterns with Python* (O'Reilly, 2020)
  — главы 4-6 о тестировании в контексте чистой архитектуры.

### Документация
- [pytest Official Documentation](https://docs.pytest.org/en/stable/)
- [pytest Fixtures Reference](https://docs.pytest.org/en/stable/reference/fixtures.html)
- [pytest Parametrization Guide](https://docs.pytest.org/en/stable/how-to/parametrize.html)

### Видео
- Anthony Sottile, *pytest — why and how*, PyCon 2020
- Brian Okken, *pytest Fixtures: The Life of a Fixture*, PyCon 2021

### Инструменты
- `pytest --fixtures` — показать все доступные фикстуры
- `pytest --collect-only` — показать, какие тесты будут запущены, без запуска
- `pytest --durations=10` — показать 10 самых медленных тестов
- `pytest --lf` — перезапустить только упавшие тесты
- `pytest --ff` — запустить упавшие тесты первыми, затем остальные