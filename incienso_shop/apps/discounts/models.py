from decimal import Decimal

from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.discounts.choices import DiscountTypeChoices
from incienso_shop.apps.orders.models import Order
from incienso_shop.apps.products.models import Category


@auditlog.register()
class DiscountRule(BaseModel):
    """Regla o política de descuento comercial."""

    name = models.CharField(_("Nombre de la Regla"), max_length=150)
    discount_type = models.CharField(
        _("Tipo de Descuento"),
        max_length=20,
        choices=DiscountTypeChoices.choices,
        default=DiscountTypeChoices.PERCENTAGE,
    )
    value = models.DecimalField(
        _("Valor (Porcentaje o Monto Fijo)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Ejemplo: 10 para 10% o 5000 para $5000 fijos."),
    )
    min_order_amount = models.DecimalField(
        _("Monto Mínimo de Pedido Requerido"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    target_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="discount_rules",
        verbose_name=_("Categoría Específica (Opcional)"),
    )
    is_active = models.BooleanField(_("Activa"), default=True, db_index=True)
    valid_from = models.DateTimeField(_("Válido Desde"), default=timezone.now)
    valid_until = models.DateTimeField(_("Válido Hasta"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Regla de Descuento")
        verbose_name_plural = _("Reglas de Descuento")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.discount_type == DiscountTypeChoices.PERCENTAGE:
            return f"{self.name} ({self.value}%)"
        return f"{self.name} (${self.value})"

    @property
    def is_currently_valid(self) -> bool:
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        return not (self.valid_until and now > self.valid_until)


@auditlog.register()
class Coupon(BaseModel):
    """Cupón alfanumérico canjeable en el carrito o checkout."""

    code = models.CharField(_("Código de Cupón"), max_length=50, unique=True, db_index=True)
    description = models.CharField(_("Descripción"), max_length=255, blank=True)
    discount_rule = models.ForeignKey(
        DiscountRule,
        on_delete=models.PROTECT,
        related_name="coupons",
        verbose_name=_("Regla de Descuento"),
    )
    max_uses = models.PositiveIntegerField(
        _("Límite Global de Usos"),
        default=100,
        help_text=_("0 para ilimitado."),
    )
    max_uses_per_user = models.PositiveIntegerField(_("Límite de Usos por Cliente"), default=1)
    used_count = models.PositiveIntegerField(_("Cantidad de Usos Efectivos"), default=0)
    is_active = models.BooleanField(_("Activo"), default=True, db_index=True)
    valid_from = models.DateTimeField(_("Válido Desde"), default=timezone.now)
    valid_until = models.DateTimeField(_("Válido Hasta"), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Cupón de Descuento")
        verbose_name_plural = _("Cupones de Descuento")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.code} - {self.discount_rule}"

    @property
    def is_usable(self) -> bool:
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return self.discount_rule.is_currently_valid


@auditlog.register()
class CouponUsage(BaseModel):
    """Registro inmutable de cada canje de cupón por un usuario y pedido."""

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name=_("Cupón"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coupon_usages",
        verbose_name=_("Usuario"),
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
        verbose_name=_("Pedido"),
    )
    discount_amount = models.DecimalField(_("Monto Descontado"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Uso de Cupón")
        verbose_name_plural = _("Usos de Cupones")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.coupon.code} en {self.order} (-${self.discount_amount})"
