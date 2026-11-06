from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import View

from incienso_shop.apps.products.models import Product
from incienso_shop.apps.reviews.forms import ReviewForm
from incienso_shop.apps.reviews.services import ReviewService


class CreateReviewView(LoginRequiredMixin, View):
    """Guarda o actualiza una valoración para un producto."""

    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        form = ReviewForm(request.POST)
        if form.is_valid():
            ReviewService.create_review(
                product=product,
                user=request.user,
                rating=form.cleaned_data["rating"],
                title=form.cleaned_data["title"],
                comment=form.cleaned_data["comment"],
            )
            messages.success(request, "¡Gracias por compartir tu experiencia olfativa!")
        else:
            messages.error(request, "Hubo un error al guardar tu reseña.")
        return redirect("products:product_detail", slug=product.slug)
