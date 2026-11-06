import logging

from django.db import transaction

from .models import AuditEvent

logger = logging.getLogger(__name__)


class AuditEventService:
    @classmethod
    @transaction.atomic
    def save_record(cls, *, instance: AuditEvent | None = None, **data) -> AuditEvent:
        obj = instance or AuditEvent()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("audit_audit_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: AuditEvent) -> None:
        rid = instance.id
        instance.delete()
        logger.info("audit_audit_deleted", extra={"record_id": rid})
