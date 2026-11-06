from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.models import BaseModel


class ApplicationLogEntry(BaseModel):
    level = models.CharField(_("Nivel"), max_length=20, default="INFO", db_index=True)
    logger_name = models.CharField(_("Logger / Módulo"), max_length=150, db_index=True)
    event_code = models.CharField(
        _("Código de Evento (snake_case)"),
        max_length=150,
        db_index=True,
    )
    message = models.TextField(_("Mensaje"))
    extra_data = models.JSONField(_("Metadatos Extra"), default=dict, blank=True)
    traceback_text = models.TextField(_("Traceback"), blank=True)
    occurred_at = models.DateTimeField(_("Ocurrido el"), db_index=True)

    class Meta:
        verbose_name = _("Entrada de Log")
        verbose_name_plural = _("Entradas de Log")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.level}] {self.event_code} ({self.logger_name})"

    def get_absolute_url(self) -> str:
        return reverse("logs:log_detail", kwargs={"pk": self.pk})
