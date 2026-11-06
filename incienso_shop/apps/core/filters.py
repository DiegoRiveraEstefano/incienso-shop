import django_filters

from .models import StoreSettings


class StoreSettingsFilter(django_filters.FilterSet):
    class Meta:
        model = StoreSettings
        fields = {
            "store_name": ["icontains"],
            "currency": ["exact"],
            "maintenance_mode": ["exact"],
        }
