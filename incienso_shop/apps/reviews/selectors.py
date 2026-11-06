from django.db.models import Avg
from django.db.models import QuerySet

from .models import Review


class ReviewSelector:
    @staticmethod
    def list_for_product(product) -> QuerySet[Review]:
        return Review.objects.filter(product=product, is_approved=True).select_related("user").order_by("-created_at")

    @staticmethod
    def get_product_rating_summary(product) -> dict:
        qs = Review.objects.filter(product=product, is_approved=True)
        avg = qs.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0.0
        count = qs.count()
        return {
            "average": round(float(avg), 1),
            "count": count,
        }
