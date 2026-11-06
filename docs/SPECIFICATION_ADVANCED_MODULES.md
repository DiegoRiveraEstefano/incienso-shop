# Especificación Técnica de Requerimientos Avanzados: Incienso Shop

**Fecha:** Noviembre 2026  
**Proyecto:** Incienso Shop (Django 6.0, Python 3.14, SQLite WAL, Unpoly 3, Bootstrap 5)  
**Documento:** Evaluación de Requerimientos, Casos de Uso, Casos de Uso Extra y Especificación de Arquitectura

---

## 1. Evaluación Detallada de Requerimientos y Casos de Uso

### Requerimiento 1 & 2: Sistema de Inventario por Lotes (Batches) con Salida FIFO
- **Evaluación**: Los productos de inciensos y resinas aromáticas tienen fechas de producción, cosechas y caducidad de esencias naturales. Un stock numérico plano no permite conocer el coste de adquisición ni priorizar el material más antiguo. Se requiere modelar lotes (`ProductBatch`) con coste unitario, fecha de ingreso, caducidad opcional y cantidad disponible. La asignación a pedidos debe consumir lotes mediante FIFO (First-In, First-Out: ordenar por fecha de recepción/creación ascendente).
- **Casos de Uso Principales**:
  - **UC-INV-01 (Crear Lote de Producto)**: El operador registra un nuevo lote con código, fecha de fabricación/ingreso, costo unitario y cantidad inicial.
  - **UC-INV-02 (Deducción FIFO al Despachar Pedido)**: Al confirmarse/pagarse una orden, el servicio de inventario busca los lotes disponibles del producto ordenados por `received_date ASC, id ASC`, debitando las unidades requeridas secuencialmente y creando registros de movimiento.
  - **UC-INV-03 (Consultar Stock Consolidado y Trazabilidad por Lote)**: El administrador visualiza el stock total y el desglose por lotes activos.
- **Casos de Uso Extra / Relacionados**:
  - **UC-INV-04 (Ajuste Manual de Inventario / Mermas)**: Registro de pérdidas, evaporación de aceites o roturas, deduciendo de un lote específico con motivo documentado.
  - **UC-INV-05 (Alerta de Stock Crítico y Vencimiento)**: Notificaciones automáticas cuando un lote está próximo a caducar (30/60 días) o el stock consolidado cae por debajo del umbral mínimo.
  - **UC-INV-06 (Valoración de Inventario FIFO)**: Cálculo del valor total de existencias en almacén basado en el coste real de los lotes remanentes.

---

### Requerimiento: Módulo Dedicado de Proveedores y Órdenes de Compra (Suppliers)
- **Evaluación**: La gestión de proveedores y órdenes de aprovisionamiento requiere un ciclo de vida independiente del almacén físico. Los pedidos a proveedores (`PurchaseOrder`) pasan por estados de cotización, envío, recepción parcial y recepción completa.
- **Casos de Uso Principales**:
  - **UC-SUP-01 (Directorio de Proveedores)**: Ficha de proveedor con datos de contacto, país, moneda y tiempo de entrega promedio (lead time).
  - **UC-SUP-02 (Crear Orden de Compra)**: Emisión de pedido formal a proveedor con líneas de producto, costo unitario pactado y fecha esperada de entrega.
  - **UC-SUP-03 (Recepción de Orden de Compra e Ingreso de Lotes)**: Al recibir la mercancía, el inventario genera automáticamente los `ProductBatch` correspondientes con el coste de compra real, alimentando el stock FIFO.

---

### Requerimiento: Sistema de Pagos con Libro Contable de Partida Doble (Double-Entry Ledger)
- **Evaluación**: La conciliación bancaria y la integridad financiera de un e-commerce exigen que cada movimiento de dinero cumpla con la partida doble contable: cada transacción tiene al menos un Débito y un Crédito, y $\sum \text{Débitos} == \sum \text{Créditos}$.
- **Casos de Uso Principales**:
  - **UC-PAY-01 (Catálogo Contable / Chart of Accounts)**: Cuentas normalizadas (`LedgerAccount`): Activos (`1100 Pasarelas por Liquidar`), Pasivos (`2000 Cuentas por Pagar`), Ingresos (`4000 Ventas de Inciensos`), Gastos (`5100 Comisiones de Pasarela`).
  - **UC-PAY-02 (Asiento Automático de Pago)**: Al confirmarse un pago de cliente, se genera un asiento compuesto (`LedgerTransaction` y `LedgerEntry`): Débito a Pasarelas de Pago / Caja y Crédito a Ingresos por Ventas.
  - **UC-PAY-03 (Balance de Comprobación / Trial Balance)**: Generación del informe de sumas y saldos para verificar que el libro contable esté cuadrado sin discrepancias monetarias.

---

### Requerimiento 3 & 4: Motor de Descuentos Flexibles y Cupones
- **Evaluación**: Las estrategias comerciales de e-commerce exigen combinar promociones automáticas (porcentaje, monto fijo, por categoría o por volumen) con códigos promocionales alfanuméricos redimibles (cupones con límite de uso, fecha de expiración y restricciones de cliente).
- **Casos de Uso Principales**:
  - **UC-DSC-01 (Crear Regla de Descuento)**: El administrador configura una regla (porcentaje o monto fijo) aplicable a todo el carrito, a una categoría o producto, con monto mínimo de compra.
  - **UC-DSC-02 (Crear Cupón Alfanumérico)**: El administrador genera un cupón (ej: `AROMA10`, `BIENVENIDA2026`) definiendo fechas de vigencia, límite global de usos y límite por usuario.
  - **UC-DSC-03 (Aplicar Cupón en Checkout)**: El cliente ingresa un código de cupón; el sistema valida vigencia, límites y condiciones, calculando el descuento y actualizando el total de la orden en tiempo real con Unpoly.
- **Casos de Uso Extra / Relacionados**:
  - **UC-DSC-04 (Descuento Exclusivo por Nivel/Grupo de Cliente)**: Descuentos automáticos vinculados a grupos CRM (ej: Clientes Mayoristas o Socios Oro).
  - **UC-DSC-05 (Restricción de No Acumulabilidad)**: Regla para evitar la combinación indebida de múltiples cupones o productos ya rebajados.
  - **UC-DSC-06 (Generación Dinámica de Cupones por Fidelización)**: Emisión de cupones automáticos de un solo uso cuando un cliente canjea sus puntos acumulados.

---

### Requerimiento 5: CRM y Sistema de Fidelización (Loyalty Program)
- **Evaluación**: Fomentar la recurrencia premiando a los compradores con puntos por cada compra realizada, clasificándolos en niveles (Bronce, Plata, Oro, Platino) según su actividad y gasto histórico.
- **Casos de Uso Principales**:
  - **UC-CRM-01 (Acumulación Automática de Puntos)**: Al completarse el pago de un pedido, el sistema acredita puntos según la tasa configurada (ej. 1 punto por cada $10 gastados).
  - **UC-CRM-02 (Canje de Puntos por Beneficios/Descuentos)**: El cliente canjea sus puntos por saldo a favor o cupones de descuento desde su panel personal.
  - **UC-CRM-03 (Gestión de Niveles de Fidelización)**: Actualización automática del nivel de lealtad (`tier`) del cliente en base a sus puntos o gasto acumulado.

---

### Requerimiento 6: Embudos de Venta (Sales Funnels) con Tablero Canvas / Kanban
- **Evaluación**: El equipo de ventas corporativo o B2B (distribuidores, tiendas esotéricas, spas y centros de yoga) requiere gestionar tratos (`Deals`) a través de un pipeline visual interactivo tipo Trello/Jira.
- **Casos de Uso Principales**:
  - **UC-FNL-01 (Configurar Embudo y Etapas)**: El administrador crea funnels con etapas ordenadas (`Prospecto`, `En Negociación`, `Ganado`).
  - **UC-FNL-02 (Visualizar Tablero Canvas/Kanban)**: Los agentes ven las oportunidades comerciales organizadas en columnas por etapa con tarjetas interactivas.
  - **UC-FNL-03 (Mover Tratos entre Etapas)**: El usuario actualiza de etapa un trato con actualización reactiva Unpoly.

---

### Requerimiento 7 & 8: Segmentación de Clientes y Campañas de Email Masivo
- **Evaluación**: Comunicación segmentada para promocionar novedades aromáticas a toda la base o a segmentos específicos.
- **Casos de Uso Principales**:
  - **UC-EML-01 (Crear Grupos y Segmentos de Clientes)**: Clasificación de clientes en grupos dinámicos o estáticos.
  - **UC-EML-02 (Diseñar y Enviar Campaña de Email)**: Creación de un boletín seleccionando como destinatarios "Todos los clientes" o un grupo específico.
  - **UC-EML-03 (Registro y Auditoría de Envíos)**: Registro histórico de campañas enviadas y destinatarios alcanzados.

---

### Requerimiento 9 & 10: Logística de Rutas / Última Milla y Rastreo de Envíos
- **Evaluación**: Gestión de despachos físicos, asignación a transportistas o rutas locales, generación de código de seguimiento único (`tracking_number`) y portal visual de trazabilidad.
- **Casos de Uso Principales**:
  - **UC-LOG-01 (Generar Envío y Número de Tracking)**: Al procesar la orden, se genera un registro de envío (`Shipment`) con código de rastreo alfanumérico único.
  - **UC-LOG-02 (Planificación y Hoja de Ruta de Última Milla)**: El despachador crea una ruta de entrega (`DeliveryRoute`) asignando un transportista y ordenando las paradas (`RouteStop`).
  - **UC-LOG-03 (Portal de Tracking Público / Privado)**: El cliente accede a una página visual con barra de progreso de estado y línea de tiempo de eventos.

---

### Requerimiento 11 & 12: Permisos, Grupos y Portal de Clientes
- **Evaluación**: Roles preconfigurados (`Administradores`, `Gestores de Inventario & Proveedores`, `Agentes CRM & Ventas`, `Operadores Logísticos`, `Clientes`) y portal de autoservicio de órdenes con seguimiento de entrega.

---

### Requerimiento 13: Analítica & Business Intelligence (BI)
- **Evaluación**: Dashboard ejecutivo en tiempo real con facturación total, ticket promedio, valoración de inventario FIFO, rendimiento logístico y ranking de productos estrella.

---

## 2. Mapa Arquitectónico de Aplicaciones

1. **`incienso_shop/apps/suppliers`**:
   - `Supplier`: Proveedores.
   - `PurchaseOrder` & `PurchaseOrderItem`: Órdenes de compra formales.
   - Selectors y Services dedicados.

2. **`incienso_shop/apps/inventory`**:
   - `ProductBatch`: Lotes con salida FIFO vinculados al proveedor y compra.
   - `StockMovement`: Trazabilidad inmutable de entradas y salidas.

3. **`incienso_shop/apps/payments`**:
   - `Payment`: Integración de pasarelas (`django-payments`).
   - `LedgerAccount`: Catálogo de cuentas (Activo, Pasivo, Ingreso, Gasto).
   - `LedgerTransaction`: Asiento contable del libro diario.
   - `LedgerEntry`: Apuntes individuales con validación estricta de partida doble ($\sum \text{Débito} == \sum \text{Crédito}$).

4. **`incienso_shop/apps/discounts`**:
   - `DiscountRule`, `Coupon`, `CouponUsage`.

5. **`incienso_shop/apps/crm`**:
   - `LoyaltyTier`, `LoyaltyAccount`, `PointTransaction`.
   - `SalesFunnel`, `FunnelStage`, `Deal` (Canvas/Kanban).
   - `CustomerSegment`, `EmailCampaign`, `CampaignRecipient`.

6. **`incienso_shop/apps/shipping`**:
   - `Carrier`, `Shipment`, `ShipmentEvent`, `DeliveryRoute`, `RouteStop`.

7. **`incienso_shop/apps/analytics`**:
   - Selectors de BI y Dashboard ejecutivo.
