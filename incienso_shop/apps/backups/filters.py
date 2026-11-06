import django_filters

from .models import DatabaseBackup


class DatabaseBackupFilter(django_filters.FilterSet):
    class Meta:
        model = DatabaseBackup
        fields = ["backup_name", "status", "is_compressed"]
