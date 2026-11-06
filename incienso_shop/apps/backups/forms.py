from crispy_forms.helper import FormHelper
from django import forms

from .models import DatabaseBackup


class DatabaseBackupForm(forms.ModelForm):
    class Meta:
        model = DatabaseBackup
        fields = [
            "backup_name",
            "file_path",
            "file_size_bytes",
            "checksum_sha256",
            "status",
            "is_compressed",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
