from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.db.models import Sum

from incienso_shop.apps.crm.models import LoyaltyAccount
from incienso_shop.apps.inventory.selectors import get_inventory_valuation
from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.models import OrderItem
from incienso_shop.apps.shipping.choices import ShipmentStatusChoices
from incienso_shop.apps.shipping.models import Shipment

User = get_user_model()


def get_business_intelligence_kpis() -> dict[str, Any]:
    """Calcula las métricas ejecutivas consolidadas del e-commerce."""
    total_sales = Order.objects.filter(
        status__in=[OrderStatusChoices.PAID, OrderStatusChoices.SHIPPED, OrderStatusChoices.DELIVERED],
    ).aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    total_orders = Order.objects.count()
    completed_orders = Order.objects.filter(status=OrderStatusChoices.DELIVERED).count()
    avg_order_value = Order.objects.filter(total_amount__gt=0).aggregate(aov=Avg("total_amount"))["aov"] or Decimal(
        "0.00",
    )

    # Inventario FIFO
    inv = get_inventory_valuation()

    # Clientes y Fidelización
    total_customers = User.objects.filter(is_active=True).count()
    total_loyalty_points = LoyaltyAccount.objects.aggregate(total_pts=Sum("points_balance"))["total_pts"] or 0

    # Logística
    total_shipments = Shipment.objects.count()
    delivered_shipments = Shipment.objects.filter(status=ShipmentStatusChoices.DELIVERED).count()
    delivery_rate_pct = int(delivered_shipments / total_shipments * 100) if total_shipments > 0 else 100

    return {
        "total_revenue": total_sales,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "average_order_value": avg_order_value,
        "inventory_valuation": inv["total_valuation"],
        "inventory_units": inv["total_units"],
        "total_customers": total_customers,
        "total_loyalty_points": total_loyalty_points,
        "delivery_rate_pct": delivery_rate_pct,
    }


def get_top_selling_products(limit: int = 5) -> list[dict[str, Any]]:
    """Obtiene los productos con mayor cantidad de unidades vendidas."""
    items = (
        OrderItem.objects.values("product__name", "product__sku")
        .annotate(units_sold=Sum("quantity"), revenue=Sum("line_total"))
        .order_by("-units_sold")[:limit]
    )
    return list(items)
