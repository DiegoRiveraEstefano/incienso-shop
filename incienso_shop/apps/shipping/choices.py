from django.db import models
from django.utils.translation import gettext_lazy as _


class ShipmentStatusChoices(models.TextChoices):
    PREPARING = "PREPARING", _("Preparando en Almacén")
    READY_FOR_DISPATCH = "READY", _("Listo para Despacho")
    IN_TRANSIT = "IN_TRANSIT", _("En Ruta / En Camino")
    DELIVERED = "DELIVERED", _("Entregado Exitosamente")
    FAILED_ATTEMPT = "FAILED", _("Intento Fallido de Entrega")
    RETURNED = "RETURNED", _("Devuelto al Almacén")


class RouteStatusChoices(models.TextChoices):
    PLANNED = "PLANNED", _("Planificada")
    IN_PROGRESS = "IN_PROGRESS", _("En Curso / En Reparto")
    COMPLETED = "COMPLETED", _("Completada")
