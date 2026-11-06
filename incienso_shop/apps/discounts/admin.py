from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.discounts.models import Coupon
from incienso_shop.apps.discounts.models import CouponUsage
from incienso_shop.apps.discounts.models import DiscountRule


@admin.register(DiscountRule)
class DiscountRuleAdmin(SimpleHistoryAdmin):
    list_display = ("name", "discount_type", "value", "min_order_amount", "is_active", "valid_from", "valid_until")
    list_filter = ("discount_type", "is_active")
    search_fields = ("name",)


@admin.register(Coupon)
class CouponAdmin(SimpleHistoryAdmin):
    list_display = ("code", "discount_rule", "used_count", "max_uses", "max_uses_per_user", "is_active", "valid_until")
    list_filter = ("is_active",)
    search_fields = ("code", "description")


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order", "discount_amount", "created_at")
    list_filter = ("created_at",)
    search_fields = ("coupon__code", "order__order_number", "user__username")
