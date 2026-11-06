import django_tables2 as tables

from .models import User


class UserTable(tables.Table):
    username = tables.Column(linkify=True)

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap5.html"
        fields = ("username", "name", "email", "is_staff", "is_active", "date_joined")
        attrs = {"class": "table table-hover table-striped align-middle mb-0"}
