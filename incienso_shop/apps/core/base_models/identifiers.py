import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.base_models.common import BaseModel


class UUIDModelMixin(models.Model):
    """Abstract mixin providing a public, immutable UUID identifier."""

    uuid = models.UUIDField(
        _("Identificador UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class UUIDPrimaryKeyModelMixin(models.Model):
    """Abstract mixin providing a UUID primary key."""

    id = models.UUIDField(
        _("Identificador"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class UUIDBaseModel(BaseModel, UUIDModelMixin):
    """Base model combining timestamps with a public UUID field."""

    class Meta:
        abstract = True
