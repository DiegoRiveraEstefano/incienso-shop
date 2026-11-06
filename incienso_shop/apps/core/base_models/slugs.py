from typing import Any

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from incienso_shop.apps.core.base_models.common import BaseModel
from incienso_shop.apps.core.base_models.descriptors import NameDescriptionModelMixin
from incienso_shop.apps.core.base_models.descriptors import TitleDescriptionModelMixin


class SluggedModelMixin(models.Model):
    """Abstract mixin providing a unique slug field and automatic generation logic."""

    slug_source_field: str = "title"

    slug = models.SlugField(
        _("Slug"),
        max_length=150,
        unique=True,
        db_index=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if not self.slug:
            self.slug = self.generate_unique_slug()

    def get_slug_source(self) -> str:
        """Retrieve the source string used to build the slug."""
        source_val = getattr(self, self.slug_source_field, None)
        if source_val:
            return str(source_val)
        return ""

    def generate_unique_slug(self) -> str:
        """Generate a unique slug checking for collisions against existing records."""
        base_slug = slugify(self.get_slug_source()) or "item"
        slug_candidate = base_slug[:140]

        model_cls = self.__class__
        qs = model_cls._default_manager.all()  # noqa: SLF001
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if not qs.filter(slug=slug_candidate).exists():
            return slug_candidate

        counter = 2
        while qs.filter(slug=f"{slug_candidate[:140]}-{counter}").exists():
            counter += 1

        return f"{slug_candidate[:140]}-{counter}"


class TitleSlugDescriptionModel(
    TitleDescriptionModelMixin,
    SluggedModelMixin,
    BaseModel,
):
    """Base model combining title, description, unique slug, and timestamps."""

    slug_source_field: str = "title"

    class Meta:
        abstract = True


class NameSlugDescriptionModel(
    NameDescriptionModelMixin,
    SluggedModelMixin,
    BaseModel,
):
    """Base model combining name, description, unique slug, and timestamps."""

    slug_source_field: str = "name"

    class Meta:
        abstract = True
