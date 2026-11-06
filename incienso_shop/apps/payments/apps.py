from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShopPaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.payments"
    label = "shop_payments"
    verbose_name = _("Pagos y Transacciones")
