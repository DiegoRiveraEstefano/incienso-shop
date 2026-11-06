from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.products"
    verbose_name = _("Catálogo de Productos")
