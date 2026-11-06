
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.shipping.choices import RouteStatusChoices
from incienso_shop.apps.shipping.choices import ShipmentStatusChoices
from incienso_shop.apps.shipping.models import Carrier
from incienso_shop.apps.shipping.models import DeliveryRoute
from incienso_shop.apps.shipping.models import RouteStop
from incienso_shop.apps.shipping.models import Shipment
from incienso_shop.apps.shipping.models import ShipmentEvent

if TYPE_CHECKING:
    from datetime import date

    from incienso_shop.apps.orders.models import Order


@transaction.atomic
def create_shipment_for_order(
    *,
    order: Order,
    carrier: Carrier | None = None,
    estimated_delivery_date: date | None = None,
) -> Shipment:
    """Crea el envío físico para un pedido confirmado y su primer evento de tracking."""
    shipment, created = Shipment.objects.get_or_create(
        order=order,
        defaults={
            "carrier": carrier,
            "status": ShipmentStatusChoices.PREPARING,
            "recipient_name": order.customer_name,
            "shipping_address": order.shipping_address,
            "shipping_city": order.shipping_city,
            "estimated_delivery_date": estimated_delivery_date,
            "delivery_notes": order.notes,
        },
    )

    if created:
        ShipmentEvent.objects.create(
            shipment=shipment,
            status=ShipmentStatusChoices.PREPARING,
            location="Centro de Distribución Incienso Shop",
            notes="El pedido ha ingresado a bodega y está siendo preparado.",
        )

    return shipment


@transaction.atomic
def update_shipment_status(
    *,
    shipment: Shipment,
    new_status: str,
    location: str,
    notes: str = "",
) -> ShipmentEvent:
    """Actualiza el estado logístico del envío y añade un hito al historial de tracking."""
    shipment.status = new_status
    if new_status == ShipmentStatusChoices.DELIVERED:
        shipment.delivered_at = timezone.now()
        # Sincronizar estado del pedido
        shipment.order.status = OrderStatusChoices.DELIVERED
        shipment.order.save(update_fields=["status"])
    elif new_status == ShipmentStatusChoices.IN_TRANSIT:
        shipment.order.status = OrderStatusChoices.SHIPPED
        shipment.order.save(update_fields=["status"])

    shipment.save(update_fields=["status", "delivered_at"])

    return ShipmentEvent.objects.create(
        shipment=shipment,
        status=new_status,
        location=location,
        notes=notes,
    )


@transaction.atomic
def create_delivery_route(
    *,
    route_code: str,
    carrier: Carrier,
    shipments: list[Shipment],
    scheduled_date: date | None = None,
    notes: str = "",
) -> DeliveryRoute:
    """Genera una hoja de ruta de última milla con paradas secuenciales."""
    route = DeliveryRoute.objects.create(
        route_code=route_code,
        carrier=carrier,
        scheduled_date=scheduled_date or timezone.now().date(),
        status=RouteStatusChoices.PLANNED,
        notes=notes,
    )

    for index, shipment in enumerate(shipments, start=1):
        RouteStop.objects.create(
            route=route,
            shipment=shipment,
            stop_order=index,
        )
        # Asignar transportista al envío
        shipment.carrier = carrier
        shipment.save(update_fields=["carrier"])

    return route


@transaction.atomic
def complete_route_stop(
    *,
    stop: RouteStop,
    notes: str = "Entregado en domicilio conforme",
) -> None:
    """Marca una parada como entregada y actualiza el tracking del envío asociado."""
    stop.is_completed = True
    stop.delivery_notes = notes
    stop.save(update_fields=["is_completed", "delivery_notes"])

    update_shipment_status(
        shipment=stop.shipment,
        new_status=ShipmentStatusChoices.DELIVERED,
        location=stop.shipment.shipping_city,
        notes=notes,
    )

    # Si todas las paradas están completas, cerrar la ruta
    all_stops = stop.route.stops.all()
    if all(s.is_completed for s in all_stops):
        stop.route.status = RouteStatusChoices.COMPLETED
        stop.route.save(update_fields=["status"])
