import django_filters

from .choices import OrderStatusChoices
from .models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=OrderStatusChoices.choices,
        empty_label="Todos los Estados",
    )
    customer_email = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Order
        fields = ["status", "customer_email"]
