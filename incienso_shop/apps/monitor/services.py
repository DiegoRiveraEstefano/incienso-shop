import logging

from django.db import transaction

from .models import InstanceHealthCheck

logger = logging.getLogger(__name__)


class InstanceHealthCheckService:
    @classmethod
    @transaction.atomic
    def save_record(
        cls,
        *,
        instance: InstanceHealthCheck | None = None,
        **data,
    ) -> InstanceHealthCheck:
        obj = instance or InstanceHealthCheck()
        for field, value in data.items():
            setattr(obj, field, value)
        obj.save()
        logger.info("monitor_health_saved", extra={"record_id": obj.id})
        return obj

    @classmethod
    @transaction.atomic
    def delete_record(cls, *, instance: InstanceHealthCheck) -> None:
        rid = instance.id
        instance.delete()
        logger.info("monitor_health_deleted", extra={"record_id": rid})
