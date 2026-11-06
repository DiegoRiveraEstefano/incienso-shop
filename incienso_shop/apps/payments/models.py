import uuid
from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from payments.models import BasePayment
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.payments.choices import AccountTypeChoices
from incienso_shop.apps.payments.choices import EntryTypeChoices


def generate_transaction_number() -> str:
    return f"TX-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@auditlog.register()
class Payment(BasePayment):
    """Modelo de pago transaccional que integra django-payments con los pedidos de la tienda."""

    order = models.ForeignKey(
        Order,
        related_name="payments",
        on_delete=models.CASCADE,
        verbose_name=_("Pedido Asociado"),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Transacción de Pago")
        verbose_name_plural = _("Transacciones de Pago")

    def __str__(self) -> str:
        return f"Pago #{self.id} ({self.variant}) - {self.status} - ${self.total}"

    def get_failure_url(self) -> str:
        return reverse(
            "shop_payments:payment_failure",
            kwargs={"order_number": self.order.order_number},
        )

    def get_success_url(self) -> str:
        return reverse(
            "shop_payments:payment_success",
            kwargs={"order_number": self.order.order_number},
        )

    def get_purchased_items(self):
        for item in self.order.items.all():
            yield {
                "name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "currency": self.currency,
            }


@auditlog.register()
class LedgerAccount(BaseModel):
    """Cuenta del catálogo contable para el libro de doble entrada."""

    code = models.CharField(_("Código Contable"), max_length=20, unique=True, db_index=True)
    name = models.CharField(_("Nombre de la Cuenta"), max_length=150)
    account_type = models.CharField(
        _("Tipo de Cuenta"),
        max_length=20,
        choices=AccountTypeChoices.choices,
        db_index=True,
    )
    is_active = models.BooleanField(_("Activa"), default=True)

    class Meta:
        verbose_name = _("Cuenta Contable")
        verbose_name_plural = _("Cuentas Contables")
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name} ({self.get_account_type_display()})"

    def get_balance(self) -> Decimal:
        """
        Calcula el saldo acumulado de la cuenta según su naturaleza contable:
        - Activos y Gastos: Débitos - Créditos
        - Pasivos, Patrimonio e Ingresos: Créditos - Débitos
        """
        total_debits = self.entries.filter(entry_type=EntryTypeChoices.DEBIT).aggregate(total=models.Sum("amount"))[
            "total"
        ] or Decimal("0.00")
        total_credits = self.entries.filter(entry_type=EntryTypeChoices.CREDIT).aggregate(total=models.Sum("amount"))[
            "total"
        ] or Decimal("0.00")

        if self.account_type in [AccountTypeChoices.ASSET, AccountTypeChoices.EXPENSE]:
            return total_debits - total_credits
        return total_credits - total_debits


@auditlog.register()
class LedgerTransaction(BaseModel):
    """Asiento contable compuesto en el libro diario de doble entrada."""

    transaction_number = models.CharField(
        _("Número de Asiento"),
        max_length=64,
        unique=True,
        default=generate_transaction_number,
        db_index=True,
    )
    entry_date = models.DateTimeField(_("Fecha y Hora Contable"), default=timezone.now, db_index=True)
    description = models.CharField(_("Glosa / Descripción del Asiento"), max_length=255)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_transactions",
        verbose_name=_("Pago Asociado"),
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_transactions",
        verbose_name=_("Pedido Asociado"),
    )
    is_posted = models.BooleanField(_("Asentado Definitivo"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Asiento Contable (Libro Diario)")
        verbose_name_plural = _("Asientos Contables (Libro Diario)")
        ordering = ["-entry_date", "-id"]

    def __str__(self) -> str:
        return f"{self.transaction_number}: {self.description}"

    @property
    def total_debits(self) -> Decimal:
        return self.entries.filter(entry_type=EntryTypeChoices.DEBIT).aggregate(total=models.Sum("amount"))[
            "total"
        ] or Decimal("0.00")

    @property
    def total_credits(self) -> Decimal:
        return self.entries.filter(entry_type=EntryTypeChoices.CREDIT).aggregate(total=models.Sum("amount"))[
            "total"
        ] or Decimal("0.00")

    @property
    def is_balanced(self) -> bool:
        return self.total_debits == self.total_credits and self.total_debits > Decimal("0.00")


class LedgerEntry(BaseModel):
    """Apunte individual (Débito o Crédito) en una cuenta contable específica."""

    transaction = models.ForeignKey(
        LedgerTransaction,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name=_("Asiento Contable"),
    )
    account = models.ForeignKey(
        LedgerAccount,
        on_delete=models.PROTECT,
        related_name="entries",
        verbose_name=_("Cuenta Afectada"),
    )
    entry_type = models.CharField(
        _("Tipo de Movimiento"),
        max_length=10,
        choices=EntryTypeChoices.choices,
    )
    amount = models.DecimalField(_("Monto"), max_digits=12, decimal_places=2)
    notes = models.CharField(_("Notas de Línea"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Línea de Asiento Contable")
        verbose_name_plural = _("Líneas de Asiento Contable")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=Decimal("0.00")),
                name="check_ledger_entry_amount_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account.code} | {self.get_entry_type_display()}: ${self.amount}"
