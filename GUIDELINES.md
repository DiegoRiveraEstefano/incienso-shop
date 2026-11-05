# Directivas de Arquitectura y Guía Técnica (GUIDELINES)

Este documento detalla las directrices de ingeniería y arquitectura aplicadas en **Incienso Shop**.

---

## 1. Arquitectura en Capas (Modular Monolith)

Cada aplicación en `incienso_shop/apps/` está estrictamente dividida en capas desacopladas:

1. **`models.py`**:
   - Heredan de `BaseModel` (con `created_at` y `updated_at`).
   - Definición de restricciones explícitas mediante `CheckConstraint` y `UniqueConstraint`.
   - Registro automático en `auditlog` y `HistoricalRecords()`.
   - Prohibido incluir lógica de negocio compleja dentro de `save()`.

2. **`selectors.py`**:
   - Métodos estáticos con tipado estricto (`Type hints`).
   - Encapsulan todas las consultas de lectura (`QuerySet`).
   - Optimizan consultas para prevenir el problema N+1 mediante `select_related` y `prefetch_related`.
   - Administran el cacheo granular con `diskcache`.

3. **`services.py`**:
   - Métodos estáticos decorados con `@transaction.atomic`.
   - Ejecutan mutaciones en la base de datos (crear órdenes, modificar stock, confirmar pagos).
   - Validan invariantes de negocio levantando `BusinessLogicError`.
   - Invalidan claves de caché afectadas tras la mutación.

4. **`forms.py` y `filters.py`**:
   - `Crispy Forms` configurado para Bootstrap 5 (`FormHelper`, `Submit`).
   - `django-filter` para el filtrado dinámico del catálogo por familia olfativa, precio y categoría.

5. **`tables.py`**:
   - `django-tables2` para listados tabulares con paginación, ordenamiento y columnas de plantilla.

6. **`views.py`**:
   - Vistas basadas en clases (`TemplateView`, `DetailView`, `FormView`, `FilterView`, `SingleTableMixin`).
   - Delegan las lecturas a `selectors.py` y las mutaciones a `services.py`.

---

## 2. Frontend Reactivo: Unpoly 3 & Web Components

- **Unpoly 3**:
  - Enlaces con `up-follow` actualizan el contenedor principal `<main id="main-content" up-main>`.
  - Formularios rápidos (como "Agregar al Carrito") usan `up-submit up-target="#header-cart-badge"` para actualizar únicamente el contador del carrito en el navbar.
  - Filtros del catálogo utilizan `up-autosubmit up-target="#product-grid"` para recargar los productos en tiempo real al cambiar un desplegable o campo de texto.
  - El token CSRF se adjunta de manera global en `project.js` a través de `up.network.config.headers["X-CSRFToken"]`.

- **Web Components**:
  - Componentes autónomos nativos (`<incienso-aroma-badge>`, `<incienso-stock-counter>`, `<incienso-cart-badge>`).
  - No requieren frameworks pesados; funcionan inmediatamente sobre el DOM inyectado por Unpoly.

---

## 3. Integración con `django-payments`

- El modelo `Payment` en `incienso_shop/apps/payments/models.py` hereda de `payments.models.BasePayment`.
- Expone los métodos requeridos:
  - `get_failure_url()`
  - `get_success_url()`
  - `get_purchased_items()`
- En el flujo de checkout, una vez generado el `Order`, se orquesta la pasarela mediante `StartPaymentView` obteniendo el formulario de pago mediante `payment.get_form()`.
- Al confirmarse el pago, `PaymentService.complete_payment()` actualiza el estado de la orden a `PAID`.
