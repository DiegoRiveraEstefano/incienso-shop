from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(SimpleHistoryAdmin):
    list_display = (
        "store_name",
        "currency",
        "free_shipping_threshold",
        "maintenance_mode",
        "updated_at",
    )
    search_fields = ("store_name", "contact_email")
