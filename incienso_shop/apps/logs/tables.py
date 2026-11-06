import django_tables2 as tables

from .models import ApplicationLogEntry


class ApplicationLogEntryTable(tables.Table):
    occurred_at = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="logs/includes/log_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = ApplicationLogEntry
        template_name = "django_tables2/bootstrap5.html"
        fields = ("occurred_at", "level", "logger_name", "event_code", "message")
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
