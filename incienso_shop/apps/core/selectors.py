from typing import TYPE_CHECKING

from django.core.cache import cache

from .models import StoreSettings

if TYPE_CHECKING:
    from django.db.models import QuerySet

CACHE_KEY_STORE_SETTINGS = "store_settings_singleton"
CACHE_TTL_STORE_SETTINGS = 60 * 15  # 15 minutes


class StoreSettingsSelector:
    """Read queries for store configuration."""

    @staticmethod
    def get_settings() -> StoreSettings:
        settings_obj = cache.get(CACHE_KEY_STORE_SETTINGS)
        if settings_obj is None:
            settings_obj = StoreSettings.objects.first()
            if settings_obj is None:
                settings_obj = StoreSettings.objects.create()
            cache.set(CACHE_KEY_STORE_SETTINGS, settings_obj, CACHE_TTL_STORE_SETTINGS)
        return settings_obj

    @staticmethod
    def list_settings() -> QuerySet[StoreSettings]:
        return StoreSettings.objects.all().order_by("-created_at")
