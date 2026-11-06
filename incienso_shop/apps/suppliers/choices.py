from django.db import models
from django.utils.translation import gettext_lazy as _


class PurchaseOrderStatusChoices(models.TextChoices):
    DRAFT = "DRAFT", _("Borrador")
    SUBMITTED = "SUBMITTED", _("Enviado al Proveedor")
    PARTIALLY_RECEIVED = "PARTIAL", _("Recibido Parcial")
    RECEIVED = "RECEIVED", _("Recibido Completo")
    CANCELLED = "CANCELLED", _("Cancelado")
