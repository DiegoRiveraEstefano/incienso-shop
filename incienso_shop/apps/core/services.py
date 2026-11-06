from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import transaction

from .selectors import CACHE_KEY_STORE_SETTINGS

if TYPE_CHECKING:
    from .models import StoreSettings


class StoreSettingsService:
    """Business operations and mutations for StoreSettings."""

    @staticmethod
    @transaction.atomic
    def update_settings(settings_instance: StoreSettings, **data) -> StoreSettings:
        for field, value in data.items():
            if hasattr(settings_instance, field):
                setattr(settings_instance, field, value)
        settings_instance.save()
        cache.delete(CACHE_KEY_STORE_SETTINGS)
        return settings_instance
