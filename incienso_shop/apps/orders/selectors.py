from typing import TYPE_CHECKING

from .models import Cart
from .models import Order

if TYPE_CHECKING:
    import uuid

    from django.db.models import QuerySet
    from django.http import HttpRequest


class CartSelector:
    """Obtención y lectura de carrito actual."""

    @staticmethod
    def get_or_create_cart(request: HttpRequest) -> Cart:
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart

        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart


class OrderSelector:
    """Consultas sobre órdenes."""

    @staticmethod
    def get_by_number(order_number: uuid.UUID | str) -> Order | None:
        return Order.objects.filter(order_number=order_number).prefetch_related("items", "payments").first()

    @staticmethod
    def list_for_user(user) -> QuerySet[Order]:
        return Order.objects.filter(user=user).prefetch_related("items").order_by("-created_at")

    @staticmethod
    def list_all() -> QuerySet[Order]:
        return Order.objects.all().prefetch_related("items").order_by("-created_at")
