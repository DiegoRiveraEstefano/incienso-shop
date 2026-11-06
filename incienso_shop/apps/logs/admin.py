from django.contrib import admin

from .models import ApplicationLogEntry


@admin.register(ApplicationLogEntry)
class ApplicationLogEntryAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "level", "logger_name", "event_code", "message")
    list_filter = ("level", "logger_name", "event_code")
