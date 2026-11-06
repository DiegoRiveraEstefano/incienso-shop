import django_filters

from .models import ApplicationLogEntry


class ApplicationLogEntryFilter(django_filters.FilterSet):
    class Meta:
        model = ApplicationLogEntry
        fields = ["level", "logger_name", "event_code"]
