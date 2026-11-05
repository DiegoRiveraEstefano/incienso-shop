# Guía de Estilo y Convenciones de Código (STYLE_GUIDE)

Este documento define los estándares de código, formato y convenciones estéticas para **Incienso Shop**.

---

## 1. Convenciones Python (Ruff, Mypy)

- **Versión de Python**: Python 3.14.
- **Linter & Formatter**: `Ruff` con configuración estricta en `pyproject.toml`.
  - Longitud de línea: 119 caracteres.
  - Ordenamiento de imports con `isort.force-single-line = true`.
  - Verificación estricta con `uv run ruff check --fix` y `uv run ruff format`.
- **Tipado Estático**: `Mypy` activado con comprobación de tipos (`check_untyped_defs = true`).

---

## 2. Convenciones de Plantillas y HTML5 (djLint)

- **Formateador**: `djLint` con perfil `django` e indentación de 2 espacios.
- **HTML5 Semántico**:
  - Utilizar `<main>`, `<header>`, `<nav>`, `<section>`, `<article>`, `<aside>`, `<figure>`.
  - Asegurar atributos de accesibilidad (`aria-label`, `aria-labelledby`, `role`).

---

## 3. Convenciones Frontend: Bootstrap 5, Web Components & Unpoly

- **Bootstrap 5**:
  - Clases utilitarias nativas (`d-flex`, `gap-*`, `rounded-4`, `shadow-sm`).
  - Botones principales de acento: `.btn-warning` con tono ámbar cálido.
- **Web Components**:
  - Nombres con prefijo obligatorio: `incienso-<nombre>` (ejemplo: `<incienso-aroma-badge>`).
  - Encapsulación limpia en `connectedCallback()`.
- **Unpoly 3**:
  - Atributos `up-follow`, `up-main`, `up-target`, `up-submit`.
