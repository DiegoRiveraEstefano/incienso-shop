from django.db import models
from django.utils.translation import gettext_lazy as _


class PurchaseOrderStatusChoices(models.TextChoices):
    DRAFT = "DRAFT", _("Borrador")
    SUBMITTED = "SUBMITTED", _("Enviado al Proveedor")
    PARTIALLY_RECEIVED = "PARTIAL", _("Recibido Parcial")
    RECEIVED = "RECEIVED", _("Recibido Completo")
    CANCELLED = "CANCELLED", _("Cancelado")


class StockMovementTypeChoices(models.TextChoices):
    PURCHASE_RECEIPT = "RECEIPT", _("Recepción de Compra (Ingreso de Lote)")
    FIFO_SALE = "FIFO_SALE", _("Salida por Venta (FIFO)")
    MANUAL_ADJUSTMENT = "ADJUSTMENT", _("Ajuste Manual / Conteo Físico")
    SCRAP = "SCRAP", _("Merma / Daño")
    RETURN = "RETURN", _("Devolución de Cliente")


MovementTypeChoices = StockMovementTypeChoices
