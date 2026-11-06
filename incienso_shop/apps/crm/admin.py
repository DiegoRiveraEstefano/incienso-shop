from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.crm.models import CustomerSegment
from incienso_shop.apps.crm.models import CustomerSegmentMembership
from incienso_shop.apps.crm.models import Deal
from incienso_shop.apps.crm.models import EmailCampaign
from incienso_shop.apps.crm.models import FunnelStage
from incienso_shop.apps.crm.models import LoyaltyAccount
from incienso_shop.apps.crm.models import LoyaltyTier
from incienso_shop.apps.crm.models import PointTransaction
from incienso_shop.apps.crm.models import SalesFunnel


@admin.register(LoyaltyTier)
class LoyaltyTierAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "min_spent", "points_multiplier", "badge_color")


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(SimpleHistoryAdmin):
    list_display = ("user", "current_tier", "points_balance", "lifetime_points", "total_spent")
    search_fields = ("user__username", "user__email")


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "transaction_type", "points", "order", "created_at")
    list_filter = ("transaction_type",)


class FunnelStageInline(admin.TabularInline):
    model = FunnelStage
    extra = 3


@admin.register(SalesFunnel)
class SalesFunnelAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    inlines = [FunnelStageInline]


@admin.register(Deal)
class DealAdmin(SimpleHistoryAdmin):
    list_display = ("title", "stage", "customer_name", "estimated_value", "priority", "expected_close_date")
    list_filter = ("priority", "stage__funnel", "stage")
    search_fields = ("title", "customer_name", "customer_email")


class CustomerSegmentMembershipInline(admin.TabularInline):
    model = CustomerSegmentMembership
    extra = 1


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    inlines = [CustomerSegmentMembershipInline]


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "segment", "status", "recipients_count", "sent_at")
    list_filter = ("status", "created_at")
