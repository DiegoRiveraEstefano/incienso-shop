from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control text-center"}),
    )


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label="Nombre Completo", max_length=200)
    customer_email = forms.EmailField(label="Correo Electrónico")
    customer_phone = forms.CharField(label="Teléfono Móvil", max_length=50)
    shipping_address = forms.CharField(label="Dirección de Entrega", max_length=255)
    shipping_city = forms.CharField(label="Ciudad / Comuna", max_length=100)
    shipping_postal_code = forms.CharField(
        label="Código Postal",
        max_length=20,
        required=False,
    )
    notes = forms.CharField(
        label="Instrucciones para la entrega",
        widget=forms.Textarea(attrs={"rows": 2}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                "submit",
                "Confirmar y Proceder al Pago",
                css_class="btn-primary btn-lg w-100",
            ),
        )
