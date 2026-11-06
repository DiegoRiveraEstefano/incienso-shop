from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import View

from incienso_shop.apps.shipping.models import DeliveryRoute
from incienso_shop.apps.shipping.selectors import get_active_delivery_routes
from incienso_shop.apps.shipping.selectors import get_shipment_by_tracking


class ShipmentTrackingView(View):
    """Vista de seguimiento y rastreo de envíos (Tracking Portal)."""

    template_name = "shipping/tracking.html"

    def get(self, request, *args, **kwargs):
        tracking_number = kwargs.get("tracking_number") or request.GET.get("tracking")
        shipment = None
        if tracking_number:
            shipment = get_shipment_by_tracking(tracking_number)

        return render(
            request,
            self.template_name,
            {
                "shipment": shipment,
                "tracking_number": tracking_number,
            },
        )


class DeliveryRouteListView(LoginRequiredMixin, ListView):
    """Listado y gestión de hojas de ruta de última milla."""

    model = DeliveryRoute
    template_name = "shipping/route_list.html"
    context_object_name = "routes"

    def get_queryset(self):
        return get_active_delivery_routes()


class DeliveryRouteDetailView(LoginRequiredMixin, DetailView):
    """Detalle de ruta y paradas secuenciales de entrega."""

    model = DeliveryRoute
    template_name = "shipping/route_detail.html"
    context_object_name = "route"
    slug_field = "route_code"
    slug_url_kwarg = "route_code"
