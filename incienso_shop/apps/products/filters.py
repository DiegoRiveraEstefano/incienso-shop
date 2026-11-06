import django_filters
from django import forms

from .choices import AromaFamilyChoices
from .choices import ProductFormatChoices
from .models import Category
from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Buscar incienso por nombre...",
                "class": "form-control",
            },
        ),
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        empty_label="Todas las Categorías",
    )
    aroma_family = django_filters.ChoiceFilter(
        choices=AromaFamilyChoices.choices,
        empty_label="Todas las Familias Aromáticas",
    )
    product_format = django_filters.ChoiceFilter(
        choices=ProductFormatChoices.choices,
        empty_label="Todos los Formatos",
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["name", "category", "aroma_family", "product_format"]
