from auditlog.registry import auditlog
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.inventory.choices import MovementTypeChoices
from incienso_shop.apps.products.models import Product
from incienso_shop.apps.suppliers.models import PurchaseOrderItem
from incienso_shop.apps.suppliers.models import Supplier


@auditlog.register()
class ProductBatch(BaseModel):
    """Lote de inventario con trazabilidad y soporte de salida FIFO."""

    batch_code = models.CharField(_("Código de Lote"), max_length=100, unique=True, db_index=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="batches",
        verbose_name=_("Producto"),
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplied_batches",
        verbose_name=_("Proveedor de Origen"),
    )
    purchase_order_item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
        verbose_name=_("Ítem de Compra Asociado"),
    )
    initial_quantity = models.PositiveIntegerField(_("Cantidad Inicial"), default=0)
    available_quantity = models.PositiveIntegerField(_("Cantidad Disponible"), default=0, db_index=True)
    unit_cost = models.DecimalField(_("Costo Unitario de Adquisición"), max_digits=10, decimal_places=2)
    received_date = models.DateField(_("Fecha de Ingreso / Recepción"), default=timezone.now, db_index=True)
    expiry_date = models.DateField(_("Fecha de Vencimiento / Caducidad"), null=True, blank=True, db_index=True)
    notes = models.TextField(_("Notas de Calidad / Aroma"), blank=True)
    is_active = models.BooleanField(_("Lote Activo"), default=True, db_index=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Lote de Producto")
        verbose_name_plural = _("Lotes de Producto")
        ordering = ["received_date", "id"]  # Orden natural FIFO
        constraints = [
            models.CheckConstraint(
                condition=models.Q(available_quantity__lte=models.F("initial_quantity")),
                name="check_batch_available_lte_initial",
            ),
        ]

    def __str__(self) -> str:
        return f"Lote {self.batch_code} - {self.product.name} ({self.available_quantity}/{self.initial_quantity})"

    @property
    def is_depleted(self) -> bool:
        return self.available_quantity <= 0


@auditlog.register()
class StockMovement(BaseModel):
    """Registro inmutable de auditoría de cada movimiento de inventario."""

    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.PROTECT,
        related_name="movements",
        verbose_name=_("Lote Afectado"),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_movements",
        verbose_name=_("Producto"),
    )
    movement_type = models.CharField(
        _("Tipo de Movimiento"),
        max_length=20,
        choices=MovementTypeChoices.choices,
        db_index=True,
    )
    quantity = models.IntegerField(_("Cantidad (+/-)"))
    unit_cost = models.DecimalField(_("Costo Unitario del Movimiento"), max_digits=10, decimal_places=2)
    reference_order_number = models.CharField(
        _("Referencia de Orden / Documento"),
        max_length=100,
        blank=True,
        db_index=True,
    )
    notes = models.CharField(_("Motivo / Notas"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Movimiento de Stock")
        verbose_name_plural = _("Movimientos de Stock")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        type_lbl = self.get_movement_type_display()
        return f"{type_lbl}: {self.quantity} un ({self.product.name})"
