from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.base_models.common import BaseModel


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet providing soft delete, restore, and filtering operations."""

    def delete(self) -> tuple[int, dict[str, int]]:
        """Soft delete all matching records."""
        count = self.update(is_deleted=True, deleted_at=timezone.now())
        return count, {self.model._meta.label: count}  # noqa: SLF001

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Permanently delete matching records from the database."""
        return super().delete()

    def restore(self) -> int:
        """Restore all soft-deleted records in this queryset."""
        return self.update(is_deleted=False, deleted_at=None)

    def deleted(self) -> SoftDeleteQuerySet:
        """Filter only soft-deleted records."""
        return self.filter(is_deleted=True)

    def active(self) -> SoftDeleteQuerySet:
        """Filter active records if model has is_active field."""
        return self.filter(is_active=True)

    def inactive(self) -> SoftDeleteQuerySet:
        """Filter inactive records if model has is_active field."""
        return self.filter(is_active=False)


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records by default."""

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self) -> SoftDeleteQuerySet:
        """Return all records including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted(self) -> SoftDeleteQuerySet:
        """Return only soft-deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)

    def active(self) -> SoftDeleteQuerySet:
        """Return active, non-deleted records."""
        return self.get_queryset().active()

    def inactive(self) -> SoftDeleteQuerySet:
        """Return inactive, non-deleted records."""
        return self.get_queryset().inactive()

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Permanently delete non-deleted records in manager scope."""
        return self.get_queryset().hard_delete()

    def restore(self) -> int:
        """Restore non-deleted records in manager scope."""
        return self.get_queryset().restore()


class SoftDeletableModelMixin(models.Model):
    """Abstract mixin to support soft-deletion of records."""

    is_deleted = models.BooleanField(
        _("Eliminado"),
        default=False,
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        _("Fecha de Eliminación"),
        null=True,
        blank=True,
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # noqa: DJ012

    class Meta:
        abstract = True

    def delete(
        self,
        using: Any = None,
        keep_parents: bool = False,  # noqa: FBT001, FBT002
        *,
        soft: bool = True,
    ) -> tuple[int, dict[str, int]]:
        """Soft delete by default, or permanently delete if soft=False."""
        if not soft:
            return super().delete(using=using, keep_parents=keep_parents)
        if self.pk is None:
            return 0, {self._meta.label: 0}
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
        return 1, {self._meta.label: 1}

    def restore(self, *, commit: bool = True) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        if commit and self.pk:
            self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(
        self,
        using: Any = None,
        keep_parents: bool = False,  # noqa: FBT001, FBT002
    ) -> tuple[int, dict[str, int]]:
        """Permanently delete this instance from the database."""
        return super().delete(using=using, keep_parents=keep_parents)


class SoftDeleteBaseModel(BaseModel, SoftDeletableModelMixin):
    """Base model combining timestamps with soft delete capabilities."""

    class Meta:
        abstract = True
