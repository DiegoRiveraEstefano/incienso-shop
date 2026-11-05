---
trigger: always_on
---

# Incienso Shop: Templates & Frontend Guidelines

## Core Principles

1. **Server-Side Rendering (SSR) Semantic HTML5**:
   - Plantillas Django (`{% extends %}`, `{% block %}`, `{% include %}`) formateadas con `djLint` (2 espacios de indentación, perfil `django`).
   - Etiquetas semánticas estrictas (`<main id="main-content" up-main>`, `<header up-nav>`, `<nav>`, `<section>`, `<article>`, `<aside>`, `<figure>`, `<time>`).
   - Cero dependencias de SPAs pesadas (no React, Vue o Angular).
2. **Bootstrap 5 & Ecosistema Django**:
   - Renderizado de tablas con `{% load django_tables2 %}` y `{% render_table table %}`.
   - Formularios estilizados con `{% load crispy_forms_tags %}` y `{% crispy form %}` (`crispy-bootstrap5`).
   - Filtros dinámicos con `{% load widget_tweaks %}`.
3. **Navegación Reactiva con Unpoly 3**:
   - Utilizar atributos de Unpoly para interactividad sin recarga:
     - `up-follow`: navegación de enlaces ajax fluidos.
     - `up-target="#target-id"`: actualización quirúrgica de fragmentos del DOM (por ejemplo carrito o grilla de productos).
     - `up-submit`: envío asíncrono de formularios.
     - `up-layer="new"`: modales o drawers rápidos.
     - `up-autosubmit`: para barras de búsqueda y filtros reactivos.
   - Configuración de cabecera `X-CSRFToken` automática en `project.js`.
4. **JavaScript Vanilla (ES6+) & Web Components Nativos**:
   - Custom Elements registrados (`<incienso-aroma-badge>`, `<incienso-stock-counter>`, `<incienso-cart-badge>`).
   - Sin librerías JS pesadas.
5. **Accesibilidad (WCAG 2.1 AA)**:
   - Atributos `aria-label`, `aria-labelledby`, `role` en alertas y componentes interactivos.
