from auditlog.models import LogEntry
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class AuditEvent(LogEntry):
    class Meta:
        proxy = True
        verbose_name = _("Evento de Auditoría")
        verbose_name_plural = _("Eventos de Auditoría")
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        action_name = self.get_action_display().upper()
        ts = f"{self.timestamp:%Y-%m-%d %H:%M}"
        return f"[{action_name}] {self.content_type} #{self.object_pk} ({ts})"

    def get_absolute_url(self) -> str:
        return reverse("audit:audit_detail", kwargs={"pk": self.pk})

    @property
    def created_at(self):
        return self.timestamp

    @property
    def event_action(self) -> str:
        return self.get_action_display()

    @property
    def target_model(self) -> str:
        return str(self.content_type)

    @property
    def target_object_id(self) -> str:
        return self.object_pk

    @property
    def ip_address(self) -> str | None:
        return self.remote_addr

    @property
    def summary(self) -> str:
        action_name = self.get_action_display().title()
        return f"{action_name} {self.content_type}: {self.object_repr}"

    @property
    def changes_payload(self):
        return self.changes_display_dict
