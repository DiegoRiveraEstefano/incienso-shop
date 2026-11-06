from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatusChoices(models.TextChoices):
    PENDING = "PENDING", _("Pendiente de Pago")
    PAID = "PAID", _("Pagado / Confirmado")
    PROCESSING = "PROCESSING", _("En Preparación Artesanal")
    SHIPPED = "SHIPPED", _("Enviado / En Tránsito")
    DELIVERED = "DELIVERED", _("Entregado")
    CANCELLED = "CANCELLED", _("Cancelado")
