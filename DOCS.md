# Documentación Técnica del Sistema (DOCS)

## 1. Mapeo de Entidades y Modelos

### Core & Configuración (`incienso_shop/apps/core/`)
- `StoreSettings`: Singleton que define nombre de tienda, moneda base, mínimo para envío gratis, costo estándar de envío, IVA y modo mantenimiento.

### Catálogo de Productos (`incienso_shop/apps/products/`)
- `Category`: Categorías de inciensos (Resinas, Maderas sagradas, Conos, Sahumerios).
- `Product`: Entidad central con SKU, precio, precio comparativo, stock, familia olfativa (`AromaFamilyChoices`), tiempo de quemado y país de origen.
- `ProductImage`: Galería de fotos con soporte para imagen principal.

### Carrito y Pedidos (`incienso_shop/apps/orders/`)
- `Cart`: Carrito persistente asociado al usuario autenticado o a la sesión anónima.
- `CartItem`: Línea de producto y cantidad.
- `Order`: Pedido formal con dirección de entrega, desglose de subtotal, costos de envío e impuestos.
- `OrderItem`: Snapshot inmutable del producto y precio al momento de la compra.

### Pagos (`incienso_shop/apps/payments/`)
- `Payment`: Hereda de `payments.models.BasePayment` para integración nativa con `django-payments`.
- Pasarelas configurables mediante `PAYMENT_VARIANTS` (por defecto `dummy` para entornos de prueba).

### Valoraciones (`incienso_shop/apps/reviews/`)
- `Review`: Reseña con puntuación de 1 a 5 estrellas vinculada al producto y usuario.

---

## 2. Flujo Completo de Compra

1. **Exploración**: El usuario explora el catálogo filtrando por familia olfativa con Unpoly (`up-autosubmit`).
2. **Adición al Carrito**: `POST /orders/cart/add/<id>/` agrega el producto y actualiza el badge superior sin recargar la página.
3. **Revisión del Carrito**: En `/orders/cart/` se valida el subtotal y se calcula el costo de despacho.
4. **Checkout**: En `/orders/checkout/` se completan los datos de envío y se crea el `Order`.
5. **Procesamiento de Pago**: El usuario es redirigido a `/checkout-payments/pay/<order_number>/` donde `django-payments` procesa la transacción.
6. **Confirmación**: La pasarela redirige a `/checkout-payments/success/<order_number>/` y la orden pasa a estado `PAID`.
