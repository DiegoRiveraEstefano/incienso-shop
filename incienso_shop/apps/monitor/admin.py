from django.contrib import admin

from .models import InstanceHealthCheck


@admin.register(InstanceHealthCheck)
class InstanceHealthCheckAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "status",
        "sqlite_journal_mode",
        "sqlite_db_size_mb",
        "diskcache_size_mb",
        "response_time_ms",
    )
    list_filter = ("status", "sqlite_journal_mode")
