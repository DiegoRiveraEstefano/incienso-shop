from django.urls import path

from incienso_shop.apps.shipping import views

app_name = "shipping"

urlpatterns = [
    path("tracking/", views.ShipmentTrackingView.as_view(), name="tracking"),
    path("tracking/<str:tracking_number>/", views.ShipmentTrackingView.as_view(), name="tracking_detail"),
    path("routes/", views.DeliveryRouteListView.as_view(), name="route_list"),
    path("routes/<str:route_code>/", views.DeliveryRouteDetailView.as_view(), name="route_detail"),
]
