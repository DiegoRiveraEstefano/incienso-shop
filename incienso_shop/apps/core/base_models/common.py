from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Abstract base model with creation and update timestamps."""

    created_at = models.DateTimeField(
        _("Creado el"),
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        _("Actualizado el"),
        auto_now=True,
    )

    class Meta:
        abstract = True


class MetadataModelMixin(models.Model):
    """Abstract mixin providing flexible JSON metadata field and helper methods."""

    metadata = models.JSONField(
        _("Metadatos adicionales"),
        default=dict,
        blank=True,
    )

    class Meta:
        abstract = True

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Safely retrieve a value from the JSON metadata dictionary."""
        if not isinstance(self.metadata, dict):
            return default
        return self.metadata.get(key, default)

    def set_metadata(self, key: str, value: Any, *, commit: bool = False) -> None:
        """Set a key-value pair in the JSON metadata dictionary."""
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
        if commit and self.pk:
            self.save(update_fields=["metadata"])

    def remove_metadata(self, key: str, *, commit: bool = False) -> None:
        """Remove a key from the JSON metadata dictionary if present."""
        if isinstance(self.metadata, dict) and key in self.metadata:
            del self.metadata[key]
            if commit and self.pk:
                self.save(update_fields=["metadata"])


class MonetaryModelMixin(models.Model):
    """Abstract mixin providing monetary amount and currency code with validation."""

    amount = models.DecimalField(
        _("Monto"),
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    currency = models.CharField(
        _("Moneda"),
        max_length=3,
        default="USD",
    )

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="%(app_label)s_%(class)s_amount_gte_0",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.amount is not None and self.amount < Decimal("0.00"):
            raise ValidationError(
                {"amount": _("El monto no puede ser negativo.")},
            )


class DateRangeModelMixin(models.Model):
    """Abstract mixin providing start and end date range with integrity validation."""

    start_date = models.DateField(
        _("Fecha de Inicio"),
        null=True,
        blank=True,
    )
    end_date = models.DateField(
        _("Fecha de Término"),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__isnull=True)
                    | models.Q(end_date__gte=models.F("start_date"))
                ),
                name="%(app_label)s_%(class)s_end_date_gte_start_date",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {
                    "end_date": _(
                        "La fecha de término no puede ser anterior a la de inicio.",
                    ),
                },
            )

    @property
    def is_currently_active(self) -> bool:
        """Return True if today is within start_date and end_date (inclusive)."""
        today = timezone.localdate()
        if self.start_date and today < self.start_date:
            return False
        return not (self.end_date and today > self.end_date)
