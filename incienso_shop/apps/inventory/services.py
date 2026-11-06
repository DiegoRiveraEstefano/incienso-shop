from typing import TYPE_CHECKING
from typing import Any

from django.db import transaction
from django.utils import timezone

from incienso_shop.apps.inventory.choices import MovementTypeChoices
from incienso_shop.apps.inventory.exceptions import InsufficientStockError
from incienso_shop.apps.inventory.exceptions import InvalidBatchOperationError
from incienso_shop.apps.inventory.models import ProductBatch
from incienso_shop.apps.inventory.models import StockMovement
from incienso_shop.apps.inventory.selectors import get_active_batches_fifo
from incienso_shop.apps.inventory.selectors import get_product_available_stock_fifo
from incienso_shop.apps.suppliers.choices import PurchaseOrderStatusChoices

if TYPE_CHECKING:
    from incienso_shop.apps.orders.models import Order
    from incienso_shop.apps.suppliers.models import PurchaseOrder
    from incienso_shop.apps.suppliers.models import PurchaseOrderItem


@transaction.atomic
def receive_purchase_order(
    *,
    purchase_order: PurchaseOrder,
    receipts_data: list[dict[str, Any]],
) -> list[ProductBatch]:
    """
    Registra la recepción de una orden de compra, generando lotes (ProductBatch)
    con su coste de adquisición real e incrementando el stock FIFO.
    """
    created_batches: list[ProductBatch] = []

    for receipt in receipts_data:
        po_item: PurchaseOrderItem = receipt["purchase_order_item"]
        qty_received: int = receipt["quantity_received"]
        batch_code: str = receipt.get(
            "batch_code",
            f"BATCH-{purchase_order.po_number}-{po_item.product.sku}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        )
        expiry_date = receipt.get("expiry_date")
        unit_cost = receipt.get("unit_cost", po_item.unit_cost)

        if qty_received <= 0:
            continue

        batch = ProductBatch.objects.create(
            batch_code=batch_code,
            product=po_item.product,
            supplier=purchase_order.supplier,
            purchase_order_item=po_item,
            initial_quantity=qty_received,
            available_quantity=qty_received,
            unit_cost=unit_cost,
            received_date=timezone.now().date(),
            expiry_date=expiry_date,
            is_active=True,
        )
        created_batches.append(batch)

        # Movimiento de stock
        StockMovement.objects.create(
            batch=batch,
            product=po_item.product,
            movement_type=MovementTypeChoices.PURCHASE_RECEIPT,
            quantity=qty_received,
            unit_cost=unit_cost,
            reference_order_number=purchase_order.po_number,
            notes=f"Recepción PO {purchase_order.po_number}",
        )

        po_item.quantity_received += qty_received
        po_item.save(update_fields=["quantity_received"])

        # Sincronizar stock plano en el producto
        new_stock = get_product_available_stock_fifo(po_item.product_id)
        po_item.product.stock = new_stock
        po_item.product.save(update_fields=["stock"])

    # Actualizar estado de la orden de compra
    all_items = purchase_order.items.all()
    all_received = all(item.quantity_received >= item.quantity_ordered for item in all_items)
    any_received = any(item.quantity_received > 0 for item in all_items)

    if all_received:
        purchase_order.status = PurchaseOrderStatusChoices.RECEIVED
    elif any_received:
        purchase_order.status = PurchaseOrderStatusChoices.PARTIALLY_RECEIVED
    purchase_order.save(update_fields=["status"])

    return created_batches


@transaction.atomic
def deduct_order_stock_fifo(order: Order) -> list[StockMovement]:
    """
    Deduce el stock de una orden vendida utilizando el algoritmo FIFO estricto
    (First-In, First-Out: se consumen primero los lotes más antiguos).
    """
    movements: list[StockMovement] = []

    for item in order.items.select_related("product").all():
        product = item.product
        needed = item.quantity
        available_batches = list(get_active_batches_fifo(product.id))
        total_available = sum(b.available_quantity for b in available_batches)

        if total_available < needed:
            msg = f"Stock insuficiente para {product.name}. Solicitado: {needed}, Disponible: {total_available}"
            raise InsufficientStockError(
                msg,
            )

        for batch in available_batches:
            if needed == 0:
                break

            take = min(batch.available_quantity, needed)
            batch.available_quantity -= take
            if batch.available_quantity == 0:
                batch.is_active = False
            batch.save(update_fields=["available_quantity", "is_active"])

            mov = StockMovement.objects.create(
                batch=batch,
                product=product,
                movement_type=MovementTypeChoices.FIFO_SALE,
                quantity=-take,
                unit_cost=batch.unit_cost,
                reference_order_number=str(order.order_number),
                notes=f"Salida FIFO por Pedido #{str(order.order_number)[:8]}",
            )
            movements.append(mov)
            needed -= take

        # Sincronizar el stock en el producto
        product.stock = get_product_available_stock_fifo(product.id)
        product.save(update_fields=["stock"])

    return movements


@transaction.atomic
def adjust_batch_stock(
    *,
    batch: ProductBatch,
    new_quantity: int,
    reason: str,
    movement_type: str = MovementTypeChoices.MANUAL_ADJUSTMENT,
) -> StockMovement:
    """Ajusta manualmente las existencias de un lote por conteo o merma."""
    if new_quantity < 0:
        msg = "La cantidad no puede ser negativa."
        raise InvalidBatchOperationError(msg)

    diff = new_quantity - batch.available_quantity
    batch.available_quantity = new_quantity
    batch.is_active = new_quantity > 0
    batch.save(update_fields=["available_quantity", "is_active"])

    mov = StockMovement.objects.create(
        batch=batch,
        product=batch.product,
        movement_type=movement_type,
        quantity=diff,
        unit_cost=batch.unit_cost,
        notes=reason,
    )

    batch.product.stock = get_product_available_stock_fifo(batch.product_id)
    batch.product.save(update_fields=["stock"])

    return mov
