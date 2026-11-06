import logging

from django.db import transaction

from .models import DatabaseBackup

logger = logging.getLogger(__name__)


class DatabaseBackupService:
    @classmethod
    @transaction.atomic
    def save_record(
        cls,
        *,
        instance: DatabaseBackup | None = None,
        **data,
    ) -> DatabaseBackup:
        obj = instance or DatabaseBackup()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("backups_backup_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: DatabaseBackup) -> None:
        rid = instance.id
        instance.delete()
        logger.info("backups_backup_deleted", extra={"record_id": rid})
