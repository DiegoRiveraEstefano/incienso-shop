from django.urls import path

from .views import AddToCartView
from .views import CartDetailView
from .views import CheckoutView
from .views import OrderDetailView
from .views import OrderListView
from .views import RemoveFromCartView

app_name = "orders"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="cart_detail"),
    path("cart/add/<int:product_id>/", AddToCartView.as_view(), name="cart_add"),
    path(
        "cart/remove/<int:product_id>/",
        RemoveFromCartView.as_view(),
        name="cart_remove",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("my-orders/", OrderListView.as_view(), name="order_list"),
    path("<uuid:order_number>/", OrderDetailView.as_view(), name="order_detail"),
]
