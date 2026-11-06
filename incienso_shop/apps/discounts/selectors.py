from typing import TYPE_CHECKING
from typing import Any

from incienso_shop.apps.discounts.models import Coupon
from incienso_shop.apps.discounts.models import CouponUsage
from incienso_shop.apps.discounts.models import DiscountRule

if TYPE_CHECKING:
    from django.db.models import QuerySet


def get_valid_coupon_by_code(code: str) -> Coupon | None:
    """Busca un cupón por su código exacto o case-insensitive."""
    coupon = Coupon.objects.filter(code__iexact=code.strip(), is_active=True).select_related("discount_rule").first()
    if coupon and coupon.is_usable:
        return coupon
    return None


def get_user_coupon_usage_count(coupon: Coupon, user: Any) -> int:
    """Retorna cuántas veces un usuario específico ha utilizado este cupón."""
    if not user or not user.is_authenticated:
        return 0
    return CouponUsage.objects.filter(coupon=coupon, user=user).count()


def get_active_discount_rules() -> QuerySet[DiscountRule]:
    return DiscountRule.objects.filter(is_active=True).order_by("name")


def get_active_coupons() -> QuerySet[Coupon]:
    return Coupon.objects.filter(is_active=True).select_related("discount_rule").order_by("-created_at")
