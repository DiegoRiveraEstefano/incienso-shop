from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import reverse

from incienso_shop.apps.products.choices import AromaFamilyChoices
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.products.services import ProductService

pytestmark = pytest.mark.django_db


def test_product_creation_and_properties():
    cat = Category.objects.create(name="Resinas", slug="resinas")
    p = Product.objects.create(
        name="Mirra Sagrada",
        slug="mirra-sagrada",
        sku="MYR-100",
        category=cat,
        aroma_family=AromaFamilyChoices.RESINS,
        price=Decimal("10.00"),
        compare_at_price=Decimal("15.00"),
        stock=10,
    )
    assert p.in_stock is True
    assert p.discount_pct == 33
    assert str(p) == "Mirra Sagrada (MYR-100)"


def test_product_stock_adjustment():
    cat = Category.objects.create(name="Maderas", slug="maderas")
    p = Product.objects.create(
        name="Palo Santo",
        slug="palo-santo",
        sku="PLS-100",
        category=cat,
        aroma_family=AromaFamilyChoices.WOODS,
        price=Decimal("12.00"),
        stock=5,
    )
    ProductService.adjust_stock(p, -2)
    assert p.stock == 3


def test_product_list_view(client):
    cat = Category.objects.create(name="Florales", slug="florales")
    Product.objects.create(
        name="Lavanda Provenza",
        slug="lavanda-provenza",
        sku="LAV-100",
        category=cat,
        aroma_family=AromaFamilyChoices.FLORAL,
        price=Decimal("8.00"),
        stock=15,
        is_active=True,
    )
    url = reverse("products:product_list")
    resp = client.get(url)
    assert resp.status_code == HTTPStatus.OK
    assert "Lavanda Provenza" in resp.rendered_content
