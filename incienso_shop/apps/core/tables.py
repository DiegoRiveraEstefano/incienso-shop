import django_tables2 as tables

from .models import StoreSettings


class StoreSettingsTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name="core/tables/settings_actions.html",
        orderable=False,
        verbose_name="Acciones",
    )

    class Meta:
        model = StoreSettings
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "store_name",
            "currency",
            "free_shipping_threshold",
            "standard_shipping_cost",
            "maintenance_mode",
            "updated_at",
        )
