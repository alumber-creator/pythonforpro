# Python for Professionals — Интерактивный сайт курсов по Python

Полноценный веб-сайт с курсами по Python для опытных программистов, которые уже владеют хотя бы одним языком программирования (Java, C++, JavaScript, C#, Go и т.п.).

## ✨ Особенности

- **7 курсов, 39+ уроков** — от быстрого старта до метаклассов и C-расширений
- **Для опытных** — не учим основам программирования, показываем уникальные возможности Python
- **Сравнение языков** — каждый урок показывает решения в Python, Java, C++, JavaScript
- **Идиоматичный код** — все примеры соответствуют PEP 8 и Zen of Python
- **Тёмная/светлая тема** — автоопределение системных предпочтений
- **Подсветка синтаксиса** — Pygments для всех языков
- **Копирование кода** — в один клик
- **Адаптивный дизайн** — мобильные устройства, планшеты, десктоп
- **Markdown + YAML front matter** — легко добавлять новые уроки

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- pip

### Установка и запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/alumber-creator/pythonforpro.git python-course
cd python-course

# 2. Создайте виртуальное окружение
python -m venv .venv

# 3. Активируйте окружение
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Запустите сервер
python app.py
```

Сайт будет доступен по адресу **http://localhost:5000**.

## 📚 Структура курсов

| Курс | Уроков | Уровень |
|------|--------|---------|
| 🚀 Python для профессионалов: Быстрый старт | 5 | Начальный |
| 🐍 Идиоматический Python | 8 | Средний |
| 🔬 Продвинутые возможности Python | 6 | Продвинутый |
| ⚡ Асинхронный Python | 5 | Продвинутый |
| 🛠️ Инструменты и экосистема | 6 | Средний |
| ✅ Качество кода и тестирование | 5 | Средний |
| 🏎️ Производительность и оптимизация | 4 | Продвинутый |

## 📁 Структура проекта

```
course/
├── app.py                  # Flask-приложение
├── requirements.txt        # Зависимости Python
├── README.md               # Этот файл
├── lessons/                # Уроки (Markdown + YAML front matter)
│   ├── python-fast-track/  #   Курс 1
│   ├── idiomatic-python/   #   Курс 2
│   ├── advanced-python/    #   Курс 3
│   ├── async-python/       #   Курс 4
│   ├── tools-ecosystem/    #   Курс 5
│   ├── testing-quality/    #   Курс 6
│   └── performance/        #   Курс 7
├── blog/                   # Посты блога
├── templates/              # Jinja2-шаблоны
│   ├── base.html
│   ├── index.html
│   ├── course.html
│   ├── lesson.html
│   ├── blog.html
│   ├── blog_post.html
│   ├── faq.html
│   ├── best_practices.html
│   └── format_doc.html
└── static/                 # Статические файлы
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 📝 Формат уроков

Каждый урок — это Markdown-файл с YAML front matter. Подробнее в [документации по формату](http://localhost:5000/format) или в файле [FORMAT.md](FORMAT.md).

### Пример

```markdown
---
title: "Идиоматический Python: Comprehensions"
order: 2
tags: ["comprehensions", "list", "dict", "set"]
prerequisites: "Базовый синтаксис Python, циклы, функции"
objective: "Научиться заменять циклы на comprehensions для читаемого и быстрого кода"
---

## Введение

...

## Основная часть

...

## Практическое задание

...
```

## 🛠️ Технологии

- **Backend:** Flask 3.x
- **Контент:** Markdown + python-frontmatter + Pygments
- **Шаблоны:** Jinja2
- **Стили:** CSS custom properties (тёмная/светлая тема)
- **Шрифты:** Inter (текст) + JetBrains Mono (код)

## 📄 Лицензия

MIT
