from crispy_forms.helper import FormHelper
from django import forms

from .models import InstanceHealthCheck


class InstanceHealthCheckForm(forms.ModelForm):
    class Meta:
        model = InstanceHealthCheck
        fields = [
            "status",
            "sqlite_journal_mode",
            "sqlite_db_size_mb",
            "sqlite_wal_size_mb",
            "diskcache_size_mb",
            "active_db_connections",
            "response_time_ms",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
