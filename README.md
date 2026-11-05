# Incienso Shop 🪔✨

[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma e-commerce demo, prueba y portafolio de una tienda artesanal de venta de inciensos botánicos, resinas puras y accesorios de meditación desarrollada en **Django 6.0**, **Bootstrap 5**, **JavaScript Vanilla**, **Web Components nativos**, **Unpoly 3** para navegación SPA reactiva y **django-payments** para pasarelas de pago.

---

## 🚀 Características Principales

- **Arquitectura Limpia (CQRS Ligero)**: División estricta en capas (`models`, `selectors`, `services`, `tables`, `filters`, `forms`, `views`).
- **Frontend Moderno & Reactivo**:
  - Estilos con **Bootstrap 5** y **Crispy Forms**.
  - Navegación fluida sin recargas completas de página mediante **Unpoly 3** (`up-follow`, `up-main`, `up-target`, `up-submit`).
  - Componentes web nativos personalizados (`<incienso-aroma-badge>`, `<incienso-stock-counter>`, `<incienso-cart-badge>`).
- **Pasarela de Pagos**: Integración con **`django-payments`** mediante modelo propio `Payment`.
- **Rendimiento**: Base de datos SQLite en modo WAL y caché granular con **DiskCache**.
- **Observabilidad**: Registro de cambios con `simple_history` y auditoría de eventos con `auditlog`.
- **Docker Ready**: Entorno completo con `docker-compose`, Gunicorn ASGI (Uvicorn Worker), Redis y Celery.

---

## 🛠️ Instalación y Desarrollo Local

El proyecto está gestionado con **[uv](https://docs.astral.sh/uv/)**:

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd incienso-shop

# 2. Sincronizar dependencias
uv sync

# 3. Aplicar migraciones iniciales
uv run python manage.py migrate

# 4. Iniciar servidor de desarrollo
uv run python manage.py runserver
```

Abre tu navegador en `http://127.0.0.1:8000/`.

---

## 🧪 Pruebas y Calidad de Código

```bash
# Ejecutar suite de pruebas
uv run pytest

# Verificar linter Ruff
uv run ruff check

# Verificar formato de plantillas
uv run djlint .
```

---

## 📦 Despliegue con Docker

```bash
# Construir y levantar contenedores
docker compose up --build -d
```
