from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.suppliers.models import PurchaseOrder
from incienso_shop.apps.suppliers.models import PurchaseOrderItem
from incienso_shop.apps.suppliers.models import Supplier


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(SimpleHistoryAdmin):
    list_display = ("name", "contact_name", "email", "phone", "country", "lead_time_days", "is_active")
    list_filter = ("country", "is_active")
    search_fields = ("name", "contact_name", "email", "tax_id")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(SimpleHistoryAdmin):
    list_display = ("po_number", "supplier", "status", "order_date", "expected_delivery_date", "total_amount")
    list_filter = ("status", "order_date")
    search_fields = ("po_number", "supplier__name")
    inlines = [PurchaseOrderItemInline]
