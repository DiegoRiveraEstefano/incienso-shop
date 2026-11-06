from datetime import date
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from incienso_shop.apps.inventory.choices import MovementTypeChoices
from incienso_shop.apps.inventory.exceptions import InsufficientStockError
from incienso_shop.apps.inventory.models import ProductBatch
from incienso_shop.apps.inventory.models import StockMovement
from incienso_shop.apps.inventory.selectors import get_inventory_valuation
from incienso_shop.apps.inventory.selectors import get_product_available_stock_fifo
from incienso_shop.apps.inventory.services import deduct_order_stock_fifo
from incienso_shop.apps.inventory.services import receive_purchase_order
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.models import OrderItem
from incienso_shop.apps.products.models import Category
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.suppliers.choices import PurchaseOrderStatusChoices
from incienso_shop.apps.suppliers.services import create_purchase_order
from incienso_shop.apps.suppliers.services import create_supplier

pytestmark = pytest.mark.django_db


@pytest.fixture
def product():
    category = Category.objects.create(name="Resinas Naturales", slug="resinas-naturales")
    return Product.objects.create(
        name="Mirra Sagrada de Omán",
        slug="mirra-sagrada-oman",
        sku="MIRRA-OM-001",
        category=category,
        price=Decimal("15.00"),
        stock=0,
    )


@pytest.fixture
def supplier():
    return create_supplier(
        name="Importaciones de Oriente S.A.",
        contact_name="Ahmed Al-Hassan",
        email="ahmed@orientalresins.example",
        phone="+968 9123 4567",
        country="Omán",
    )


def test_purchase_order_and_batch_creation_fifo(product, supplier):
    """Comprueba la creación de orden de compra y la recepción generando lotes."""
    po = create_purchase_order(
        po_number="PO-2026-001",
        supplier=supplier,
        items_data=[
            {
                "product": product,
                "quantity": 50,
                "unit_cost": Decimal("7.50"),
            },
        ],
    )
    assert po.status == PurchaseOrderStatusChoices.DRAFT
    assert po.total_amount == Decimal("375.00")

    item = po.items.first()
    batches = receive_purchase_order(
        purchase_order=po,
        receipts_data=[
            {
                "purchase_order_item": item,
                "quantity_received": 50,
                "batch_code": "BATCH-OMAN-001",
                "unit_cost": Decimal("7.50"),
                "expiry_date": date(2028, 12, 31),
            },
        ],
    )

    assert len(batches) == 1
    batch = batches[0]
    assert batch.available_quantity == 50
    assert batch.initial_quantity == 50

    po.refresh_from_db()
    assert po.status == PurchaseOrderStatusChoices.RECEIVED

    product.refresh_from_db()
    assert product.stock == 50

    # Movimiento registrado
    mov = StockMovement.objects.filter(batch=batch).first()
    assert mov is not None
    assert mov.movement_type == MovementTypeChoices.PURCHASE_RECEIPT
    assert mov.quantity == 50


def test_fifo_deduction_order_consumption(product, supplier):
    """Verifica que la salida de stock consume secuencialmente los lotes más antiguos (FIFO)."""
    # Lote 1: Recibido hace 10 días, 10 unidades
    batch_old = ProductBatch.objects.create(
        batch_code="LOT-OLD-01",
        product=product,
        supplier=supplier,
        initial_quantity=10,
        available_quantity=10,
        unit_cost=Decimal("6.00"),
        received_date=timezone.now().date() - timedelta(days=10),
        is_active=True,
    )
    # Lote 2: Recibido hoy, 20 unidades
    batch_new = ProductBatch.objects.create(
        batch_code="LOT-NEW-02",
        product=product,
        supplier=supplier,
        initial_quantity=20,
        available_quantity=20,
        unit_cost=Decimal("8.00"),
        received_date=timezone.now().date(),
        is_active=True,
    )
    product.stock = get_product_available_stock_fifo(product.id)
    product.save()
    assert product.stock == 30

    # Crear una orden de compra de cliente por 15 unidades
    order = Order.objects.create(
        customer_name="Cliente Aromas",
        customer_email="cliente@example.com",
        customer_phone="+56911112222",
        shipping_address="Calle Sagrada 123",
        shipping_city="Santiago",
        total_amount=Decimal("225.00"),
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        unit_price=product.price,
        quantity=15,
        line_total=Decimal("225.00"),
    )

    movements = deduct_order_stock_fifo(order)
    assert len(movements) == 2

    # Lote antiguo consumido al 100% (10 unidades)
    batch_old.refresh_from_db()
    assert batch_old.available_quantity == 0
    assert not batch_old.is_active

    # Lote nuevo consumido parcialmente (5 unidades tomadas, quedan 15)
    batch_new.refresh_from_db()
    assert batch_new.available_quantity == 15
    assert batch_new.is_active

    # Stock total del producto actualizado a 15
    product.refresh_from_db()
    assert product.stock == 15


def test_insufficient_stock_error(product, supplier):
    """Verifica que se lanza excepción si la demanda excede el stock en lotes."""
    ProductBatch.objects.create(
        batch_code="LOT-LIMITED-01",
        product=product,
        supplier=supplier,
        initial_quantity=5,
        available_quantity=5,
        unit_cost=Decimal("5.00"),
        received_date=timezone.now().date(),
        is_active=True,
    )
    order = Order.objects.create(
        customer_name="Cliente Exigente",
        customer_email="exigente@example.com",
        shipping_address="Av. Siempre Viva 742",
        shipping_city="Santiago",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        unit_price=product.price,
        quantity=20,  # Requiere 20 pero solo hay 5
        line_total=Decimal("300.00"),
    )

    with pytest.raises(InsufficientStockError):
        deduct_order_stock_fifo(order)


def test_inventory_valuation(product, supplier):
    """Comprueba el cálculo de valoración FIFO total de existencias."""
    ProductBatch.objects.create(
        batch_code="VAL-01",
        product=product,
        supplier=supplier,
        initial_quantity=10,
        available_quantity=10,
        unit_cost=Decimal("5.00"),
        received_date=timezone.now().date(),
        is_active=True,
    )
    ProductBatch.objects.create(
        batch_code="VAL-02",
        product=product,
        supplier=supplier,
        initial_quantity=10,
        available_quantity=5,
        unit_cost=Decimal("10.00"),
        received_date=timezone.now().date(),
        is_active=True,
    )
    valuation = get_inventory_valuation()
    # 10*5 + 5*10 = 50 + 50 = 100
    assert valuation["total_valuation"] == Decimal("100.00")
    assert valuation["total_units"] == 15
