from auditlog.admin import LogEntryAdmin
from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(LogEntryAdmin):
    list_display = (
        "created_at",
        "actor",
        "event_action",
        "target_model",
        "target_object_id",
        "ip_address",
        "summary",
    )
    search_fields = ("object_repr", "changes_text", "remote_addr", "object_pk")
