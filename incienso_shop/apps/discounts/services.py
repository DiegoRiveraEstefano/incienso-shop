from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any

from django.db import transaction

from incienso_shop.apps.discounts.choices import DiscountTypeChoices
from incienso_shop.apps.discounts.exceptions import InvalidCouponError
from incienso_shop.apps.discounts.models import Coupon
from incienso_shop.apps.discounts.models import CouponUsage
from incienso_shop.apps.discounts.models import DiscountRule
from incienso_shop.apps.discounts.selectors import get_user_coupon_usage_count

if TYPE_CHECKING:
    from incienso_shop.apps.orders.models import Order


def calculate_discount_amount(
    rule: DiscountRule,
    subtotal: Decimal,
) -> Decimal:
    """Calcula el monto monetario a descontar según la regla configurada."""
    if subtotal < rule.min_order_amount:
        return Decimal("0.00")

    if rule.discount_type == DiscountTypeChoices.PERCENTAGE:
        pct = rule.value / Decimal("100")
        raw_discount = subtotal * pct
        return min(raw_discount.quantize(Decimal("0.01")), subtotal)

    if rule.discount_type == DiscountTypeChoices.FIXED_AMOUNT:
        return min(rule.value, subtotal)

    return Decimal("0.00")


def validate_coupon_for_checkout(
    coupon: Coupon,
    user: Any,
    subtotal: Decimal,
) -> Decimal:
    """
    Valida vigencia, límites globales y por usuario, y retorna el descuento aplicable.
    Lanza InvalidCouponError si no cumple con las restricciones.
    """
    if not coupon.is_usable:
        msg = "El cupón ha expirado, está inactivo o superó su límite de usos."
        raise InvalidCouponError(msg)

    if coupon.discount_rule.min_order_amount > subtotal:
        msg = f"El cupón requiere un monto mínimo de compra de ${coupon.discount_rule.min_order_amount}."
        raise InvalidCouponError(
            msg,
        )

    if user and user.is_authenticated:
        user_usages = get_user_coupon_usage_count(coupon, user)
        if user_usages >= coupon.max_uses_per_user:
            msg = "Ya has alcanzado el límite máximo de usos permitido para este cupón."
            raise InvalidCouponError(msg)

    return calculate_discount_amount(coupon.discount_rule, subtotal)


@transaction.atomic
def apply_coupon_to_order(
    *,
    coupon: Coupon,
    order: Order,
    user: Any = None,
) -> CouponUsage:
    """Aplica formalmente el cupón al pedido e incrementa el contador de usos."""
    discount = validate_coupon_for_checkout(coupon, user, order.subtotal)

    # Actualizar contador del cupón
    coupon.used_count += 1
    coupon.save(update_fields=["used_count"])

    # Aplicar descuento al total del pedido
    order.total_amount = max(Decimal("0.00"), order.total_amount - discount)
    order.save(update_fields=["total_amount"])

    return CouponUsage.objects.create(
        coupon=coupon,
        user=user if (user and user.is_authenticated) else order.user,
        order=order,
        discount_amount=discount,
    )
