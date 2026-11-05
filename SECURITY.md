# Política y Lineamientos de Seguridad (SECURITY)

## 1. Protección de Transacciones y Pagos

- **django-payments**:
  - Ningún dato sensible de tarjeta de crédito (PAN, CVV) se almacena en la base de datos de la tienda.
  - El modelo `Payment` únicamente retiene referencias de transacción, estado, moneda y monto verificado.
  - En producción, `PAYMENT_USES_SSL = True` y `SESSION_COOKIE_SECURE = True`.

## 2. Protección CSRF & Unpoly

- Unpoly incluye automáticamente la cabecera `X-CSRFToken` en todas las solicitudes POST/PUT/DELETE.
- La protección estándar `CsrfViewMiddleware` está activa de forma global.

## 3. Seguridad de Base de Datos SQLite

- La base de datos SQLite opera en modo WAL con `busy_timeout=5000` para prevenir condiciones de carrera.
- Las consultas SQL directas están prohibidas; todo el acceso a datos pasa por el ORM de Django con consultas parametrizadas.

## 4. Auditoría y Trazabilidad

- Todas las mutaciones en `StoreSettings`, `Product`, `Order`, `Payment` y `Review` quedan registradas en `django-auditlog` y `simple_history`.
