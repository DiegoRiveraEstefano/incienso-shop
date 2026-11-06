import logging
from typing import TYPE_CHECKING

from django.db import transaction

if TYPE_CHECKING:
    from .models import User

logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    @transaction.atomic
    def update_user_profile(cls, *, user: User, name: str) -> User:
        user.name = name
        user.save(update_fields=["name"])
        logger.info("user_profile_updated", extra={"user_id": user.id})
        return user
