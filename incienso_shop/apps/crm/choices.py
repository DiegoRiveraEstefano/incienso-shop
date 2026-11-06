from django.db import models
from django.utils.translation import gettext_lazy as _


class LoyaltyTierChoices(models.TextChoices):
    BRONZE = "BRONZE", _("Bronce (Iniciado)")
    SILVER = "SILVER", _("Plata (Aspirante)")
    GOLD = "GOLD", _("Oro (Maestro Aromático)")
    PLATINUM = "PLATINUM", _("Platino (Guardián del Templo)")


class PointTransactionTypeChoices(models.TextChoices):
    PURCHASE_EARNED = "EARNED", _("Puntos Ganados por Compra")
    REDEMPTION = "REDEEMED", _("Puntos Canjeados")
    MANUAL_ADJUSTMENT = "ADJUSTMENT", _("Ajuste Manual / Cortesía")
    EXPIRATION = "EXPIRED", _("Expiración de Puntos")


class DealPriorityChoices(models.TextChoices):
    LOW = "LOW", _("Baja")
    MEDIUM = "MEDIUM", _("Media")
    HIGH = "HIGH", _("Alta")
    URGENT = "URGENT", _("Urgente")


class CampaignStatusChoices(models.TextChoices):
    DRAFT = "DRAFT", _("Borrador")
    SENT = "SENT", _("Enviado Exitosamente")
    FAILED = "FAILED", _("Fallo en Envío")
