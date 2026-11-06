from django.contrib import admin

from .models import DatabaseBackup


@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = (
        "backup_name",
        "status",
        "file_size_bytes",
        "is_compressed",
        "created_by",
        "created_at",
    )
    list_filter = ("backup_name", "status", "is_compressed")
