from django.urls import path

from .views import CreateReviewView

app_name = "reviews"

urlpatterns = [
    path("add/<slug:product_slug>/", CreateReviewView.as_view(), name="add_review"),
]
