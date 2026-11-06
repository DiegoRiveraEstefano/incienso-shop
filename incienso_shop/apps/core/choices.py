from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyChoices(models.TextChoices):
    USD = "USD", _("Dólar Estadounidense (USD)")
    EUR = "EUR", _("Euro (EUR)")
    CLP = "CLP", _("Peso Chileno (CLP)")


class SiteStatusChoices(models.TextChoices):
    ACTIVE = "ACTIVE", _("Activo")
    MAINTENANCE = "MAINTENANCE", _("En Mantenimiento")
