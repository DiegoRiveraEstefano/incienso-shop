import django_filters

from .models import InstanceHealthCheck


class InstanceHealthCheckFilter(django_filters.FilterSet):
    class Meta:
        model = InstanceHealthCheck
        fields = ["status", "sqlite_journal_mode"]
