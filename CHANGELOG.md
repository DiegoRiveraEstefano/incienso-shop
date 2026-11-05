# Historial de Cambios (CHANGELOG)

Todos los cambios notables en este proyecto se documentarán en este archivo siguiendo [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [0.1.0] - 2026-11-05

### Agregado
- Configuración inicial de la plataforma **Incienso Shop** con Django 6.0 y Python 3.14 gestionado por `uv`.
- Configuración de SQLite en modo WAL y DiskCache para alto rendimiento.
- Capa de frontend con Bootstrap 5, Vanilla JS, Web Components nativos y navegación reactiva con Unpoly 3.
- Módulos de dominio:
  - `core`: configuración de tienda y base models.
  - `users`: modelo de usuario personalizado compatible con `allauth`.
  - `products`: catálogo, categorías, familias olfativas y control de inventario.
  - `orders`: carrito de compras y gestión de pedidos.
  - `payments`: integración completa con pasarelas mediante `django-payments`.
  - `reviews`: valoraciones y comentarios de compradores.
  - `audit`, `logs`, `monitor`, `backups`: utilidades operativas y observabilidad.
- Soporte Docker completo (`Dockerfile`, `Dockerfile.web`, `Dockerfile.celery`, `docker-compose.yml`).
