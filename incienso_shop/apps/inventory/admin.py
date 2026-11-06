from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.inventory.models import ProductBatch
from incienso_shop.apps.inventory.models import StockMovement


@admin.register(ProductBatch)
class ProductBatchAdmin(SimpleHistoryAdmin):
    list_display = (
        "batch_code",
        "product",
        "supplier",
        "available_quantity",
        "initial_quantity",
        "unit_cost",
        "received_date",
        "expiry_date",
        "is_active",
    )
    list_filter = ("is_active", "received_date", "expiry_date")
    search_fields = ("batch_code", "product__name", "product__sku")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "movement_type",
        "product",
        "batch",
        "quantity",
        "unit_cost",
        "reference_order_number",
    )
    list_filter = ("movement_type", "created_at")
    search_fields = ("reference_order_number", "product__name", "batch__batch_code")
