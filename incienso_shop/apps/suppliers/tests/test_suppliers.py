from decimal import Decimal

import pytest

from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.suppliers.choices import PurchaseOrderStatusChoices
from incienso_shop.apps.suppliers.selectors import get_all_purchase_orders
from incienso_shop.apps.suppliers.selectors import get_all_suppliers
from incienso_shop.apps.suppliers.services import create_purchase_order
from incienso_shop.apps.suppliers.services import create_supplier
from incienso_shop.apps.suppliers.services import update_purchase_order_status

pytestmark = pytest.mark.django_db


@pytest.fixture
def product():
    cat = Category.objects.create(name="Resinas Exóticas", slug="resinas-exoticas")
    return Product.objects.create(
        name="Benjuí de Sumatra",
        slug="benjui-sumatra",
        sku="BENJUI-SUM-01",
        category=cat,
        price=Decimal("18.00"),
        stock=0,
    )


def test_supplier_creation_and_listing():
    """Comprueba la creación y listado de proveedores en su propio módulo."""
    supplier = create_supplier(
        name="Artesanos de Sumatra Ltd.",
        contact_name="Budi Santoso",
        email="budi@sumatra-resins.example",
        phone="+62 21 555 1234",
        country="Indonesia",
        lead_time_days=15,
    )

    assert supplier.id is not None
    assert supplier.name == "Artesanos de Sumatra Ltd."

    all_suppliers = get_all_suppliers()
    assert all_suppliers.count() == 1
    assert all_suppliers.first() == supplier


def test_purchase_order_lifecycle(product):
    """Verifica el ciclo de vida de la orden de compra a proveedor."""
    supplier = create_supplier(
        name="Esencias Naturales de Mysore",
        contact_name="Rajesh Patel",
        email="rajesh@mysore.example",
        country="India",
    )

    po = create_purchase_order(
        po_number="PO-INDIA-2026-001",
        supplier=supplier,
        items_data=[
            {
                "product": product,
                "quantity": 100,
                "unit_cost": Decimal("8.50"),
            },
        ],
    )

    assert po.status == PurchaseOrderStatusChoices.DRAFT
    assert po.total_amount == Decimal("850.00")
    assert po.items.count() == 1

    # Actualizar estado a SUBMITTED
    update_purchase_order_status(purchase_order=po, new_status=PurchaseOrderStatusChoices.SUBMITTED)
    po.refresh_from_db()
    assert po.status == PurchaseOrderStatusChoices.SUBMITTED

    orders_qs = get_all_purchase_orders()
    assert orders_qs.count() == 1
