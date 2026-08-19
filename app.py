"""
Python for Professionals — Course Website
Flask application that serves Markdown-based lessons with YAML front matter.
"""
import re
import os
import html
from pathlib import Path
from datetime import datetime

import frontmatter
import markdown
from flask import (
    Flask, render_template, abort, request, send_from_directory,
    redirect, url_for
)
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["TITLE"] = "Python for Professionals"
app.config["SUBTITLE"] = "От Python-разработчика к Python-эксперту"
BASE_DIR = Path(__file__).resolve().parent
LESSONS_DIR = BASE_DIR / "lessons"
BLOG_DIR = BASE_DIR / "blog"

# ---------------------------------------------------------------------------
# Course metadata
# ---------------------------------------------------------------------------
COURSES = [
    {
        "slug": "python-fast-track",
        "title": "Python для профессионалов: Быстрый старт",
        "description": (
            "Интенсивный старт для опытных программистов. "
            "Синтаксис, структуры данных, функции и модули — "
            "всё, что нужно, чтобы начать писать на Python уже сегодня."
        ),
        "icon": "🚀",
        "level": "Начальный",
        "duration": "~5 часов",
    },
    {
        "slug": "idiomatic-python",
        "title": "Идиоматический Python",
        "description": (
            "Пишите код, который читается как английский текст. "
            "Comprehensions, генераторы, контекстные менеджеры, "
            "декораторы и другие идиомы Python."
        ),
        "icon": "🐍",
        "level": "Средний",
        "duration": "~8 часов",
    },
    {
        "slug": "advanced-python",
        "title": "Продвинутые возможности Python",
        "description": (
            "Глубокое погружение в декораторы, дескрипторы, метаклассы, "
            "__slots__, ABC и датаклассы. Для тех, кто хочет понимать "
            "Python на уровне интерпретатора."
        ),
        "icon": "🔬",
        "level": "Продвинутый",
        "duration": "~10 часов",
    },
    {
        "slug": "async-python",
        "title": "Асинхронный Python",
        "description": (
            "Event loop, async/await, asyncio — от основ до продвинутых "
            "паттернов. Поймите конкурентность без потоков."
        ),
        "icon": "⚡",
        "level": "Продвинутый",
        "duration": "~8 часов",
    },
    {
        "slug": "tools-ecosystem",
        "title": "Инструменты и экосистема",
        "description": (
            "Виртуальные окружения, менеджеры пакетов, линтеры, "
            "type-чекеры, документация, отладка и профилирование."
        ),
        "icon": "🛠️",
        "level": "Средний",
        "duration": "~6 часов",
    },
    {
        "slug": "testing-quality",
        "title": "Качество кода и тестирование",
        "description": (
            "pytest, фикстуры, моки, паттерны тестирования, "
            "покрытие и CI/CD. Профессиональный подход к качеству."
        ),
        "icon": "✅",
        "level": "Средний",
        "duration": "~6 часов",
    },
    {
        "slug": "performance",
        "title": "Производительность и оптимизация",
        "description": (
            "Профилирование, оптимизация, C-расширения и "
            "конкурентность. Выжмите максимум из Python."
        ),
        "icon": "🏎️",
        "level": "Продвинутый",
        "duration": "~6 часов",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert a title to a URL-friendly slug, preserving Cyrillic letters."""
    text = text.lower().strip()
    # Allow word chars (including Cyrillic), spaces, and hyphens
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)


def _load_lessons(course_slug: str) -> list[dict]:
    """Load all lessons for a course, sorted by the 'order' front-matter key."""
    course_dir = LESSONS_DIR / course_slug
    if not course_dir.is_dir():
        return []
    lessons = []
    for fpath in sorted(course_dir.glob("*.md")):
        post = frontmatter.load(fpath)
        meta = dict(post.metadata)
        slug = _slugify(meta.get("title", fpath.stem))
        # Derive a numeric order: use explicit 'order' or fall back to filename prefix
        if "order" in meta:
            order = int(meta["order"])
        else:
            m = re.match(r"^(\d+)", fpath.stem)
            order = int(m.group(1)) if m else 999
        lessons.append({
            "slug": slug,
            "title": meta.get("title", fpath.stem),
            "order": order,
            "course_slug": course_slug,
            "content_html": _render_markdown(post.content),
            "tags": meta.get("tags", []),
            "prerequisites": meta.get("prerequisites", ""),
            "objective": meta.get("objective", ""),
        })
    lessons.sort(key=lambda x: x["order"])
    return lessons


def _load_blog_posts() -> list[dict]:
    """Load all blog posts from the blog directory."""
    blog_dir = BLOG_DIR
    if not blog_dir.is_dir():
        return []
    posts = []
    for fpath in sorted(blog_dir.glob("*.md"), reverse=True):
        post = frontmatter.load(fpath)
        meta = dict(post.metadata)
        slug = _slugify(meta.get("title", fpath.stem))
        posts.append({
            "slug": slug,
            "title": meta.get("title", fpath.stem),
            "date": meta.get("date", ""),
            "author": meta.get("author", "Команда Python for Professionals"),
            "tags": meta.get("tags", []),
            "summary": meta.get("summary", ""),
            "content_html": _render_markdown(post.content),
        })
    return posts


def _render_markdown(text: str) -> str:
    """Render Markdown to HTML with Pygments syntax highlighting."""
    # Convert Markdown to HTML
    md = markdown.Markdown(extensions=["fenced_code", "codehilite", "tables", "toc"])
    html_text = md.convert(text)
    # Post-process: wrap code blocks with copy button
    html_text = _add_copy_buttons(html_text)
    return html_text


def _add_copy_buttons(html_text: str) -> str:
    """Wrap <pre> blocks with a container and add a copy button."""
    def _wrap(m: re.Match) -> str:
        code_block = m.group(0)
        return (
            '<div class="code-block-wrapper">'
            f"{code_block}"
            '<button class="copy-btn" onclick="copyCode(this)" title="Копировать">'
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>'
            '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>'
            "</svg></button></div>"
        )
    return re.sub(r"<pre><code[^>]*>.*?</code></pre>", _wrap, html_text, flags=re.DOTALL)


def _get_prev_next_lesson(course_slug: str, lesson_slug: str):
    """Return (prev_lesson, next_lesson) for navigation."""
    lessons = _load_lessons(course_slug)
    for i, lesson in enumerate(lessons):
        if lesson["slug"] == lesson_slug:
            prev_lesson = lessons[i - 1] if i > 0 else None
            next_lesson = lessons[i + 1] if i < len(lessons) - 1 else None
            return prev_lesson, next_lesson
    return None, None


def _get_course_by_slug(slug: str) -> dict | None:
    for c in COURSES:
        if c["slug"] == slug:
            return c
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main page: course listing."""
    # Calculate lesson counts
    enriched = []
    for c in COURSES:
        lessons = _load_lessons(c["slug"])
        enriched.append({**c, "lesson_count": len(lessons)})
    return render_template("index.html", courses=enriched)


@app.route("/course/<course_slug>")
def course(course_slug: str):
    """Course overview page with lesson list."""
    course_info = _get_course_by_slug(course_slug)
    if not course_info:
        abort(404)
    lessons = _load_lessons(course_slug)
    if not lessons:
        abort(404)
    return render_template("course.html", course=course_info, lessons=lessons)


@app.route("/course/<course_slug>/<lesson_slug>")
def lesson(course_slug: str, lesson_slug: str):
    """Individual lesson page."""
    course_info = _get_course_by_slug(course_slug)
    if not course_info:
        abort(404)
    lessons = _load_lessons(course_slug)
    current = None
    for l in lessons:
        if l["slug"] == lesson_slug:
            current = l
            break
    if current is None:
        abort(404)
    prev_lesson, next_lesson = _get_prev_next_lesson(course_slug, lesson_slug)
    return render_template(
        "lesson.html",
        course=course_info,
        lesson=current,
        lessons=lessons,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
    )


@app.route("/best-practices")
def best_practices():
    """Best Practices page."""
    return render_template("best_practices.html")


@app.route("/faq")
def faq():
    """FAQ page."""
    return render_template("faq.html")


@app.route("/blog")
def blog():
    """Blog listing page."""
    posts = _load_blog_posts()
    return render_template("blog.html", posts=posts)


@app.route("/blog/<post_slug>")
def blog_post(post_slug: str):
    """Individual blog post."""
    posts = _load_blog_posts()
    current = None
    for p in posts:
        if p["slug"] == post_slug:
            current = p
            break
    if current is None:
        abort(404)
    return render_template("blog_post.html", post=current)


@app.route("/format")
def format_doc():
    """Documentation on lesson file format."""
    return render_template("format_doc.html")


@app.route("/static/<path:filename>")
def static_files(filename: str):
    return send_from_directory(BASE_DIR / "static", filename)


# ---------------------------------------------------------------------------
# Template globals
# ---------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    return {
        "site_title": app.config["TITLE"],
        "site_subtitle": app.config["SUBTITLE"],
        "all_courses": COURSES,
        "current_year": datetime.now().year,
    }


@app.template_filter("slugify")
def jinja_slugify(text: str) -> str:
    return _slugify(text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)