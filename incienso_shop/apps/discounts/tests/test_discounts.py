from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from incienso_shop.apps.discounts.choices import DiscountTypeChoices
from incienso_shop.apps.discounts.exceptions import InvalidCouponError
from incienso_shop.apps.discounts.models import Coupon
from incienso_shop.apps.discounts.models import DiscountRule
from incienso_shop.apps.discounts.services import apply_coupon_to_order
from incienso_shop.apps.discounts.services import calculate_discount_amount
from incienso_shop.apps.discounts.services import validate_coupon_for_checkout
from incienso_shop.apps.orders.models import Order

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        username="incienso_fan",
        email="fan@aromaterapia.example",
        password="ValidPassword123!",
    )


@pytest.fixture
def percent_rule():
    return DiscountRule.objects.create(
        name="15% de Descuento en Aromas",
        discount_type=DiscountTypeChoices.PERCENTAGE,
        value=Decimal("15.00"),
        min_order_amount=Decimal("20.00"),
    )


@pytest.fixture
def coupon(percent_rule):
    return Coupon.objects.create(
        code="AROMA15",
        discount_rule=percent_rule,
        max_uses=10,
        max_uses_per_user=1,
    )


def test_calculate_discount_percentage_and_fixed(percent_rule):
    """Prueba el cálculo matemático de descuento porcentual y monto fijo."""
    # Subtotal 100, 15% = 15.00
    disc = calculate_discount_amount(percent_rule, Decimal("100.00"))
    assert disc == Decimal("15.00")

    # Si no alcanza el mínimo (min=20)
    disc_low = calculate_discount_amount(percent_rule, Decimal("10.00"))
    assert disc_low == Decimal("0.00")

    # Regla de monto fijo
    fixed_rule = DiscountRule.objects.create(
        name="Bono $5000",
        discount_type=DiscountTypeChoices.FIXED_AMOUNT,
        value=Decimal("50.00"),
        min_order_amount=Decimal("100.00"),
    )
    assert calculate_discount_amount(fixed_rule, Decimal("150.00")) == Decimal("50.00")


def test_validate_coupon_success_and_expiry(coupon, user):
    """Comprueba la validación de cupón y el control de fecha de caducidad."""
    disc = validate_coupon_for_checkout(coupon, user, Decimal("50.00"))
    assert disc == Decimal("7.50")

    # Expirar el cupón
    coupon.valid_until = timezone.now() - timedelta(days=1)
    coupon.save()

    with pytest.raises(InvalidCouponError):
        validate_coupon_for_checkout(coupon, user, Decimal("50.00"))


def test_apply_coupon_to_order_and_user_limit(coupon, user):
    """Aplica cupón a pedido y verifica que se bloquee el segundo intento si max_uses_per_user=1."""
    order1 = Order.objects.create(
        user=user,
        customer_name="Comprador Frecuente",
        customer_email="fan@aromaterapia.example",
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )

    usage = apply_coupon_to_order(coupon=coupon, order=order1, user=user)
    assert usage.discount_amount == Decimal("15.00")

    order1.refresh_from_db()
    assert order1.total_amount == Decimal("85.00")

    coupon.refresh_from_db()
    assert coupon.used_count == 1

    # Intentar aplicar nuevamente con el mismo usuario en otra orden
    order2 = Order.objects.create(
        user=user,
        customer_name="Comprador Frecuente",
        customer_email="fan@aromaterapia.example",
        subtotal=Decimal("80.00"),
        total_amount=Decimal("80.00"),
    )
    with pytest.raises(InvalidCouponError):
        apply_coupon_to_order(coupon=coupon, order=order2, user=user)
