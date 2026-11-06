import django_tables2 as tables

from .models import InstanceHealthCheck


class InstanceHealthCheckTable(tables.Table):
    created_at = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="monitor/includes/health_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = InstanceHealthCheck
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "created_at",
            "status",
            "sqlite_journal_mode",
            "sqlite_db_size_mb",
            "diskcache_size_mb",
            "response_time_ms",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
