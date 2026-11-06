
from typing import TYPE_CHECKING

from incienso_shop.apps.suppliers.models import PurchaseOrder
from incienso_shop.apps.suppliers.models import Supplier

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_all_suppliers() -> QuerySet[Supplier]:
    """Retorna todos los proveedores activos ordenados por nombre."""
    return Supplier.objects.filter(is_active=True).order_by("name")


def get_supplier_by_id(supplier_id: int) -> Supplier | None:
    """Busca un proveedor por su ID con sus órdenes de compra asociadas."""
    return Supplier.objects.filter(id=supplier_id).prefetch_related("purchase_orders").first()


def get_all_purchase_orders() -> QuerySet[PurchaseOrder]:
    """Retorna todas las órdenes de compra con datos de proveedor y productos."""
    return (
        PurchaseOrder.objects.select_related("supplier")
        .prefetch_related("items__product")
        .order_by("-order_date", "-id")
    )


def get_purchase_order_by_number(po_number: str) -> PurchaseOrder | None:
    """Obtiene una orden de compra por su número identificador."""
    return (
        PurchaseOrder.objects.filter(po_number=po_number)
        .select_related("supplier")
        .prefetch_related("items__product")
        .first()
    )
