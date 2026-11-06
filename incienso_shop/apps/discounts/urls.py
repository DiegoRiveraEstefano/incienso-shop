from django.urls import path

from incienso_shop.apps.discounts import views

app_name = "discounts"

urlpatterns = [
    path("coupons/", views.CouponListView.as_view(), name="coupon_list"),
    path("rules/", views.DiscountRuleListView.as_view(), name="rule_list"),
]
