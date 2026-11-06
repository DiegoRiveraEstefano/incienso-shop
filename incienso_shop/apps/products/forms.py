from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "category",
            "aroma_family",
            "product_format",
            "origin_country",
            "burn_time_minutes",
            "pieces_count",
            "price",
            "compare_at_price",
            "stock",
            "is_featured",
            "is_active",
            "description",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Guardar Producto", css_class="btn-primary"),
        )
