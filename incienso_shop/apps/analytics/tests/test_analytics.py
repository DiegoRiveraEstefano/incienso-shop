from decimal import Decimal

import pytest

from incienso_shop.apps.analytics.selectors import get_business_intelligence_kpis
from incienso_shop.apps.analytics.selectors import get_top_selling_products
from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.models import OrderItem
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product

pytestmark = pytest.mark.django_db


@pytest.fixture
def products():
    cat = Category.objects.create(name="Inciensos en Varilla", slug="varillas")
    p1 = Product.objects.create(name="Sándalo Mysore", sku="SAN-01", category=cat, price=Decimal("10.00"), stock=50)
    p2 = Product.objects.create(name="Palo Santo Puro", sku="PALO-01", category=cat, price=Decimal("12.00"), stock=30)
    return p1, p2


def test_business_intelligence_kpis_and_top_products(products):
    """Comprueba el cálculo correcto de KPIs de ventas y top productos vendidos."""
    p1, p2 = products

    order = Order.objects.create(
        customer_name="Comprador Analytics",
        customer_email="analytics@example.com",
        status=OrderStatusChoices.DELIVERED,
        subtotal=Decimal("80.00"),
        total_amount=Decimal("80.00"),
    )
    OrderItem.objects.create(
        order=order,
        product=p1,
        product_name=p1.name,
        unit_price=p1.price,
        quantity=5,
        line_total=Decimal("50.00"),
    )
    OrderItem.objects.create(
        order=order,
        product=p2,
        product_name=p2.name,
        unit_price=p2.price,
        quantity=2,
        line_total=Decimal("24.00"),
    )

    kpis = get_business_intelligence_kpis()
    assert kpis["total_revenue"] == Decimal("80.00")
    assert kpis["completed_orders"] == 1
    assert kpis["average_order_value"] == Decimal("80.00")

    top = get_top_selling_products(limit=5)
    assert len(top) == 2
    assert top[0]["product__name"] == "Sándalo Mysore"
    assert top[0]["units_sold"] == 5
