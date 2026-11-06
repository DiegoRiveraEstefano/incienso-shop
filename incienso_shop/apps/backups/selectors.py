from typing import TYPE_CHECKING

from .models import DatabaseBackup

if TYPE_CHECKING:
    from django.db.models import QuerySet


class DatabaseBackupSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[DatabaseBackup]:
        return DatabaseBackup.objects.all()
