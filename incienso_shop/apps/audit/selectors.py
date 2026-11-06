from typing import TYPE_CHECKING

from .models import AuditEvent

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AuditEventSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[AuditEvent]:
        return AuditEvent.objects.select_related("actor", "content_type").order_by(
            "-timestamp",
        )

    @classmethod
    def get_by_id(cls, pk: int) -> AuditEvent | None:
        return cls.get_queryset().filter(pk=pk).first()
