from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShippingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.shipping"
    verbose_name = _("Logística & Envíos")
