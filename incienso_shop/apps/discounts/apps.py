from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiscountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.discounts"
    verbose_name = _("Descuentos y Cupones")
