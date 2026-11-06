from django.db import models
from django.utils.translation import gettext_lazy as _


class DiscountTypeChoices(models.TextChoices):
    PERCENTAGE = "PERCENT", _("Porcentaje (%) sobre el total")
    FIXED_AMOUNT = "FIXED", _("Monto Fijo ($) de Descuento")
    CATEGORY_PERCENT = "CAT_PERCENT", _("Porcentaje (%) sobre Categoría Específica")
