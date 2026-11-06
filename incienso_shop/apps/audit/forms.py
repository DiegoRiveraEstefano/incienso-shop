from crispy_forms.helper import FormHelper
from django import forms

from .models import AuditEvent


class AuditEventForm(forms.ModelForm):
    class Meta:
        model = AuditEvent
        fields = [
            "actor",
            "action",
            "content_type",
            "object_pk",
            "object_repr",
            "remote_addr",
            "additional_data",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
