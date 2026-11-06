from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.utils.translation import gettext_lazy as _


def configure_sqlite_pragmas(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA temp_store=MEMORY;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.execute("PRAGMA busy_timeout=5000;")


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "incienso_shop.apps.core"
    verbose_name = _("Core & Configuración")

    def ready(self):
        connection_created.connect(configure_sqlite_pragmas)
