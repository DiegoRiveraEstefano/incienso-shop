from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from taggit.managers import TaggableManager

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.core.base_models import NameSlugDescriptionModel
from incienso_shop.apps.products.choices import AromaFamilyChoices
from incienso_shop.apps.products.choices import ProductFormatChoices


@auditlog.register()
class Category(NameSlugDescriptionModel):
    """Categoría principal de inciensos o accesorios de aromaterapia."""

    icon = models.CharField(
        _("Icono (Bootstrap Icons / FontAwesome)"),
        max_length=50,
        blank=True,
        default="bi-flower1",
    )
    image = models.ImageField(
        _("Imagen de Portada"),
        upload_to="categories/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_("Activa"), default=True, db_index=True)
    sort_order = models.PositiveIntegerField(_("Orden de Visualización"), default=0)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("products:category_detail", kwargs={"slug": self.slug})


@auditlog.register()
class Product(NameSlugDescriptionModel):
    """Producto de incienso artesanal, quemador o accesorio."""

    sku = models.CharField(
        _("SKU / Código Único"),
        max_length=50,
        unique=True,
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Categoría"),
    )
    aroma_family = models.CharField(
        _("Familia Olfativa"),
        max_length=20,
        choices=AromaFamilyChoices.choices,
        default=AromaFamilyChoices.RESINS,
        db_index=True,
    )
    product_format = models.CharField(
        _("Formato del Incienso"),
        max_length=20,
        choices=ProductFormatChoices.choices,
        default=ProductFormatChoices.STICKS,
    )
    origin_country = models.CharField(
        _("País de Origen"),
        max_length=100,
        default="India",
    )
    burn_time_minutes = models.PositiveIntegerField(
        _("Tiempo de Quemado (minutos)"),
        default=45,
    )
    pieces_count = models.PositiveIntegerField(
        _("Cantidad de Unidades por Paquete"),
        default=20,
    )

    price = models.DecimalField(_("Precio de Venta"), max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(
        _("Precio de Comparación (Tachado)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    stock = models.PositiveIntegerField(_("Stock Disponible"), default=10)
    is_featured = models.BooleanField(
        _("Destacado en Portada"),
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(_("Activo para Venta"), default=True, db_index=True)

    tags = TaggableManager(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")
        ordering = ["-is_featured", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=Decimal("0.00")),
                name="check_product_price_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self) -> str:
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def discount_pct(self) -> int:
        if self.compare_at_price and self.compare_at_price > self.price:
            diff = self.compare_at_price - self.price
            return int((diff / self.compare_at_price) * 100)
        return 0

    @property
    def primary_image_url(self) -> str | None:
        first_img = self.images.filter(is_primary=True).first() or self.images.first()
        return first_img.image.url if first_img and first_img.image else None


class ProductImage(BaseModel):
    """Galería de imágenes de un producto."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Producto"),
    )
    image = models.ImageField(_("Archivo de Imagen"), upload_to="products/")
    alt_text = models.CharField(
        _("Texto Alternativo (Accesibilidad)"),
        max_length=255,
        blank=True,
    )
    is_primary = models.BooleanField(_("Imagen Principal"), default=False)
    sort_order = models.PositiveIntegerField(_("Orden"), default=0)

    class Meta:
        verbose_name = _("Imagen de Producto")
        verbose_name_plural = _("Imágenes de Producto")
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"Imagen de {self.product.name} (#{self.id})"
