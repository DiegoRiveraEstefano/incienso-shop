from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from incienso_shop.apps.shipping.models import Carrier
from incienso_shop.apps.shipping.models import DeliveryRoute
from incienso_shop.apps.shipping.models import RouteStop
from incienso_shop.apps.shipping.models import Shipment
from incienso_shop.apps.shipping.models import ShipmentEvent


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "vehicle_plate", "is_active")


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 1


@admin.register(Shipment)
class ShipmentAdmin(SimpleHistoryAdmin):
    list_display = ("tracking_number", "order", "carrier", "status", "shipping_city", "estimated_delivery_date")
    list_filter = ("status", "carrier")
    search_fields = ("tracking_number", "order__order_number", "recipient_name")
    inlines = [ShipmentEventInline]


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1


@admin.register(DeliveryRoute)
class DeliveryRouteAdmin(SimpleHistoryAdmin):
    list_display = ("route_code", "carrier", "scheduled_date", "status")
    list_filter = ("status", "scheduled_date")
    inlines = [RouteStopInline]
