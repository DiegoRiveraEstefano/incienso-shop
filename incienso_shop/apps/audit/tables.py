import django_tables2 as tables

from .models import AuditEvent


class AuditEventTable(tables.Table):
    timestamp = tables.DateTimeColumn(
        format="Y-m-d H:i:s",
        linkify=True,
        verbose_name="Fecha / Hora",
    )
    action = tables.TemplateColumn(
        template_code="""
        {% if record.action == 0 %}
          <span class="badge text-bg-success">CREACIÓN</span>
        {% elif record.action == 1 %}
          <span class="badge text-bg-info">MODIFICACIÓN</span>
        {% elif record.action == 2 %}
          <span class="badge text-bg-danger">ELIMINACIÓN</span>
        {% else %}
          <span class="badge text-bg-secondary">{{ record.get_action_display }}</span>
        {% endif %}
        """,
        verbose_name="Acción",
    )
    content_type = tables.Column(verbose_name="Modelo")
    object_repr = tables.Column(verbose_name="Registro")
    actor = tables.Column(verbose_name="Usuario / Actor")
    remote_addr = tables.Column(verbose_name="IP")
    actions = tables.TemplateColumn(
        template_name="audit/includes/audit_actions.html",
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        model = AuditEvent
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "timestamp",
            "actor",
            "action",
            "content_type",
            "object_repr",
            "remote_addr",
        )
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
