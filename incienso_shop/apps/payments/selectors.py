from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

from django.db.models import Sum

from incienso_shop.apps.payments.choices import EntryTypeChoices
from incienso_shop.apps.payments.models import LedgerAccount
from incienso_shop.apps.payments.models import LedgerTransaction
from incienso_shop.apps.payments.models import Payment

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PaymentSelector:
    @staticmethod
    def get_latest_for_order(order) -> Payment | None:
        return Payment.objects.filter(order=order).order_by("-created").first()

    @staticmethod
    def list_all() -> QuerySet[Payment]:
        return Payment.objects.all().select_related("order").order_by("-created")

    @staticmethod
    def get_payment_transactions(payment: Payment) -> QuerySet[LedgerTransaction]:
        return (
            LedgerTransaction.objects.filter(payment=payment)
            .prefetch_related("entries__account")
            .order_by("-entry_date")
        )

    @staticmethod
    def get_trial_balance() -> dict[str, Any]:
        """Genera el Balance de Comprobación de Sumas y Saldos de doble entrada."""
        accounts = LedgerAccount.objects.filter(is_active=True).order_by("code")
        account_rows = []
        grand_total_debits = Decimal("0.00")
        grand_total_credits = Decimal("0.00")

        for acc in accounts:
            debits = acc.entries.filter(entry_type=EntryTypeChoices.DEBIT).aggregate(tot=Sum("amount"))[
                "tot"
            ] or Decimal("0.00")
            total_credits = acc.entries.filter(entry_type=EntryTypeChoices.CREDIT).aggregate(tot=Sum("amount"))[
                "tot"
            ] or Decimal("0.00")
            balance = acc.get_balance()

            grand_total_debits += debits
            grand_total_credits += total_credits

            account_rows.append(
                {
                    "account": acc,
                    "debits": debits,
                    "credits": total_credits,
                    "balance": balance,
                },
            )

        return {
            "rows": account_rows,
            "grand_total_debits": grand_total_debits,
            "grand_total_credits": grand_total_credits,
            "is_balanced": grand_total_debits == grand_total_credits,
        }
