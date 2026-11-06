from typing import TYPE_CHECKING

from .models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserSelector:
    @classmethod
    def get_queryset(cls) -> QuerySet[User]:
        return User.objects.prefetch_related("groups").order_by("username")
