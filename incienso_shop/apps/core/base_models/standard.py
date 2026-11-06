from incienso_shop.apps.core.base_models.active import ActiveModelMixin
from incienso_shop.apps.core.base_models.common import BaseModel
from incienso_shop.apps.core.base_models.common import MetadataModelMixin
from incienso_shop.apps.core.base_models.identifiers import UUIDModelMixin


class StandardModel(BaseModel, ActiveModelMixin, MetadataModelMixin):
    """Standard base model combining timestamps, active status, and JSON metadata."""

    class Meta:
        abstract = True


class StandardUUIDModel(
    BaseModel,
    UUIDModelMixin,
    ActiveModelMixin,
    MetadataModelMixin,
):
    """Comprehensive standard model with public UUID, timestamps, and metadata."""

    class Meta:
        abstract = True
