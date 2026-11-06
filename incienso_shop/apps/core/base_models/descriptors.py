from django.db import models
from django.utils.translation import gettext_lazy as _


class TitleDescriptionModelMixin(models.Model):
    """Abstract mixin providing title and description fields."""

    title = models.CharField(_("Título"), max_length=255)
    description = models.TextField(_("Descripción"), blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title


class NameDescriptionModelMixin(models.Model):
    """Abstract mixin providing name and description fields."""

    name = models.CharField(_("Nombre"), max_length=255)
    description = models.TextField(_("Descripción"), blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class OrderableModelMixin(models.Model):
    """Abstract mixin providing a sort order field for ordered listings."""

    sort_order = models.PositiveIntegerField(
        _("Orden de Clasificación"),
        default=0,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ["sort_order"]
