---
title: "Интеграция с C/C++: Cython, ctypes, cffi, pybind11"
order: 3
tags: ["C", "C++", "Cython", "ctypes", "cffi", "pybind11"]
prerequisites: "Урок 2, базовое знание C/C++"
objective: "Освоить способы интеграции Python с C/C++ для критически важных участков кода"
---

# Интеграция с C/C++: Cython, ctypes, cffi, pybind11

## Введение

> "Если 1% кода потребляет 99% времени, напишите этот 1% на C." — практическое правило performance-инженера.

Когда микро-оптимизации Python исчерпаны (Урок 2), а PyPy не даёт нужного прироста, остаётся последний рубеж: **нативный код**. Python предоставляет несколько способов интеграции с C/C++, от простого вызова разделяемых библиотек до написания полноценных расширений.

В этом уроке мы разберём:

- **ctypes** — вызов C-библиотек из Python без компиляции;
- **cffi** — современный FFI с чистым синтаксисом;
- **Cython** — надмножество Python, компилируемое в C-расширения;
- **pybind11 / nanobind** — C++ библиотеки для создания Python-модулей;
- **Сборка** расширений с setuptools.

### 🎯 Цель урока

Освоить способы интеграции Python с C/C++ для критически важных участков кода.

### 📋 Предпосылки

Урок 2 (оптимизация Python), базовое знание C/C++ (указатели, структуры, компиляция).

---

## Основная часть

### 1. Когда стоит обращаться к C/C++?

Правило 1%: только для горячих путей, которые исчерпали лимит Python-оптимизаций.

#### Дерево решений

```text
Профилирование показало горячую функцию (Урок 1)
    │
    ├─ Применили микро-оптимизации (Урок 2)
    │      │
    │      ├─ Достаточно быстро? → ✅ Остановиться
    │      │
    │      └─ Всё ещё медленно?
    │             │
    │             ├─ Числовые вычисления? → NumPy / Numba
    │             │
    │             ├─ Много мелких операций? → PyPy
    │             │
    │             └─ Ничего не помогло? → C/C++ расширение
```

#### Хорошие кандидаты для C/C++

| Категория           | Примеры                                  |
|---------------------|------------------------------------------|
| Числовые алгоритмы  | Умножение матриц, БПФ, хеширование       |
| Парсинг             | JSON (orjson), XML (lxml), MessagePack   |
| Криптография        | AES, SHA, RSA (cryptography)             |
| Сжатие              | gzip, zstd, lz4                          |
| Обработка изображений | Pillow (внутри C), OpenCV bindings     |
| Сетевые протоколы   | HTTP/2 парсинг заголовков                |

#### Плохие кандидаты для C/C++

| Категория           | Почему не стоит                          |
|---------------------|------------------------------------------|
| I/O-bound код       | Ожидание диска/сети — не CPU             |
| Код с бизнес-логикой| Сложность поддержки перевешивает профит  |
| Редко вызываемый код| Оверхед перехода Python↔C съедает выгоду |
| Прототипы           | Скорость разработки важнее               |

---

### 2. ctypes: вызов C-библиотек без компиляции

`ctypes` — модуль стандартной библиотеки для вызова функций из разделяемых библиотек (.so, .dll, .dylib). Не требует компилятора — идеально для быстрого прототипирования.

#### 2.1 Базовый пример: вызов стандартной библиотеки C

```python
import ctypes
import platform
from pathlib import Path

# Определяем библиотеку в зависимости от ОС
system = platform.system()
if system == "Windows":
    libc = ctypes.CDLL("msvcrt.dll")
elif system == "Darwin":
    libc = ctypes.CDLL("libc.dylib")
else:
    libc = ctypes.CDLL("libc.so.6")


# Объявляем сигнатуру функции
libc.strlen.argtypes = [ctypes.c_char_p]
libc.strlen.restype = ctypes.c_size_t

# Вызов
text = b"Hello, C from Python!"
length = libc.strlen(text)
print(f"Длина строки '{text.decode()}': {length}")


# Пример: вычисление косинуса через libm
if system == "Windows":
    libm = ctypes.CDLL("msvcrt.dll")
else:
    libm = ctypes.CDLL("libm.so.6")

libm.cos.argtypes = [ctypes.c_double]
libm.cos.restype = ctypes.c_double

print(f"cos(0) = {libm.cos(0.0)}")
print(f"cos(π/2) = {libm.cos(1.57079632679)}")
```

#### 2.2 Создание собственной C-библиотеки

```c
/* Файл: fast_math.c — компилируется в разделяемую библиотеку */
#include <stdint.h>

/* Сумма массива целых чисел */
int64_t sum_array(const int64_t *arr, int64_t len) {
    int64_t total = 0;
    for (int64_t i = 0; i < len; i++) {
        total += arr[i];
    }
    return total;
}

/* Число Фибоначчи — итеративно */
int64_t fibonacci(int64_t n) {
    if (n < 2) return n;
    int64_t a = 0, b = 1, tmp;
    for (int64_t i = 2; i <= n; i++) {
        tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

/* Проверка: является ли строка палиндромом */
int is_palindrome(const char *s, int64_t len) {
    for (int64_t i = 0; i < len / 2; i++) {
        if (s[i] != s[len - 1 - i]) return 0;
    }
    return 1;
}
```

Компиляция:

```bash
# Linux / macOS
gcc -shared -o libfastmath.so -fPIC -O2 fast_math.c

# macOS (альтернативно)
gcc -shared -o libfastmath.dylib -fPIC -O2 fast_math.c

# Windows (MSVC)
cl /LD /O2 fast_math.c /Fe:libfastmath.dll
```

Вызов из Python:

```python
import ctypes
import timeit
from pathlib import Path


# Загрузка библиотеки
lib_path = Path("libfastmath.so")  # или .dll / .dylib
lib = ctypes.CDLL(str(lib_path))

# Объявление сигнатур
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_int64]
lib.sum_array.restype = ctypes.c_int64

lib.fibonacci.argtypes = [ctypes.c_int64]
lib.fibonacci.restype = ctypes.c_int64

lib.is_palindrome.argtypes = [ctypes.c_char_p, ctypes.c_int64]
lib.is_palindrome.restype = ctypes.c_int


def py_sum_array(arr: list[int]) -> int:
    """Python-версия для сравнения."""
    return sum(arr)


def c_sum_array(arr: list[int]) -> int:
    """C-версия через ctypes."""
    arr_type = ctypes.c_int64 * len(arr)
    c_arr = arr_type(*arr)
    return lib.sum_array(c_arr, len(arr))


# Бенчмарк
data = list(range(10_000_000))

print("=== sum_array: Python vs C (ctypes) ===")
py_time = timeit.timeit(lambda: py_sum_array(data), number=10)
c_time = timeit.timeit(lambda: c_sum_array(data), number=10)
print(f"Python:  {py_time:.4f}s")
print(f"Ctypes:  {c_time:.4f}s")
print(f"Прирост: {py_time / c_time:.1f}x")
```

#### 2.3 ctypes: плюсы и минусы

| ✅ Плюсы                              | ❌ Минусы                                     |
|---------------------------------------|-----------------------------------------------|
| Встроен в стандартную библиотеку      | Ручное объявление argtypes/restype            |
| Не требует компилятора                | Ошибки сигнатур — segfault, а не исключение   |
| Работает с любой C-библиотекой        | Медленный маршалинг Python ↔ C                |
| Идеален для прототипов                | Нет поддержки C++ (только extern "C")         |
|                                       | Передача сложных структур — ручная работа     |

---

### 3. cffi: современный FFI-интерфейс

`cffi` (C Foreign Function Interface) — сторонняя библиотека, решающая проблемы `ctypes`: более чистый синтаксис, лучшая производительность маршалинга, поддержка PyPy.

```bash
pip install cffi
```

#### 3.1 Режим ABI (как ctypes, без компиляции)

```python
from cffi import FFI

ffi = FFI()

# Загружаем существующую библиотеку
lib = ffi.dlopen("./libfastmath.so")

# Объявляем функции
ffi.cdef("""
    int64_t sum_array(const int64_t *arr, int64_t len);
    int64_t fibonacci(int64_t n);
    int is_palindrome(const char *s, int64_t len);
""")

# Вызов
lib.fibonacci(40)  # Работает!
```

#### 3.2 Режим API (компиляция расширения "на лету")

```python
from cffi import FFI

ffi = FFI()

# Заголовочный файл на C (в embed-строке)
ffi.cdef("""
    int64_t sum_array(const int64_t *arr, int64_t len);
    int64_t fibonacci(int64_t n);
""")

# Исходный код на C
source = """
    #include <stdint.h>

    int64_t sum_array(const int64_t *arr, int64_t len) {
        int64_t total = 0;
        for (int64_t i = 0; i < len; i++) {
            total += arr[i];
        }
        return total;
    }

    int64_t fibonacci(int64_t n) {
        if (n < 2) return n;
        int64_t a = 0, b = 1, tmp;
        for (int64_t i = 2; i <= n; i++) {
            tmp = a + b;
            a = b;
            b = tmp;
        }
        return b;
    }
"""

# Компиляция на лету
ffi.set_source(
    "_fastmath_cffi",
    source,
    libraries=[],  # дополнительные библиотеки для линковки
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
```

После компиляции:

```python
from _fastmath_cffi import ffi, lib

# Вызов скомпилированных функций
result = lib.fibonacci(50)
print(f"fibonacci(50) = {result}")

# Массив
data = [1, 2, 3, 4, 5]
c_arr = ffi.new("int64_t[]", data)
total = lib.sum_array(c_arr, len(data))
print(f"sum = {total}")
```

#### 3.3 Сравнение ctypes vs cffi

| Характеристика        | ctypes                          | cffi (ABI)                      | cffi (API)                      |
|-----------------------|---------------------------------|---------------------------------|---------------------------------|
| Компиляция            | Не требуется                    | Не требуется                    | Требуется (C-компилятор)        |
| Скорость маршалинга   | Медленная                       | Быстрая                         | Очень быстрая                   |
| Синтаксис объявлений  | `argtypes = [c_int, ...]`       | `ffi.cdef("int f(int)")`       | `ffi.cdef(...)` + `set_source` |
| Поддержка PyPy         | Ограниченная                    | Полная                          | Полная                          |
| Поддержка C++          | ❌                              | ❌                              | ❌ (только extern "C")          |
| Инлайн-C              | ❌                              | ❌                              | ✅                              |

---

### 4. Cython: Python-подобный синтаксис, C-производительность

Cython — это надмножество Python, которое компилируется в C-расширения. Вы пишете код, похожий на Python, добавляете аннотации типов, и получаете скорость C.

```bash
pip install cython
```

#### 4.1 Первый Cython-модуль

```cython
# Файл: fast_ops.pyx

def fibonacci_py(int n):
    """Обычная Python-функция в Cython — без ускорения."""
    if n < 2:
        return n
    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_cy(int n):
    """Cython с аннотациями типов — компилируется в чистый C-цикл."""
    cdef int a = 0, b = 1, i, tmp
    if n < 2:
        return n
    for i in range(2, n + 1):
        tmp = a + b
        a = b
        b = tmp
    return b


cpdef double sum_of_squares(double[:] arr):
    """cpdef: доступна и из Python, и из Cython.

    Использует typed memoryview для быстрого доступа к массиву.
    """
    cdef:
        double total = 0.0
        Py_ssize_t i
        Py_ssize_t n = arr.shape[0]

    for i in range(n):
        total += arr[i] * arr[i]

    return total


def primes_up_to(int n):
    """Решето Эратосфена — поиск простых чисел до n."""
    cdef:
        int i, j
        list result = []

    # Используем bytearray как битовый массив
    cdef bytearray sieve = bytearray(b'\x01') * (n + 1)
    cdef unsigned char[:] sieve_view = sieve

    sieve_view[0] = 0
    sieve_view[1] = 0

    cdef int limit = int(n ** 0.5)
    for i in range(2, limit + 1):
        if sieve_view[i]:
            for j in range(i * i, n + 1, i):
                sieve_view[j] = 0

    for i in range(2, n + 1):
        if sieve_view[i]:
            result.append(i)

    return result
```

#### 4.2 Сборка с setuptools

```python
# Файл: setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="fast_ops",
    ext_modules=cythonize(
        "fast_ops.pyx",
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,      # Отключаем проверку границ
            "wraparound": False,       # Отключаем отрицательные индексы
            "cdivision": True,         # C-деление (без ZeroDivisionError)
        },
    ),
)
```

```bash
# Сборка
python setup.py build_ext --inplace
```

#### 4.3 Бенчмарк: Python vs Cython

```python
import timeit
import fast_ops


def benchmark_fibonacci() -> None:
    """Сравнение Python и Cython-версий Фибоначчи."""
    n = 100_000

    py_time = timeit.timeit(
        stmt="fib_py(n)",
        setup="def fib_py(n):\n"
              "    if n < 2: return n\n"
              "    a = b = 1\n"
              "    for i in range(2, n):\n"
              "        a, b = b, a + b\n"
              "    return b",
        globals={"n": n},
        number=100,
    )

    cy_time = timeit.timeit(
        stmt="fast_ops.fibonacci_cy(n)",
        globals={"fast_ops": fast_ops, "n": n},
        number=100,
    )

    print(f"Python fibonacci({n}):  {py_time:.4f}s")
    print(f"Cython fibonacci({n}):  {cy_time:.4f}s")
    print(f"Прирост: {py_time / cy_time:.1f}x")


if __name__ == "__main__":
    benchmark_fibonacci()
```

Ожидаемый прирост: 15–50x для числовых алгоритмов.

#### 4.4 Cython: аннотация типов

| Тип Cython | Тип C          | Описание                         |
|------------|----------------|----------------------------------|
| `int`      | `int` (C int)  | Машинное слово (32 или 64 бита)  |
| `long`     | `long`         | Длинное целое                    |
| `float`    | `float`        | 32-битное с плавающей точкой     |
| `double`   | `double`       | 64-битное с плавающей точкой     |
| `bint`     | `int`          | Булево значение (0/1)            |
| `char`     | `char`         | Одиночный байт                   |
| `Py_ssize_t`| `Py_ssize_t`  | Размер контейнера (64 бита)      |
| `double[:]`| typed memoryview| Быстрый доступ к массиву        |

#### 4.5 Cython: директивы компилятора

| Директива          | Значение                       | Когда отключать                |
|--------------------|--------------------------------|--------------------------------|
| `boundscheck`      | Проверка выхода за границы     | Всегда, если уверены в индексах|
| `wraparound`       | Поддержка отрицательных индексов| Всегда, если не нужны          |
| `cdivision`        | C-деление (без исключений)     | Числовые алгоритмы             |
| `nonecheck`        | Проверка на None               | После отладки                  |
| `embedsignature`   | Сохранение сигнатур в docstring| Для интроспекции               |

```cython
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: language_level=3
```

---

### 5. pybind11: C++ для Python

`pybind11` — это header-only C++ библиотека для создания Python-модулей. Используется в крупных проектах: PyTorch, TensorFlow, OpenCV.

```bash
pip install pybind11
```

#### 5.1 Базовый пример

```cpp
// Файл: fast_math.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <cstdint>
#include <cmath>

namespace py = pybind11;

// Быстрая сумма массива (C++ с оптимизациями)
int64_t sum_array(const std::vector<int64_t>& arr) {
    int64_t total = 0;
    for (const auto& val : arr) {
        total += val;
    }
    return total;
}

// Скалярное произведение двух векторов
double dot_product(const std::vector<double>& a, const std::vector<double>& b) {
    if (a.size() != b.size()) {
        throw std::runtime_error("Vectors must have the same size");
    }
    double result = 0.0;
    for (size_t i = 0; i < a.size(); ++i) {
        result += a[i] * b[i];
    }
    return result;
}

// Класс для быстрых геометрических вычислений
class Vector3D {
public:
    double x, y, z;

    Vector3D(double x = 0, double y = 0, double z = 0)
        : x(x), y(y), z(z) {}

    double length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    Vector3D normalize() const {
        double len = length();
        if (len == 0) return Vector3D();
        return Vector3D(x / len, y / len, z / len);
    }

    Vector3D cross(const Vector3D& other) const {
        return Vector3D(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }

    double dot(const Vector3D& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    std::string repr() const {
        return "Vector3D(" + std::to_string(x) + ", "
               + std::to_string(y) + ", " + std::to_string(z) + ")";
    }
};

// Модуль
PYBIND11_MODULE(fast_math, m) {
    m.doc() = "Fast math operations implemented in C++";

    m.def("sum_array", &sum_array,
          "Sum all elements of an int64 array",
          py::arg("arr"));

    m.def("dot_product", &dot_product,
          "Compute dot product of two vectors",
          py::arg("a"), py::arg("b"));

    py::class_<Vector3D>(m, "Vector3D")
        .def(py::init<double, double, double>(),
             py::arg("x") = 0.0, py::arg("y") = 0.0, py::arg("z") = 0.0)
        .def_readwrite("x", &Vector3D::x)
        .def_readwrite("y", &Vector3D::y)
        .def_readwrite("z", &Vector3D::z)
        .def("length", &Vector3D::length)
        .def("normalize", &Vector3D::normalize)
        .def("cross", &Vector3D::cross)
        .def("dot", &Vector3D::dot)
        .def("__repr__", &Vector3D::repr);
}
```

#### 5.2 Сборка с setuptools

```python
# Файл: setup.py
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "fast_math",
        ["fast_math.cpp"],
        cxx_std=17,
        extra_compile_args=["-O3", "-march=native"],
    ),
]

setup(
    name="fast_math",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
```

```bash
pip install .
```

#### 5.3 Использование

```python
import fast_math
import timeit

# C++ sum_array
data = list(range(10_000_000))
print("=== sum_array: Python vs C++ (pybind11) ===")

py_time = timeit.timeit(lambda: sum(data), number=10)
cpp_time = timeit.timeit(lambda: fast_math.sum_array(data), number=10)

print(f"Python: {py_time:.4f}s")
print(f"C++:    {cpp_time:.4f}s")
print(f"Прирост: {py_time / cpp_time:.1f}x")

# Vector3D
v1 = fast_math.Vector3D(1, 2, 3)
v2 = fast_math.Vector3D(4, 5, 6)
print(f"\nv1 = {v1}")
print(f"v1.length() = {v1.length()}")
print(f"v1.dot(v2) = {v1.dot(v2)}")
print(f"v1.cross(v2) = {v1.cross(v2)}")
```

---

### 6. nanobind: новое поколение биндингов

`nanobind` — это преемник pybind11 от того же автора (Wenzel Jakob). Он меньше, быстрее и создан с учётом уроков pybind11.

```bash
pip install nanobind
```

```cpp
// Файл: fast_math_nb.cpp
#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <vector>
#include <cstdint>

namespace nb = nanobind;

int64_t sum_array(const std::vector<int64_t>& arr) {
    int64_t total = 0;
    for (const auto& val : arr) {
        total += val;
    }
    return total;
}

NB_MODULE(fast_math_nb, m) {
    m.def("sum_array", &sum_array, nb::arg("arr"));
}
```

```python
# setup.py
from setuptools import setup
from nanobind.setup_helpers import NanobindExtension, build_ext

setup(
    name="fast_math_nb",
    ext_modules=[NanobindExtension("fast_math_nb", ["fast_math_nb.cpp"])],
    cmdclass={"build_ext": build_ext},
)
```

#### pybind11 vs nanobind: сравнение

| Характеристика   | pybind11              | nanobind                  |
|-------------------|-----------------------|---------------------------|
| Размер бинарника  | Больше               | Меньше (на ~30–50%)       |
| Скорость компиляции| Медленнее            | Быстрее                   |
| Рантайм-оверхед   | Выше                  | Ниже                      |
| Стабильность      | Зрелая (с 2015)       | Молодая (с 2023)          |
| Экосистема        | Огромная              | Растущая                  |
| Миграция          | —                     | Частичная совместимость   |

---

### 7. Сравнение всех подходов

| Подход      | Язык       | Скорость       | Сложность | Сборка          | Когда использовать               |
|-------------|------------|----------------|-----------|-----------------|----------------------------------|
| ctypes      | C (FFI)    | ⭐⭐            | ⭐         | Не нужна        | Быстрый прототип, вызов системных библиотек |
| cffi (ABI)  | C (FFI)    | ⭐⭐⭐           | ⭐         | Не нужна        | Чистый синтаксис, PyPy           |
| cffi (API)  | C (inline) | ⭐⭐⭐⭐          | ⭐⭐        | Нужна           | Средние проекты с C-логикой      |
| Cython      | .pyx       | ⭐⭐⭐⭐⭐         | ⭐⭐⭐       | Нужна           | Математика, алгоритмы, NumPy-интеграция |
| pybind11    | C++        | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐      | Нужна           | Крупные проекты, ООП, C++ библиотеки |
| nanobind    | C++        | ⭐⭐⭐⭐⭐         | ⭐⭐⭐⭐      | Нужна           | Новые проекты, когда важен размер |

---

### 8. Сравнение с другими языками

#### Java JNI / Panama

| Аспект                | Python (ctypes/cffi/cython)       | Java (JNI / Project Panama)          |
|-----------------------|-----------------------------------|--------------------------------------|
| Вызов нативного кода  | `ctypes.CDLL("lib.so")`           | `System.loadLibrary("lib")` + JNI    |
| Сложность             | Низкая-средняя                    | Высокая (JNI header generation)      |
| Современный подход    | cffi, pybind11                    | Project Panama (Foreign Function)    |
| Маршалинг             | Ручной или автоматический         | Ручной (JNI) / автоматический (Panama) |
| Производительность    | Высокая (Cython) / средняя (ctypes) | Высокая (прямой доступ к памяти) |

#### Node.js Native Addons

| Аспект                | Python                             | Node.js                              |
|-----------------------|------------------------------------|--------------------------------------|
| Нативный модуль       | Cython, pybind11                   | node-addon-api, N-API                |
| FFI без компиляции    | ctypes, cffi (ABI)                 | node-ffi (сторонний)                 |
| Сборка                | setuptools                         | node-gyp, cmake-js                   |
| Асинхронность         | ❌ в C-расширениях                 | ✅ Нативные async worker'ы          |

#### Go cgo

| Аспект                | Python                             | Go                                   |
|-----------------------|------------------------------------|--------------------------------------|
| Вызов C               | ctypes, cffi                       | `import "C"` (cgo)                   |
| Вызов Go извне        | ❌ Без биндингов                   | c-shared build mode                  |
| Сложность             | Низкая                             | Низкая                               |
| Производительность    | Высокая (Cython) / средняя         | Высокая (рядом) + низкий оверхед     |

---

### 9. Реальные примеры из экосистемы

| Проект         | Технология   | Для чего используется                       |
|----------------|--------------|---------------------------------------------|
| **NumPy**      | C + Cython   | Числовые операции, работа с массивами       |
| **cryptography** | C + cffi   | Криптографические примитивы (AES, RSA, SHA) |
| **orjson**     | Rust + PyO3  | Быстрый JSON-парсер (не C, но схожий подход)|
| **lxml**       | Cython       | XML/HTML парсинг                            |
| **Pillow**     | C            | Обработка изображений                       |
| **PyTorch**    | C++ + pybind11| Тензорные операции, автодифференцирование  |
| **pydantic-core** | Rust + PyO3 | Валидация данных (pydantic v2)             |

---

### 10. Практический чек-лист: выбор инструмента

```text
1. Нужно вызвать системную C-библиотеку (libc, libm)?
   → ctypes (уже есть в stdlib)

2. Нужен чистый синтаксис, поддержка PyPy?
   → cffi (ABI-режим)

3. Нужно написать C-логику внутри Python-проекта?
   → cffi (API-режим) или Cython

4. Нужна максимальная производительность для числовых алгоритмов?
   → Cython с typed memoryviews

5. Есть существующая C++ библиотека, которую нужно обернуть?
   → pybind11 или nanobind

6. Сложная C++ иерархия классов, ООП?
   → pybind11

7. Новый проект, важен минимальный размер?
   → nanobind
```

---

## Практическое задание

### Задача: ускорение вычисления чисел Фибоначчи и работы с матрицами

#### Часть 1: Фибоначчи через разные интерфейсы

Реализуйте вычисление `fibonacci(n)` для `n = 100 000` пятью способами и сравните производительность:

1. **Чистый Python** (итеративный)
2. **ctypes** — вызов C-функции из скомпилированной `.so`/`.dll`
3. **cffi** — ABI-режим и API-режим
4. **Cython** — с аннотациями типов
5. **pybind11** — C++ версия

Для каждого способа:
- Измерьте время выполнения (100 итераций)
- Сравните с Python baseline
- Заполните таблицу результатов

```python
# Шаблон для бенчмарков
import timeit
import json

results = {}

def bench(name: str, stmt: str, setup: str = "", number: int = 100) -> None:
    total = timeit.timeit(stmt, setup=setup, number=number)
    results[name] = {
        "total_time": total,
        "per_iter": total / number,
    }
    print(f"{name:30s}: {total:.4f}s ({total/number*1000:.2f}ms/iter)")

# ... Ваши реализации ...
```

#### Часть 2: Умножение матриц

Реализуйте умножение двух матриц 500×500:

1. **Чистый Python** (тройной цикл)
2. **NumPy** (`np.dot()` или `@`)
3. **Cython** с typed memoryviews
4. **C++ через pybind11**

```python
import numpy as np

def py_matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Python-версия: тройной цикл."""
    n = len(a)
    result = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += a[i][k] * b[k][j]
            result[i][j] = s
    return result

# Генерация тестовых данных
n = 500
a = np.random.randn(n, n)
b = np.random.randn(n, n)

# Python
py_result = py_matrix_multiply(a.tolist(), b.tolist())

# NumPy
np_result = a @ b
```

### Шаги выполнения

1. **Скомпилируйте C-библиотеку** для ctypes:
   ```bash
   gcc -shared -o libfib.so -fPIC -O2 fibonacci.c
   ```

2. **Создайте Cython-модуль** и соберите:
   ```bash
   python setup.py build_ext --inplace
   ```

3. **Создайте pybind11-модуль** и соберите.

4. **Запустите бенчмарки** и заполните таблицу:

5. **Проанализируйте оверхед маршалинга**:
   - Для ctypes измерьте время конвертации Python-списка в C-массив
   - Для pybind11 измерьте время конвертации `std::vector`

### Ожидаемые результаты

| Метод              | fibonacci(100k) | Матрицы 500×500 | Прирост vs Python |
|--------------------|-----------------|-----------------|-------------------|
| Python             | ... ms          | ... ms          | 1.0x              |
| ctypes             | ... ms          | N/A             | ...x              |
| cffi (ABI)         | ... ms          | N/A             | ...x              |
| Cython             | ... ms          | ... ms          | ...x              |
| pybind11           | ... ms          | ... ms          | ...x              |
| NumPy              | N/A             | ... ms          | ...x              |

---

## Дополнительные материалы

### Книги

- **Cython: A Guide for Python Programmers**, Kurt W. Smith
- **Learning Cython Programming**, Philip Herron
- **Python/C API Reference Manual** — официальная документация

### Инструменты

- [Cython](https://cython.org/) — официальный сайт с документацией
- [pybind11](https://pybind11.readthedocs.io/) — документация
- [nanobind](https://github.com/wjakob/nanobind) — GitHub репозиторий
- [cffi](https://cffi.readthedocs.io/) — документация
- [scikit-build-core](https://github.com/scikit-build/scikit-build-core) — современная система сборки C++ расширений

### Онлайн-ресурсы

- [Cython tutorial](https://cython.readthedocs.io/en/latest/src/tutorial/cython_tutorial.html)
- [pybind11: First Steps](https://pybind11.readthedocs.io/en/stable/basics.html)
- [Python C API: Extending Python with C or C++](https://docs.python.org/3/extending/extending.html)
- [cffi overview](https://cffi.readthedocs.io/en/latest/overview.html)
- [Build systems for C++ extensions](https://pypackaging-native.github.io/) — гайд по pypackaging-native

### Сравнительная таблица: C/C++ интеграция в разных языках

| Язык        | Инструменты                                  | Сложность | Производительность |
|-------------|----------------------------------------------|-----------|-------------------|
| **Python**  | ctypes, cffi, Cython, pybind11, nanobind     | ⭐–⭐⭐⭐⭐  | ⭐⭐–⭐⭐⭐⭐⭐       |
| **Java**    | JNI, JNA, Project Panama, GraalVM Native     | ⭐⭐⭐–⭐⭐⭐⭐⭐ | ⭐⭐⭐–⭐⭐⭐⭐⭐     |
| **Node.js** | node-addon-api, N-API, ffi-napi, wasm        | ⭐⭐–⭐⭐⭐⭐  | ⭐⭐⭐–⭐⭐⭐⭐⭐     |
| **Go**      | cgo, c-shared build mode                     | ⭐⭐        | ⭐⭐⭐⭐            |
| **Rust**    | PyO3, cbindgen, extern "C"                   | ⭐⭐⭐–⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐          |
| **Ruby**    | ffi, Ruby-FFI, Rice                          | ⭐⭐–⭐⭐⭐   | ⭐⭐–⭐⭐⭐⭐        |