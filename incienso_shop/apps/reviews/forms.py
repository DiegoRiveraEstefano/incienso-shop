from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} Estrellas") for i in range(5, 0, -1)],
            ),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Publicar Valoración", css_class="btn-primary"),
        )
