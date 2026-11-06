from auditlog.registry import auditlog
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.models import BaseModel


@auditlog.register()
class InstanceHealthCheck(BaseModel):
    status = models.CharField(
        _("Estado Global"),
        max_length=20,
        default="healthy",
        db_index=True,
    )
    sqlite_journal_mode = models.CharField(
        _("SQLite Journal Mode"),
        max_length=20,
        default="wal",
    )
    sqlite_db_size_mb = models.DecimalField(
        _("Tamaño SQLite DB (MB)"),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    sqlite_wal_size_mb = models.DecimalField(
        _("Tamaño SQLite WAL (MB)"),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    diskcache_size_mb = models.DecimalField(
        _("Tamaño DiskCache (MB)"),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    active_db_connections = models.PositiveIntegerField(
        _("Conexiones DB Activas"),
        default=1,
    )
    response_time_ms = models.DecimalField(
        _("Latencia DB (ms)"),
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    notes = models.TextField(_("Diagnóstico / Notas"), blank=True)

    class Meta:
        verbose_name = _("Chequeo de Salud de Instancia")
        verbose_name_plural = _("Chequeos de Salud de Instancia")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        ts = f"{self.created_at:%Y-%m-%d %H:%M}"
        return f"Health [{self.status}] - DB: {self.sqlite_db_size_mb}MB ({ts})"

    def get_absolute_url(self) -> str:
        return reverse("monitor:health_detail", kwargs={"pk": self.pk})
