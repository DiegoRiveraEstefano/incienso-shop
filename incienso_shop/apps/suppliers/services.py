from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

from django.db import transaction
from django.utils import timezone

from incienso_shop.apps.suppliers.choices import PurchaseOrderStatusChoices
from incienso_shop.apps.suppliers.models import PurchaseOrder
from incienso_shop.apps.suppliers.models import PurchaseOrderItem
from incienso_shop.apps.suppliers.models import Supplier

if TYPE_CHECKING:
    from datetime import date


@transaction.atomic
def create_supplier(  # noqa: PLR0913
    *,
    name: str,
    contact_name: str = "",
    email: str = "",
    phone: str = "",
    address: str = "",
    country: str = "Chile",
    tax_id: str = "",
    lead_time_days: int = 7,
    notes: str = "",
) -> Supplier:
    """Crea un nuevo proveedor en el sistema."""
    return Supplier.objects.create(
        name=name,
        contact_name=contact_name,
        email=email,
        phone=phone,
        address=address,
        country=country,
        tax_id=tax_id,
        lead_time_days=lead_time_days,
        notes=notes,
    )


@transaction.atomic
def create_purchase_order(  # noqa: PLR0913
    *,
    po_number: str,
    supplier: Supplier,
    order_date: date | None = None,
    expected_delivery_date: date | None = None,
    notes: str = "",
    items_data: list[dict[str, Any]],
) -> PurchaseOrder:
    """Crea una nueva orden de compra formal a un proveedor."""
    po = PurchaseOrder.objects.create(
        po_number=po_number,
        supplier=supplier,
        order_date=order_date or timezone.now().date(),
        expected_delivery_date=expected_delivery_date,
        notes=notes,
        status=PurchaseOrderStatusChoices.DRAFT,
    )

    total_amount = Decimal("0.00")
    for item in items_data:
        product = item["product"]
        quantity = item["quantity"]
        unit_cost = item["unit_cost"]
        line_total = unit_cost * quantity
        total_amount += line_total

        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product,
            quantity_ordered=quantity,
            quantity_received=0,
            unit_cost=unit_cost,
            line_total=line_total,
        )

    po.total_amount = total_amount
    po.save(update_fields=["total_amount"])
    return po


@transaction.atomic
def update_purchase_order_status(
    *,
    purchase_order: PurchaseOrder,
    new_status: str,
) -> PurchaseOrder:
    """Actualiza el estado operativo de la orden de compra."""
    purchase_order.status = new_status
    purchase_order.save(update_fields=["status"])
    return purchase_order
