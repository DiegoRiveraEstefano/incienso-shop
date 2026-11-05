---
trigger: always_on
---

# Incienso Shop: 12-Factor App & Architecture Guidelines

**Context:** Plataforma de E-commerce Artesanal Demo & Portafolio (Python 3.14+, Django 6.0, SQLite en modo WAL, DiskCache, Bootstrap 5, HTML5 Semántico, Vanilla JS, Web Components Nativos y Unpoly 3 para reactividad y navegación, integrando `django-payments`).

## Core Directives

### 1. Configuration in Environment (Factor III)
- Nunca hardcodear credenciales, secrets, host names ni puertos.
- Usar `django-environ` leyendo desde `.env`.
- Rutas de base de datos y cache configurables por variables de entorno (`SQLITE_DB_PATH`, `DISKCACHE_DIR`, `PAYMENT_HOST`).

### 2. Single-Tenant Architecture
- El sistema opera para una única tienda de inciensos artesanales.
- **Estrictamente Prohibido**: No agregar modelos `Organization` / `Tenant`, ni campos `organization_id` / `tenant_id`, ni mixins multi-tenant.

### 3. Persistencia y Despliegue: SQLite (WAL) & DiskCache
- **Base de Datos**: SQLite 3 configurado con `PRAGMA journal_mode=WAL;`, `synchronous=NORMAL;`, `busy_timeout=5000;`, y `foreign_keys=ON;`.
- Mantener las transacciones de escritura (`@transaction.atomic`) atómicas, cortas y rápidas.
- **Cache**: `diskcache.DjangoCache` para almacenar agregaciones de catálogo, productos destacados y configuración.

### 4. Frontend: SSR Semántico + Bootstrap 5 + Unpoly 3 + Web Components
- **Server-Side Rendering (SSR)**: Templates estándar de Django formateados con `djLint`.
- **Navegación & Reactividad**: **Unpoly 3** maneja la navegación SPA progresiva (`up-follow`, `up-main`, `up-target`, `up-submit`, `up-layer`), reemplazando fragmentos HTML del DOM sin recargas de página completas.
- **Componentes Nativos**: Custom Elements (`<incienso-aroma-badge>`, `<incienso-stock-counter>`, `<incienso-cart-badge>`) con JavaScript Vanilla (ES6+).
- **Formularios & Tablas**: `crispy-bootstrap5` y `django-tables2`.

### 5. Pasarela de Pagos: `django-payments`
- El modelo `Payment` hereda de `payments.models.BasePayment`.
- Implementar los métodos requeridos: `get_failure_url()`, `get_success_url()`, `get_purchased_items()`.
- Variantes de pago configuradas en `PAYMENT_VARIANTS` (por defecto `dummy` para pruebas/demo, ampliable a Stripe/MercadoPago/PayPal).
