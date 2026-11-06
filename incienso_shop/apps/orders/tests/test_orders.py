from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import reverse

from incienso_shop.apps.core.models import StoreSettings
from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Cart
from incienso_shop.apps.orders.services import CartService
from incienso_shop.apps.orders.services import OrderService
from incienso_shop.apps.products.choices import AromaFamilyChoices
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product

pytestmark = pytest.mark.django_db


def test_cart_and_order_flow():
    StoreSettings.objects.get_or_create(
        id=1,
        defaults={
            "store_name": "Incienso Shop",
            "free_shipping_threshold": Decimal("50.00"),
            "standard_shipping_cost": Decimal("5.00"),
            "tax_rate_pct": Decimal("10.00"),
        },
    )
    cat = Category.objects.create(name="Resinas", slug="resinas")
    prod = Product.objects.create(
        name="Incienso Copal",
        slug="incienso-copal",
        sku="COP-100",
        category=cat,
        aroma_family=AromaFamilyChoices.RESINS,
        price=Decimal("20.00"),
        stock=10,
    )

    cart = Cart.objects.create(session_key="test-session-123")
    CartService.add_product(cart, prod, quantity=2)
    assert cart.total_items == 2
    assert cart.subtotal == Decimal("40.00")

    order = OrderService.create_order_from_cart(
        cart=cart,
        customer_data={
            "customer_name": "Comprador Demo",
            "customer_email": "demo@example.com",
            "customer_phone": "123456",
            "shipping_address": "Calle Aromas 123",
            "shipping_city": "Santiago",
        },
    )

    assert order.status == OrderStatusChoices.PENDING
    assert order.items.count() == 1
    assert cart.items.count() == 0  # Cart emptied
    prod.refresh_from_db()
    assert prod.stock == 8  # Reserved stock


def test_cart_detail_view(client):
    url = reverse("orders:cart_detail")
    resp = client.get(url)
    assert resp.status_code == HTTPStatus.OK
    assert "Carrito" in resp.rendered_content
