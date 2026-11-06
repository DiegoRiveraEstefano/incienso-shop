from crispy_forms.helper import FormHelper
from django import forms

from .models import ApplicationLogEntry


class ApplicationLogEntryForm(forms.ModelForm):
    class Meta:
        model = ApplicationLogEntry
        fields = [
            "occurred_at",
            "level",
            "logger_name",
            "event_code",
            "message",
            "extra_data",
            "traceback_text",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
