from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountTypeChoices(models.TextChoices):
    ASSET = "ASSET", _("Activo (Caja, Banco, Pasarelas por Cobrar)")
    LIABILITY = "LIABILITY", _("Pasivo (Obligaciones, Cuentas por Pagar)")
    EQUITY = "EQUITY", _("Patrimonio")
    REVENUE = "REVENUE", _("Ingresos (Ventas de Inciensos)")
    EXPENSE = "EXPENSE", _("Gastos (Costes Operativos, Comisiones Pasarela)")


class EntryTypeChoices(models.TextChoices):
    DEBIT = "DEBIT", _("Débito (Debe)")
    CREDIT = "CREDIT", _("Crédito (Haber)")
