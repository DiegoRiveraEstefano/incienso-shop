from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.suppliers.choices import PurchaseOrderStatusChoices


@auditlog.register()
class Supplier(BaseModel):
    """Proveedor artesanal o mayorista de inciensos y materias primas."""

    name = models.CharField(_("Razón Social / Nombre"), max_length=200, unique=True)
    contact_name = models.CharField(_("Persona de Contacto"), max_length=150, blank=True)
    email = models.EmailField(_("Correo Electrónico"), blank=True)
    phone = models.CharField(_("Teléfono de Contacto"), max_length=50, blank=True)
    address = models.CharField(_("Dirección Fiscal / Bodega"), max_length=255, blank=True)
    country = models.CharField(_("País de Origen"), max_length=100, default="Chile")
    tax_id = models.CharField(_("RUT / NIF / Identificación Fiscal"), max_length=50, blank=True)
    lead_time_days = models.PositiveIntegerField(_("Tiempo de Entrega Promedio (Días)"), default=7)
    notes = models.TextField(_("Notas del Proveedor"), blank=True)
    is_active = models.BooleanField(_("Activo"), default=True, db_index=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Proveedor")
        verbose_name_plural = _("Proveedores")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


@auditlog.register()
class PurchaseOrder(BaseModel):
    """Orden de compra formal emitida a un proveedor."""

    po_number = models.CharField(_("Número de Orden de Compra"), max_length=50, unique=True, db_index=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name=_("Proveedor"),
    )
    status = models.CharField(
        _("Estado"),
        max_length=20,
        choices=PurchaseOrderStatusChoices.choices,
        default=PurchaseOrderStatusChoices.DRAFT,
        db_index=True,
    )
    order_date = models.DateField(_("Fecha de Emisión"), default=timezone.now)
    expected_delivery_date = models.DateField(_("Fecha Estimada de Entrega"), null=True, blank=True)
    notes = models.TextField(_("Condiciones y Observaciones"), blank=True)
    total_amount = models.DecimalField(
        _("Monto Total de Compra"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Orden de Compra a Proveedor")
        verbose_name_plural = _("Órdenes de Compra a Proveedores")
        ordering = ["-order_date", "-id"]

    def __str__(self) -> str:
        return f"{self.po_number} - {self.supplier.name} ({self.get_status_display()})"


@auditlog.register()
class PurchaseOrderItem(BaseModel):
    """Ítem específico en una orden de compra a proveedor."""

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Orden de Compra"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_items",
        verbose_name=_("Producto"),
    )
    quantity_ordered = models.PositiveIntegerField(_("Cantidad Solicitada"), default=1)
    quantity_received = models.PositiveIntegerField(_("Cantidad Recibida"), default=0)
    unit_cost = models.DecimalField(_("Costo Unitario de Compra"), max_digits=10, decimal_places=2)
    line_total = models.DecimalField(_("Total Línea"), max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = _("Ítem de Orden de Compra")
        verbose_name_plural = _("Ítems de Orden de Compra")

    def __str__(self) -> str:
        return f"{self.quantity_ordered}x {self.product.name} ({self.purchase_order.po_number})"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_cost * self.quantity_ordered
        super().save(*args, **kwargs)
