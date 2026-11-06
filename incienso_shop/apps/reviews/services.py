from typing import TYPE_CHECKING

from django.db import transaction

from incienso_shop.apps.reviews.models import Review

if TYPE_CHECKING:
    from incienso_shop.apps.products.models import Product


class ReviewService:
    @staticmethod
    @transaction.atomic
    def create_review(
        product: Product,
        user,
        rating: int,
        title: str,
        comment: str,
    ) -> Review:
        review, _created = Review.objects.update_or_create(
            product=product,
            user=user,
            defaults={
                "rating": rating,
                "title": title,
                "comment": comment,
                "is_approved": True,
            },
        )
        return review
