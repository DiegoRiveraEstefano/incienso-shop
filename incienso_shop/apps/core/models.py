from decimal import Decimal

from auditlog.registry import auditlog
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.core.choices import CurrencyChoices


@auditlog.register()
class StoreSettings(BaseModel):
    """Configuración general y parámetros comerciales de la tienda de inciensos."""

    store_name = models.CharField(
        _("Nombre de la Tienda"),
        max_length=200,
        default="Incienso Shop Artesanal",
    )
    tagline = models.CharField(
        _("Eslogan / Subtítulo"),
        max_length=255,
        default="Aromas sagrados y resinas naturales para tu espacio",
    )
    contact_email = models.EmailField(
        _("Email de Contacto"),
        default="contacto@inciensoshop.example.com",
    )
    contact_phone = models.CharField(
        _("Teléfono de Contacto"),
        max_length=50,
        blank=True,
        default="+56 9 1234 5678",
    )
    currency = models.CharField(
        _("Moneda por Defecto"),
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD,
    )
    free_shipping_threshold = models.DecimalField(
        _("Monto Mínimo Envío Gratis"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("50.00"),
    )
    standard_shipping_cost = models.DecimalField(
        _("Costo Envío Estándar"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("4.99"),
    )
    tax_rate_pct = models.DecimalField(
        _("Tasa de Impuesto IVA (%)"),
        max_digits=5,
        decimal_places=2,
        default=Decimal("19.00"),
    )
    allow_guest_checkout = models.BooleanField(
        _("Permitir Compra como Invitado"),
        default=True,
    )
    maintenance_mode = models.BooleanField(
        _("Modo Mantenimiento"),
        default=False,
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Configuración de la Tienda")
        verbose_name_plural = _("Configuraciones de la Tienda")

    def __str__(self) -> str:
        return self.store_name

    def get_absolute_url(self) -> str:
        return reverse("core:settings_detail", kwargs={"pk": self.pk})
