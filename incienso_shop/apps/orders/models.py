import uuid
from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.orders.choices import OrderStatusChoices
from incienso_shop.apps.products.models import Product


class Cart(BaseModel):
    """Carrito de compras del usuario o sesión anónima."""

    session_key = models.CharField(
        _("Clave de Sesión"),
        max_length=40,
        blank=True,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
        verbose_name=_("Usuario"),
    )

    class Meta:
        verbose_name = _("Carrito de Compras")
        verbose_name_plural = _("Carritos de Compras")

    def __str__(self) -> str:
        return f"Carrito #{self.id} ({self.user or self.session_key})"

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self) -> Decimal:
        return sum(item.line_total for item in self.items.all())


class CartItem(BaseModel):
    """Línea de producto dentro del carrito."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Carrito"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Producto"),
    )
    quantity = models.PositiveIntegerField(_("Cantidad"), default=1)

    class Meta:
        verbose_name = _("Ítem del Carrito")
        verbose_name_plural = _("Ítems del Carrito")
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product.name}"

    @property
    def line_total(self) -> Decimal:
        return self.product.price * self.quantity


@auditlog.register()
class Order(BaseModel):
    """Pedido formal de compra registrado en el sistema."""

    order_number = models.UUIDField(
        _("Número de Pedido"),
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name=_("Usuario"),
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING,
        db_index=True,
    )

    # Datos de contacto y entrega
    customer_name = models.CharField(_("Nombre Completo"), max_length=200)
    customer_email = models.EmailField(_("Correo Electrónico"), db_index=True)
    customer_phone = models.CharField(_("Teléfono"), max_length=50)
    shipping_address = models.CharField(_("Dirección de Envío"), max_length=255)
    shipping_city = models.CharField(_("Ciudad / Comuna"), max_length=100)
    shipping_postal_code = models.CharField(
        _("Código Postal"),
        max_length=20,
        blank=True,
    )
    shipping_country = models.CharField(_("País"), max_length=100, default="Chile")
    notes = models.TextField(_("Notas de Entrega / Instrucciones"), blank=True)

    # Importes
    subtotal = models.DecimalField(
        _("Subtotal"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    shipping_cost = models.DecimalField(
        _("Costo de Envío"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    tax_amount = models.DecimalField(
        _("Impuestos"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_amount = models.DecimalField(
        _("Total a Pagar"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Pedido #{str(self.order_number)[:8]} - {self.customer_name}"

    def get_absolute_url(self) -> str:
        return reverse(
            "orders:order_detail",
            kwargs={"order_number": self.order_number},
        )


class OrderItem(BaseModel):
    """Detalle de producto comprado en una orden."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Pedido"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_("Producto"),
    )
    product_name = models.CharField(_("Nombre del Incienso"), max_length=255)
    unit_price = models.DecimalField(
        _("Precio Unitario"),
        max_digits=10,
        decimal_places=2,
    )
    quantity = models.PositiveIntegerField(_("Cantidad"), default=1)
    line_total = models.DecimalField(_("Total Línea"), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("Ítem del Pedido")
        verbose_name_plural = _("Ítems del Pedido")

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_name}"
