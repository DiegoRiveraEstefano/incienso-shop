from typing import TYPE_CHECKING

from .models import InstanceHealthCheck

if TYPE_CHECKING:
    from django.db.models import QuerySet


class InstanceHealthCheckSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[InstanceHealthCheck]:
        return InstanceHealthCheck.objects.all()
