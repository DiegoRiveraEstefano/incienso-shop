from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BackupsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.backups"
    verbose_name = _("Copias de Seguridad (SQLite)")
