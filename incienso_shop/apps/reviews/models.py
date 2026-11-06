from auditlog.registry import auditlog
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from incienso_shop.apps.core.base_models import BaseModel
from incienso_shop.apps.products.models import Product


@auditlog.register()
class Review(BaseModel):
    """Reseña y calificación de un incienso dejado por un comprador."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Producto"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Usuario"),
    )
    rating = models.PositiveSmallIntegerField(
        _("Calificación (1 a 5)"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
    )
    title = models.CharField(_("Título de la Reseña"), max_length=150)
    comment = models.TextField(_("Comentario y Experiencia Olfativa"))
    is_verified_purchase = models.BooleanField(_("Compra Verificada"), default=False)
    is_approved = models.BooleanField(_("Aprobado para Publicación"), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Reseña")
        verbose_name_plural = _("Reseñas")
        ordering = ["-created_at"]
        unique_together = ("product", "user")

    def __str__(self) -> str:
        return f"{self.rating}★ - {self.title} por {self.user}"
