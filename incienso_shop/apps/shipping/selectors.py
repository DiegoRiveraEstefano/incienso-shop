
from typing import TYPE_CHECKING

from incienso_shop.apps.shipping.choices import RouteStatusChoices
from incienso_shop.apps.shipping.choices import ShipmentStatusChoices
from incienso_shop.apps.shipping.models import Carrier
from incienso_shop.apps.shipping.models import DeliveryRoute
from incienso_shop.apps.shipping.models import Shipment

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_shipment_by_tracking(tracking_number: str) -> Shipment | None:
    """Busca un envío por su código de rastreo único con todos sus eventos."""
    return (
        Shipment.objects.filter(tracking_number__iexact=tracking_number.strip())
        .select_related("order", "carrier")
        .prefetch_related("events")
        .first()
    )


def get_pending_shipments() -> QuerySet[Shipment]:
    """Retorna los envíos que aún no han sido entregados o cerrados."""
    return (
        Shipment.objects.exclude(status__in=[ShipmentStatusChoices.DELIVERED, ShipmentStatusChoices.RETURNED])
        .select_related("order", "carrier")
        .order_by("-created_at")
    )


def get_active_delivery_routes() -> QuerySet[DeliveryRoute]:
    return (
        DeliveryRoute.objects.filter(status__in=[RouteStatusChoices.PLANNED, RouteStatusChoices.IN_PROGRESS])
        .select_related("carrier")
        .prefetch_related("stops__shipment")
        .order_by("-scheduled_date")
    )


def get_all_carriers() -> QuerySet[Carrier]:
    return Carrier.objects.filter(is_active=True).order_by("name")
