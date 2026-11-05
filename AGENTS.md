# Guía Operativa para Agentes de IA (AGENTS)

Este documento proporciona el contexto esencial, las restricciones de infraestructura y las reglas de arquitectura que cualquier Agente de IA o asistente de programación debe seguir al trabajar en **Incienso Shop**.

---

## 1. Contexto Fundamental del Proyecto

- **Propósito**: Plataforma de e-commerce artesanal en **Django 6.0** (Python `3.14`) para la venta de inciensos botánicos, resinas puras, maderas sagradas y accesorios de aromaterapia. Concebido a modo de proyecto demo, prueba y portafolio de alta fidelidad.
- **Frontend & Reactividad**: **Bootstrap 5** (`crispy-bootstrap5`) para los estilos visuales, **JavaScript Vanilla (ES6+)** con **Web Components nativos** (`<incienso-*>`), y **Unpoly 3** para la navegación SPA progresiva y reactividad de fragmentos sin recargar la página.
- **Pagos**: Integración con **`django-payments`** mediante el modelo `Payment` (heredado de `BasePayment`) y pasarelas configurables (variante `dummy` por defecto).
- **Reglas en `.agents/rules/`**: Precedencia absoluta sobre convenciones de desarrollo, capas y límites de código.

> [!IMPORTANT]
> ### Decisiones Arquitectónicas con Precedencia Absoluta
> 1. **NO ES MULTI-TENANT**: El sistema pertenece a una única tienda. **No agregues** modelos `Organization` / `Tenant`, ni campos `organization_id` / `tenant_id`.
> 2. **Base de Datos SQLite (WAL)**: Utiliza **SQLite 3** optimizado con `PRAGMA journal_mode=WAL;`, `synchronous=NORMAL;`, `busy_timeout=5000;`. Mantén las transacciones `@transaction.atomic` cortas y eficientes.
> 3. **Caché con DiskCache / Memoria**: Se utiliza **`diskcache`** (`diskcache.DjangoCache`) para catálogos y consultas agregadas.
> 4. **Frontend con Unpoly & Web Components**: Prioriza atributos de Unpoly (`up-follow`, `up-target`, `up-submit`) y elementos personalizados `<incienso-*>` antes que frameworks JS externos.
> 5. **Ecosistema Django**: Prioriza el uso de **`django-tables2`**, **`django-filter`**, **`django-crispy-forms`**, **`django-widget-tweaks`**, **`django-simple-history`**, **`django-auditlog`** y **`django-payments`**.

---

## 2. Mapa de Documentación del Repositorio

- [`DOCS.md`](file:///home/diego/Proyectos/incienso-shop/DOCS.md): Mapeo completo de modelos (`Product`, `Category`, `Cart`, `Order`, `Payment`, `Review`), flujos de checkout y pasarela de pago.
- [`GUIDELINES.md`](file:///home/diego/Proyectos/incienso-shop/GUIDELINES.md): Arquitectura en capas (`models.py`, `selectors.py`, `services.py`, `tables.py`, `filters.py`, `forms.py`, `views.py`), integración con Unpoly y directivas TDD.
- [`STYLE_GUIDE.md`](file:///home/diego/Proyectos/incienso-shop/STYLE_GUIDE.md): Convenciones de Python (`Ruff`, `Mypy`), plantillas HTML5 (`djLint`), Bootstrap 5 y Web Components.
- [`DESING.md`](file:///home/diego/Proyectos/incienso-shop/DESING.md): Guía UI/UX, paleta de colores aromática, badges de familias olfativas y componentes reactivos.
- [`SECURITY.md`](file:///home/diego/Proyectos/incienso-shop/SECURITY.md): Seguridad en transacciones, CSRF con Unpoly y protección de datos de pago.
- [`CONTRIBUTING.md`](file:///home/diego/Proyectos/incienso-shop/CONTRIBUTING.md): Flujo de trabajo Git, convenciones de commits y checklist de calidad.
- [`CHANGELOG.md`](file:///home/diego/Proyectos/incienso-shop/CHANGELOG.md): Registro histórico de cambios del proyecto.

---

## 3. Reglas Rápidas de Codificación para el Agente

1. **Límite de Tamaño de Archivo**: Ningún archivo Python debe superar las **400 líneas**.
2. **Separación de Responsabilidades (CQRS Ligero)**:
   - **`models.py`**: Esquema, constraints, TextChoices y auditoría.
   - **`selectors.py`**: Lecturas optimizadas (`select_related`, `prefetch_related`) y caché.
   - **`services.py`**: Mutaciones transaccionales (`@transaction.atomic`) e invalidación de caché.
   - **`views.py`**: Controladores CBV delgados que orquestan Selectors y Services.
3. **Calidad y Tests**: Antes de entregar una tarea, ejecuta `uv run pytest`, `uv run ruff check` y `uv run djlint .`.
