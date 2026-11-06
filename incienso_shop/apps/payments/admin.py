from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.payments.models import LedgerAccount
from incienso_shop.apps.payments.models import LedgerEntry
from incienso_shop.apps.payments.models import LedgerTransaction
from incienso_shop.apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "order",
        "variant",
        "status",
        "total",
        "currency",
        "created",
        "modified",
    )
    list_filter = ("status", "variant", "currency")
    search_fields = (
        "order__order_number",
        "billing_email",
        "billing_first_name",
        "billing_last_name",
    )
    readonly_fields = ("created", "modified")


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "account_type", "current_balance", "is_active")
    list_filter = ("account_type", "is_active")
    search_fields = ("code", "name")

    @admin.display(description="Saldo Actual")
    def current_balance(self, obj):
        return f"${obj.get_balance()}"


class LedgerEntryInline(admin.TabularInline):
    model = LedgerEntry
    extra = 2


@admin.register(LedgerTransaction)
class LedgerTransactionAdmin(SimpleHistoryAdmin):
    list_display = (
        "transaction_number",
        "entry_date",
        "description",
        "total_debits",
        "total_credits",
        "is_balanced",
        "is_posted",
    )
    list_filter = ("is_posted", "entry_date")
    search_fields = ("transaction_number", "description")
    inlines = [LedgerEntryInline]


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("transaction", "account", "entry_type", "amount", "created_at")
    list_filter = ("entry_type", "account__account_type")
    search_fields = ("transaction__transaction_number", "account__code", "account__name")
