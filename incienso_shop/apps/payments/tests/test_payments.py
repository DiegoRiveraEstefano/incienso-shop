from decimal import Decimal
from http import HTTPStatus

import pytest
from django.urls import reverse

from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.payments.choices import EntryTypeChoices
from incienso_shop.apps.payments.exceptions import UnbalancedTransactionError
from incienso_shop.apps.payments.models import LedgerTransaction
from incienso_shop.apps.payments.selectors import PaymentSelector
from incienso_shop.apps.payments.services import PaymentService
from incienso_shop.apps.payments.services import get_or_create_default_chart_of_accounts
from incienso_shop.apps.payments.services import record_double_entry_transaction

pytestmark = pytest.mark.django_db


def test_payment_creation_completion_and_double_entry():
    """Verifica que al completar el pago se genera automáticamente el asiento contable de partida doble."""
    order = Order.objects.create(
        customer_name="Test Buyer",
        customer_email="buyer@example.com",
        customer_phone="12345",
        shipping_address="Av. Siempre Viva 742",
        shipping_city="Springfield",
        total_amount=Decimal("35.00"),
    )

    payment = PaymentService.create_payment_for_order(order, variant="dummy")
    assert payment.total == Decimal("35.00")
    assert payment.currency == "USD"
    assert payment.status == "waiting"

    PaymentService.complete_payment(payment)
    assert payment.status == "confirmed"
    order.refresh_from_db()
    assert order.status == OrderStatusChoices.PAID

    # Verificar el asiento contable generado
    ledger_tx = LedgerTransaction.objects.filter(payment=payment).first()
    assert ledger_tx is not None
    assert ledger_tx.is_balanced
    assert ledger_tx.total_debits == Decimal("35.00")
    assert ledger_tx.total_credits == Decimal("35.00")

    # Verificar líneas contables individuales
    debit_entry = ledger_tx.entries.filter(entry_type=EntryTypeChoices.DEBIT).first()
    credit_entry = ledger_tx.entries.filter(entry_type=EntryTypeChoices.CREDIT).first()

    assert debit_entry.account.code == "1100"  # Pasarelas de Pago por Liquidar
    assert debit_entry.amount == Decimal("35.00")

    assert credit_entry.account.code == "4000"  # Ingresos por Ventas de Inciensos
    assert credit_entry.amount == Decimal("35.00")

    # Verificar Balance de Comprobación
    trial_balance = PaymentSelector.get_trial_balance()
    assert trial_balance["is_balanced"]
    assert trial_balance["grand_total_debits"] == Decimal("35.00")
    assert trial_balance["grand_total_credits"] == Decimal("35.00")


def test_unbalanced_double_entry_raises_error():
    """Comprueba que el sistema rechaza cualquier asiento contable que no cumpla Débito == Crédito."""
    accounts = get_or_create_default_chart_of_accounts()

    with pytest.raises(UnbalancedTransactionError):
        record_double_entry_transaction(
            description="Asiento corrupto desbalanceado",
            entries_data=[
                {
                    "account": accounts["1100"],
                    "entry_type": EntryTypeChoices.DEBIT,
                    "amount": Decimal("100.00"),
                },
                {
                    "account": accounts["4000"],
                    "entry_type": EntryTypeChoices.CREDIT,
                    "amount": Decimal("80.00"),  # No cuadra: 100 != 80
                },
            ],
        )


def test_payment_start_and_success_views(client):
    order = Order.objects.create(
        customer_name="Test Buyer",
        customer_email="buyer@example.com",
        customer_phone="12345",
        shipping_address="Av. Siempre Viva 742",
        shipping_city="Springfield",
        total_amount=Decimal("25.00"),
    )

    start_url = reverse(
        "shop_payments:start_payment",
        kwargs={"order_number": order.order_number},
    )
    resp = client.get(start_url)
    assert resp.status_code == HTTPStatus.OK
    assert "Pasarela de Pago Seguro" in resp.content.decode()

    success_url = reverse(
        "shop_payments:payment_success",
        kwargs={"order_number": order.order_number},
    )
    resp_success = client.post(success_url)
    assert resp_success.status_code == HTTPStatus.OK
    assert "¡Pago Confirmado con Éxito!" in resp_success.content.decode()

    order.refresh_from_db()
    assert order.status == OrderStatusChoices.PAID
