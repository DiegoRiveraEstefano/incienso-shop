from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import StoreSettings


class StoreSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = [
            "store_name",
            "tagline",
            "contact_email",
            "contact_phone",
            "currency",
            "free_shipping_threshold",
            "standard_shipping_cost",
            "tax_rate_pct",
            "allow_guest_checkout",
            "maintenance_mode",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Guardar Configuración", css_class="btn-primary"),
        )
