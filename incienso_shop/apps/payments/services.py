from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

from django.db import transaction

from incienso_shop.apps.orders.services import OrderService
from incienso_shop.apps.payments.choices import AccountTypeChoices
from incienso_shop.apps.payments.choices import EntryTypeChoices
from incienso_shop.apps.payments.exceptions import UnbalancedTransactionError
from incienso_shop.apps.payments.models import LedgerAccount
from incienso_shop.apps.payments.models import LedgerEntry
from incienso_shop.apps.payments.models import LedgerTransaction
from incienso_shop.apps.payments.models import Payment

if TYPE_CHECKING:
    from incienso_shop.apps.orders.models import Order


def get_or_create_default_chart_of_accounts() -> dict[str, LedgerAccount]:
    """Inicializa o recupera el catálogo estándar de cuentas contables del e-commerce."""
    defaults = [
        ("1100", "Pasarelas de Pago por Liquidar", AccountTypeChoices.ASSET),
        ("1200", "Cuentas por Cobrar Clientes", AccountTypeChoices.ASSET),
        ("2000", "Cuentas por Pagar Proveedores", AccountTypeChoices.LIABILITY),
        ("4000", "Ingresos por Ventas de Inciensos", AccountTypeChoices.REVENUE),
        ("4100", "Devoluciones sobre Ventas", AccountTypeChoices.REVENUE),
        ("5100", "Comisiones de Pasarelas de Pago", AccountTypeChoices.EXPENSE),
    ]
    accounts = {}
    for code, name, acc_type in defaults:
        acc, _ = LedgerAccount.objects.get_or_create(
            code=code,
            defaults={"name": name, "account_type": acc_type, "is_active": True},
        )
        accounts[code] = acc
    return accounts


@transaction.atomic
def record_double_entry_transaction(
    *,
    description: str,
    entries_data: list[dict[str, Any]],
    payment: Payment | None = None,
    order: Any = None,
) -> LedgerTransaction:
    """
    Registra un asiento en el libro diario verificando la partida doble estricta:
    Suma de Débitos == Suma de Créditos.
    """
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for entry in entries_data:
        amount = Decimal(str(entry["amount"]))
        if amount <= Decimal("0.00"):
            msg = "Los montos de las líneas contables deben ser mayores a cero."
            raise UnbalancedTransactionError(msg)

        if entry["entry_type"] == EntryTypeChoices.DEBIT:
            total_debit += amount
        elif entry["entry_type"] == EntryTypeChoices.CREDIT:
            total_credit += amount

    if total_debit != total_credit or total_debit == Decimal("0.00"):
        msg = (
            f"Asiento desbalanceado: La suma de débitos (${total_debit}) no coincide "
            f"con la suma de créditos (${total_credit})."
        )
        raise UnbalancedTransactionError(msg)

    tx = LedgerTransaction.objects.create(
        description=description,
        payment=payment,
        order=order,
        is_posted=True,
    )

    for entry in entries_data:
        LedgerEntry.objects.create(
            transaction=tx,
            account=entry["account"],
            entry_type=entry["entry_type"],
            amount=Decimal(str(entry["amount"])),
            notes=entry.get("notes", ""),
        )

    return tx


class PaymentService:
    @staticmethod
    @transaction.atomic
    def create_payment_for_order(order: Order, variant: str = "dummy") -> Payment:
        return Payment.objects.create(
            order=order,
            variant=variant,
            description=f"Pago Pedido #{str(order.order_number)[:8]}",
            total=order.total_amount,
            currency="USD",
            billing_first_name=order.customer_name.split()[0] if order.customer_name else "Cliente",
            billing_last_name=" ".join(order.customer_name.split()[1:])
            if len(order.customer_name.split()) > 1
            else "",
            billing_address_1=order.shipping_address,
            billing_city=order.shipping_city,
            billing_postcode=order.shipping_postal_code or "10000",
            billing_country_code="CL",
            billing_email=order.customer_email,
        )

    @staticmethod
    @transaction.atomic
    def complete_payment(payment: Payment) -> Payment:
        payment.status = "confirmed"
        payment.save(update_fields=["status", "modified"])
        OrderService.mark_as_paid(payment.order)

        # Registro contable de partida doble (Débito Pasarela / Crédito Ingresos Ventas)
        accounts = get_or_create_default_chart_of_accounts()
        record_double_entry_transaction(
            description=f"Cobro exitoso Pedido #{str(payment.order.order_number)[:8]} vía {payment.variant}",
            payment=payment,
            order=payment.order,
            entries_data=[
                {
                    "account": accounts["1100"],  # Activo: Pasarelas de Pago por Liquidar
                    "entry_type": EntryTypeChoices.DEBIT,
                    "amount": payment.total,
                    "notes": f"Ingreso fondos pasarela {payment.variant}",
                },
                {
                    "account": accounts["4000"],  # Ingresos: Ventas de Inciensos
                    "entry_type": EntryTypeChoices.CREDIT,
                    "amount": payment.total,
                    "notes": f"Venta generada por pedido #{str(payment.order.order_number)[:8]}",
                },
            ],
        )

        return payment
