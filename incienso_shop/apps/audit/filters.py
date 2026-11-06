import django_filters
from auditlog.models import LogEntry

from .models import AuditEvent


class AuditEventFilter(django_filters.FilterSet):
    action = django_filters.ChoiceFilter(
        choices=LogEntry.Action.choices,
        label="Tipo de Acción",
    )
    remote_addr = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Dirección IP",
    )

    class Meta:
        model = AuditEvent
        fields = ["action", "actor", "content_type", "remote_addr"]
