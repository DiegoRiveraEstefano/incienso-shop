from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

from incienso_shop.apps.core.exceptions import BusinessLogicError
from incienso_shop.apps.core.selectors import StoreSettingsSelector
from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.orders.models import Cart
from incienso_shop.apps.orders.models import CartItem
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.orders.models import OrderItem
from incienso_shop.apps.products.services import ProductService

if TYPE_CHECKING:
    from incienso_shop.apps.products.models import Product


class CartService:
    """Mutaciones sobre el carrito."""

    @staticmethod
    @transaction.atomic
    def add_product(cart: Cart, product: Product, quantity: int = 1) -> CartItem:
        if product.stock < quantity:
            msg = f"No hay suficiente stock disponible para {product.name}."
            raise BusinessLogicError(
                msg,
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])
        return item

    @staticmethod
    @transaction.atomic
    def remove_item(cart: Cart, product_id: int) -> None:
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

    @staticmethod
    @transaction.atomic
    def clear_cart(cart: Cart) -> None:
        cart.items.all().delete()


class OrderService:
    """Servicio para creación y transición de órdenes."""

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart: Cart, customer_data: dict, user=None) -> Order:
        items = list(cart.items.select_related("product"))
        if not items:
            msg = "El carrito está vacío. Agrega inciensos antes de continuar."
            raise BusinessLogicError(
                msg,
            )

        store_settings = StoreSettingsSelector.get_settings()
        subtotal = cart.subtotal

        # Calcular envío
        if subtotal >= store_settings.free_shipping_threshold:
            shipping_cost = Decimal("0.00")
        else:
            shipping_cost = store_settings.standard_shipping_cost

        # Calcular impuesto
        tax_amount = (subtotal * store_settings.tax_rate_pct) / Decimal("100.00")
        total_amount = subtotal + shipping_cost + tax_amount

        order = Order.objects.create(
            user=user if (user and user.is_authenticated) else None,
            customer_name=customer_data["customer_name"],
            customer_email=customer_data["customer_email"],
            customer_phone=customer_data["customer_phone"],
            shipping_address=customer_data["shipping_address"],
            shipping_city=customer_data["shipping_city"],
            shipping_postal_code=customer_data.get("shipping_postal_code", ""),
            shipping_country=customer_data.get("shipping_country", "Chile"),
            notes=customer_data.get("notes", ""),
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=OrderStatusChoices.PENDING,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                line_total=item.line_total,
            )
            # Reservar stock
            ProductService.adjust_stock(item.product, -item.quantity)

        # Vaciar carrito
        CartService.clear_cart(cart)
        return order

    @staticmethod
    @transaction.atomic
    def mark_as_paid(order: Order) -> Order:
        order.status = OrderStatusChoices.PAID
        order.save(update_fields=["status", "updated_at"])
        return order
