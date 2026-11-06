from typing import TYPE_CHECKING

from .models import ApplicationLogEntry

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ApplicationLogEntrySelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[ApplicationLogEntry]:
        return ApplicationLogEntry.objects.all()
