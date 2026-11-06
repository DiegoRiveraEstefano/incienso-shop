from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.inventory"
    verbose_name = _("Inventario por Lotes & Proveedores")
