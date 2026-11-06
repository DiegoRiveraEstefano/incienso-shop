import uuid

from auditlog.registry import auditlog
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.shipping.choices import RouteStatusChoices
from incienso_shop.apps.shipping.choices import ShipmentStatusChoices


def generate_tracking_number() -> str:
    return f"TRK-{uuid.uuid4().hex[:10].upper()}"


@auditlog.register()
class Carrier(BaseModel):
    """Transportista, repartidor o empresa de encomiendas."""

    name = models.CharField(_("Nombre / Empresa"), max_length=150)
    phone = models.CharField(_("Teléfono"), max_length=50, blank=True)
    vehicle_plate = models.CharField(_("Patente / Matrícula del Vehículo"), max_length=20, blank=True)
    is_active = models.BooleanField(_("Activo"), default=True)

    class Meta:
        verbose_name = _("Transportista / Repartidor")
        verbose_name_plural = _("Transportistas / Repartidores")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.vehicle_plate})" if self.vehicle_plate else self.name


@auditlog.register()
class Shipment(BaseModel):
    """Paquete y despacho logístico asociado a un pedido."""

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipment",
        verbose_name=_("Pedido de Venta"),
    )
    tracking_number = models.CharField(
        _("Número de Rastreo"),
        max_length=64,
        unique=True,
        default=generate_tracking_number,
        db_index=True,
    )
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipments",
        verbose_name=_("Transportista"),
    )
    status = models.CharField(
        _("Estado de Envío"),
        max_length=20,
        choices=ShipmentStatusChoices.choices,
        default=ShipmentStatusChoices.PREPARING,
        db_index=True,
    )
    recipient_name = models.CharField(_("Nombre del Destinatario"), max_length=200)
    shipping_address = models.CharField(_("Dirección de Entrega"), max_length=255)
    shipping_city = models.CharField(_("Ciudad / Comuna"), max_length=100)
    estimated_delivery_date = models.DateField(_("Fecha Estimada de Entrega"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Fecha y Hora de Entrega Efectiva"), null=True, blank=True)
    delivery_notes = models.TextField(_("Observaciones de Despacho"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Envío de Pedido")
        verbose_name_plural = _("Envíos de Pedidos")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tracking_number} - {self.get_status_display()}"

    @property
    def progress_percentage(self) -> int:
        mapping = {
            ShipmentStatusChoices.PREPARING: 20,
            ShipmentStatusChoices.READY_FOR_DISPATCH: 45,
            ShipmentStatusChoices.IN_TRANSIT: 75,
            ShipmentStatusChoices.DELIVERED: 100,
            ShipmentStatusChoices.FAILED_ATTEMPT: 75,
            ShipmentStatusChoices.RETURNED: 100,
        }
        return mapping.get(self.status, 20)


class ShipmentEvent(BaseModel):
    """Hito o evento cronológico en la vida del envío."""

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Envío"),
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=ShipmentStatusChoices.choices,
    )
    location = models.CharField(_("Ubicación / Ciudad"), max_length=150, default="Centro de Distribución")
    notes = models.CharField(_("Detalle / Observación"), max_length=255, blank=True)
    timestamp = models.DateTimeField(_("Fecha y Hora del Evento"), default=timezone.now)

    class Meta:
        verbose_name = _("Evento de Envío")
        verbose_name_plural = _("Eventos de Envío")
        ordering = ["-timestamp", "-id"]

    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.get_status_display()} - {self.location}"


@auditlog.register()
class DeliveryRoute(BaseModel):
    """Hoja de ruta para logística de última milla."""

    route_code = models.CharField(_("Código de Ruta"), max_length=50, unique=True, db_index=True)
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.PROTECT,
        related_name="routes",
        verbose_name=_("Repartidor Asignado"),
    )
    scheduled_date = models.DateField(_("Fecha Programada"), default=timezone.now)
    status = models.CharField(
        _("Estado de la Ruta"),
        max_length=20,
        choices=RouteStatusChoices.choices,
        default=RouteStatusChoices.PLANNED,
    )
    notes = models.TextField(_("Instrucciones de Ruta"), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Ruta de Entrega (Última Milla)")
        verbose_name_plural = _("Rutas de Entrega (Última Milla)")
        ordering = ["-scheduled_date", "-id"]

    def __str__(self) -> str:
        return f"{self.route_code} ({self.carrier.name}) - {self.scheduled_date}"


class RouteStop(BaseModel):
    """Parada o parada de entrega específica en una ruta."""

    route = models.ForeignKey(
        DeliveryRoute,
        on_delete=models.CASCADE,
        related_name="stops",
        verbose_name=_("Ruta"),
    )
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.PROTECT,
        related_name="route_stops",
        verbose_name=_("Envío Asociado"),
    )
    stop_order = models.PositiveIntegerField(_("Orden de Visita"), default=1)
    is_completed = models.BooleanField(_("Entrega Realizada"), default=False)
    delivery_notes = models.TextField(_("Comentarios del Repartidor"), blank=True)

    class Meta:
        verbose_name = _("Parada de Ruta")
        verbose_name_plural = _("Paradas de Rutas")
        ordering = ["route", "stop_order"]
        unique_together = ("route", "shipment")

    def __str__(self) -> str:
        return f"Parada #{self.stop_order}: {self.shipment.recipient_name} ({self.route.route_code})"
