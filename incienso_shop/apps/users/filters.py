import django_filters

from .models import User


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains", label="Usuario")
    name = django_filters.CharFilter(lookup_expr="icontains", label="Nombre")

    class Meta:
        model = User
        fields = ["username", "name", "is_staff", "is_active"]
