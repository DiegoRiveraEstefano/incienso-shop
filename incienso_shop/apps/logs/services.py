import logging

from django.db import transaction

from .models import ApplicationLogEntry

logger = logging.getLogger(__name__)


class ApplicationLogEntryService:
    @classmethod
    @transaction.atomic
    def save_record(
        cls,
        *,
        instance: ApplicationLogEntry | None = None,
        **data,
    ) -> ApplicationLogEntry:
        obj = instance or ApplicationLogEntry()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("logs_log_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: ApplicationLogEntry) -> None:
        rid = instance.id
        instance.delete()
        logger.info("logs_log_deleted", extra={"record_id": rid})
