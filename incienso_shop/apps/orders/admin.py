from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "total_items",
        "subtotal",
        "updated_at",
    )
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "line_total",
    )


@admin.register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "customer_email",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "order_number",
        "customer_name",
        "customer_email",
        "shipping_address",
    )
    readonly_fields = (
        "order_number",
        "subtotal",
        "shipping_cost",
        "tax_amount",
        "total_amount",
    )
    inlines = [OrderItemInline]
