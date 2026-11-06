from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MonitorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.monitor"
    verbose_name = _("Monitor de Instancia y DBA")
