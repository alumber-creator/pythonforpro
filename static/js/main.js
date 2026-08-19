/**
 * Python for Professionals — Main JavaScript
 * Theme toggle, mobile menu, code copy, smooth scrolling
 */
(function () {
  "use strict";

  // -----------------------------------------------------------------------
  // Theme management
  // -----------------------------------------------------------------------
  const THEME_KEY = "python-course-theme";

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (_) {
      return null;
    }
  }

  function setStoredTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_) {
      // localStorage unavailable
    }
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }

  function initTheme() {
    const stored = getStoredTheme();
    if (stored === "light" || stored === "dark") {
      applyTheme(stored);
    } else {
      // Respect system preference
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      applyTheme(prefersDark ? "dark" : "light");
    }
  }

  window.toggleTheme = function () {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    setStoredTheme(next);
  };

  // Listen for system theme changes
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!getStoredTheme()) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });

  // -----------------------------------------------------------------------
  // Mobile menu
  // -----------------------------------------------------------------------
  window.toggleMenu = function () {
    const nav = document.getElementById("navLinks");
    if (nav) {
      nav.classList.toggle("active");
    }
  };

  // Close menu on outside click
  document.addEventListener("click", function (e) {
    const nav = document.getElementById("navLinks");
    const toggle = document.querySelector(".nav-toggle");
    if (nav && nav.classList.contains("active") && toggle && !toggle.contains(e.target) && !nav.contains(e.target)) {
      nav.classList.remove("active");
    }
  });

  // -----------------------------------------------------------------------
  // Code copy
  // -----------------------------------------------------------------------
  window.copyCode = function (btn) {
    const wrapper = btn.closest(".code-block-wrapper");
    if (!wrapper) return;
    const code = wrapper.querySelector("code");
    if (!code) return;
    const text = code.textContent || "";

    navigator.clipboard.writeText(text).then(
      function () {
        btn.classList.add("copied");
        const originalTitle = btn.getAttribute("title");
        btn.setAttribute("title", "Скопировано!");
        setTimeout(function () {
          btn.classList.remove("copied");
          btn.setAttribute("title", originalTitle || "Копировать");
        }, 2000);
      },
      function () {
        // Fallback
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        try {
          document.execCommand("copy");
          btn.classList.add("copied");
          setTimeout(function () {
            btn.classList.remove("copied");
          }, 2000);
        } catch (_) {
          // Copy failed silently
        }
        document.body.removeChild(textarea);
      }
    );
  };

  // -----------------------------------------------------------------------
  // Smooth scroll for anchor links
  // -----------------------------------------------------------------------
  document.addEventListener("click", function (e) {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;
    const target = document.querySelector(link.getAttribute("href"));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  // -----------------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------------
  initTheme();
})();