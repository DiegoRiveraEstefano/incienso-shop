from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Review


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "title",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )
    list_filter = ("rating", "is_verified_purchase", "is_approved", "created_at")
    search_fields = ("product__name", "user__username", "title", "comment")
