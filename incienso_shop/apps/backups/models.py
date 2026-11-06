from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.models import BaseModel


@auditlog.register()
class DatabaseBackup(BaseModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="database_backups",
        verbose_name=_("Creado Por"),
    )
    backup_name = models.CharField(_("Nombre del Backup"), max_length=200)
    file_path = models.CharField(_("Ruta del Archivo"), max_length=500)
    file_size_bytes = models.PositiveBigIntegerField(_("Tamaño (Bytes)"), default=0)
    checksum_sha256 = models.CharField(_("Checksum SHA-256"), max_length=64, blank=True)
    status = models.CharField(
        _("Estado"),
        max_length=20,
        default="completed",
        db_index=True,
    )
    is_compressed = models.BooleanField(_("Comprimido (.gz)"), default=True)
    notes = models.TextField(_("Notas"), blank=True)

    class Meta:
        verbose_name = _("Copia de Seguridad")
        verbose_name_plural = _("Copias de Seguridad")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.backup_name} ({self.status})"

    def get_absolute_url(self) -> str:
        return reverse("backups:backup_detail", kwargs={"pk": self.pk})
