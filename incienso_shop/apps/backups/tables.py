import django_tables2 as tables

from .models import DatabaseBackup


class DatabaseBackupTable(tables.Table):
    backup_name = tables.Column(linkify=True)
    actions = tables.TemplateColumn(
        template_name="backups/includes/backup_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = DatabaseBackup
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "backup_name",
            "status",
            "file_size_bytes",
            "is_compressed",
            "created_by",
            "created_at",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
