from decimal import Decimal

import pytest

from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.shipping.choices import RouteStatusChoices
from incienso_shop.apps.shipping.choices import ShipmentStatusChoices
from incienso_shop.apps.shipping.models import Carrier
from incienso_shop.apps.shipping.selectors import get_shipment_by_tracking
from incienso_shop.apps.shipping.services import complete_route_stop
from incienso_shop.apps.shipping.services import create_delivery_route
from incienso_shop.apps.shipping.services import create_shipment_for_order
from incienso_shop.apps.shipping.services import update_shipment_status

pytestmark = pytest.mark.django_db


@pytest.fixture
def carrier():
    return Carrier.objects.create(
        name="Repartos Sagrados Express",
        phone="+56912345678",
        vehicle_plate="ABCD-12",
    )


@pytest.fixture
def order():
    return Order.objects.create(
        customer_name="Valeria Meditación",
        customer_email="valeria@yoga.example",
        customer_phone="+56999887766",
        shipping_address="Avenida Providencia 2000",
        shipping_city="Santiago",
        total_amount=Decimal("45.00"),
    )


def test_create_shipment_and_tracking_events(order, carrier):
    """Comprueba la generación de número de rastreo y eventos de tracking."""
    shipment = create_shipment_for_order(order=order, carrier=carrier)
    assert shipment.tracking_number.startswith("TRK-")
    assert shipment.status == ShipmentStatusChoices.PREPARING
    assert shipment.events.count() == 1

    # Actualizar estado a EN RUTA
    update_shipment_status(
        shipment=shipment,
        new_status=ShipmentStatusChoices.IN_TRANSIT,
        location="Santiago Centro",
        notes="Paquete cargado en furgón de reparto",
    )
    assert shipment.status == ShipmentStatusChoices.IN_TRANSIT
    assert shipment.progress_percentage == 75
    assert shipment.events.count() == 2

    # El pedido original pasa a ENVIADO
    order.refresh_from_db()
    assert order.status == OrderStatusChoices.SHIPPED

    # Buscar por tracking
    found = get_shipment_by_tracking(shipment.tracking_number)
    assert found == shipment


def test_delivery_route_last_mile(order, carrier):
    """Prueba la planificación de última milla y completado de paradas de entrega."""
    shipment = create_shipment_for_order(order=order, carrier=carrier)
    route = create_delivery_route(
        route_code="RUTA-STGO-ORIENTE-01",
        carrier=carrier,
        shipments=[shipment],
    )
    assert route.status == RouteStatusChoices.PLANNED
    assert route.stops.count() == 1

    stop = route.stops.first()
    assert not stop.is_completed

    # Repartidor entrega el paquete
    complete_route_stop(stop=stop, notes="Entregado en recepción del edificio")
    stop.refresh_from_db()
    assert stop.is_completed

    shipment.refresh_from_db()
    assert shipment.status == ShipmentStatusChoices.DELIVERED
    assert shipment.delivered_at is not None

    order.refresh_from_db()
    assert order.status == OrderStatusChoices.DELIVERED

    route.refresh_from_db()
    assert route.status == RouteStatusChoices.COMPLETED
