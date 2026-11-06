from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import F
from django.db.models import Sum
from django.utils import timezone

from incienso_shop.apps.inventory.models import ProductBatch
from incienso_shop.apps.products.models import Product

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_active_batches_fifo(product_id: int) -> QuerySet[ProductBatch]:
    """Obtiene los lotes activos con existencias disponibles ordenados por FIFO."""
    return (
        ProductBatch.objects.filter(
            product_id=product_id,
            is_active=True,
            available_quantity__gt=0,
        )
        .select_related("product", "supplier")
        .order_by("received_date", "id")
    )


def get_product_available_stock_fifo(product_id: int) -> int:
    """Calcula el stock total disponible en lotes activos para un producto."""
    return (
        ProductBatch.objects.filter(
            product_id=product_id,
            is_active=True,
            available_quantity__gt=0,
        ).aggregate(total_stock=Sum("available_quantity"))["total_stock"]
        or 0
    )


def get_inventory_valuation() -> dict[str, Decimal | int]:
    """Calcula la valoración total del inventario valorado por coste de lotes remanentes."""
    batches = ProductBatch.objects.filter(is_active=True, available_quantity__gt=0)
    total_valuation = batches.aggregate(val=Sum(F("available_quantity") * F("unit_cost")))["val"] or Decimal("0.00")
    total_units = batches.aggregate(units=Sum("available_quantity"))["units"] or 0
    return {
        "total_valuation": total_valuation,
        "total_units": total_units,
        "active_batches_count": batches.count(),
    }


def get_low_stock_alerts(threshold: int = 5) -> QuerySet[Product]:
    """Retorna productos cuyo stock disponible sea menor o igual al umbral."""
    return Product.objects.filter(is_active=True, stock__lte=threshold).order_by("stock")


def get_batches_near_expiry(days: int = 60) -> QuerySet[ProductBatch]:
    """Retorna lotes con existencias que vencen dentro de los próximos N días."""
    limit_date = timezone.now().date() + timedelta(days=days)
    return (
        ProductBatch.objects.filter(
            is_active=True,
            available_quantity__gt=0,
            expiry_date__isnull=False,
            expiry_date__lte=limit_date,
        )
        .select_related("product", "supplier")
        .order_by("expiry_date")
    )
