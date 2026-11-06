from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from incienso_shop.apps.discounts.models import Coupon
from incienso_shop.apps.discounts.models import DiscountRule
from incienso_shop.apps.discounts.selectors import get_active_coupons
from incienso_shop.apps.discounts.selectors import get_active_discount_rules


class CouponListView(LoginRequiredMixin, ListView):
    model = Coupon
    template_name = "discounts/coupon_list.html"
    context_object_name = "coupons"

    def get_queryset(self):
        return get_active_coupons()


class DiscountRuleListView(LoginRequiredMixin, ListView):
    model = DiscountRule
    template_name = "discounts/rule_list.html"
    context_object_name = "rules"

    def get_queryset(self):
        return get_active_discount_rules()
