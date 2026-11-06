from django.db import models
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.base_models.common import BaseModel


class ActiveQuerySet(models.QuerySet):
    """QuerySet providing filtering by active status."""

    def active(self) -> ActiveQuerySet:
        return self.filter(is_active=True)

    def inactive(self) -> ActiveQuerySet:
        return self.filter(is_active=False)


class ActiveManager(models.Manager.from_queryset(ActiveQuerySet)):
    """Manager supporting .active() and .inactive() querysets."""


class OnlyActiveManager(models.Manager):
    """Manager that restricts queries to active records by default."""

    def get_queryset(self) -> ActiveQuerySet:
        return ActiveQuerySet(self.model, using=self._db).filter(is_active=True)


class ActiveModelMixin(models.Model):
    """Abstract mixin to manage an active boolean status flag and query helpers."""

    is_active = models.BooleanField(
        _("Activo"),
        default=True,
        db_index=True,
    )

    objects = ActiveManager()

    class Meta:
        abstract = True

    def activate(self, *, commit: bool = True) -> None:
        """Mark record as active."""
        self.is_active = True
        if commit and self.pk:
            self.save(update_fields=["is_active"])

    def deactivate(self, *, commit: bool = True) -> None:
        """Mark record as inactive."""
        self.is_active = False
        if commit and self.pk:
            self.save(update_fields=["is_active"])

    def toggle_active(self, *, commit: bool = True) -> None:
        """Toggle active state."""
        self.is_active = not self.is_active
        if commit and self.pk:
            self.save(update_fields=["is_active"])


class ActiveBaseModel(BaseModel, ActiveModelMixin):
    """Base model combining timestamps with active status and ActiveManager."""

    class Meta:
        abstract = True
