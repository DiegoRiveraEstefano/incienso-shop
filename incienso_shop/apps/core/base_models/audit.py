from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserTrackingModelMixin(models.Model):
    """Abstract mixin providing foreign keys to the creator and updater users."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name=_("Creado por"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name=_("Actualizado por"),
    )

    class Meta:
        abstract = True

    def set_user_tracking(self, user: Any) -> None:
        """Convenience helper to set created_by on creation and updated_by on update."""
        if not self.created_by:
            self.created_by = user
        self.updated_by = user


class ArchivableQuerySet(models.QuerySet):
    """QuerySet providing filtering by archival status."""

    def archived(self) -> ArchivableQuerySet:
        return self.filter(is_archived=True)

    def not_archived(self) -> ArchivableQuerySet:
        return self.filter(is_archived=False)


class ArchivableManager(models.Manager.from_queryset(ArchivableQuerySet)):
    """Manager supporting .archived() and .not_archived() querysets."""


class ArchivableModelMixin(models.Model):
    """Abstract mixin providing archival state and timestamp."""

    is_archived = models.BooleanField(
        _("Archivado"),
        default=False,
        db_index=True,
    )
    archived_at = models.DateTimeField(
        _("Fecha de Archivo"),
        null=True,
        blank=True,
    )

    objects = ArchivableManager()

    class Meta:
        abstract = True

    def archive(self, *, commit: bool = True) -> None:
        """Mark record as archived."""
        self.is_archived = True
        self.archived_at = timezone.now()
        if commit and self.pk:
            self.save(update_fields=["is_archived", "archived_at"])

    def unarchive(self, *, commit: bool = True) -> None:
        """Unmark record as archived."""
        self.is_archived = False
        self.archived_at = None
        if commit and self.pk:
            self.save(update_fields=["is_archived", "archived_at"])
