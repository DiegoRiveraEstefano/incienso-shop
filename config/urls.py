from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

from incienso_shop.apps.core.views import AboutView
from incienso_shop.apps.core.views import HomeDashboardView

urlpatterns = [
    path("", HomeDashboardView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path("admin/dj-cache-panel/", include("dj_cache_panel.urls")),
    path("admin/dj-urls-panel/", include("dj_urls_panel.urls")),
    path("admin/dj_signals_panel/", include("dj_signals_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
    # User & Access management
    path("users/", include("incienso_shop.apps.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # E-commerce Core & Business Domain Apps
    path("core/", include("incienso_shop.apps.core.urls", namespace="core")),
    path(
        "products/",
        include("incienso_shop.apps.products.urls", namespace="products"),
    ),
    path("orders/", include("incienso_shop.apps.orders.urls", namespace="orders")),
    # Advanced E-commerce & Operations Modules
    path("suppliers/", include("incienso_shop.apps.suppliers.urls", namespace="suppliers")),
    path("inventory/", include("incienso_shop.apps.inventory.urls", namespace="inventory")),
    path("discounts/", include("incienso_shop.apps.discounts.urls", namespace="discounts")),
    path("crm/", include("incienso_shop.apps.crm.urls", namespace="crm")),
    path("shipping/", include("incienso_shop.apps.shipping.urls", namespace="shipping")),
    path("analytics/", include("incienso_shop.apps.analytics.urls", namespace="analytics")),
    # django-payments built-in endpoints and custom payments views
    path("payments/", include("payments.urls")),
    path(
        "checkout-payments/",
        include("incienso_shop.apps.payments.urls", namespace="shop_payments"),
    ),
    path("reviews/", include("incienso_shop.apps.reviews.urls", namespace="reviews")),
    # Data Pipeline & Operations Apps
    path("audit/", include("incienso_shop.apps.audit.urls", namespace="audit")),
    path("logs/", include("incienso_shop.apps.logs.urls", namespace="logs")),
    path("monitor/", include("incienso_shop.apps.monitor.urls", namespace="monitor")),
    path("backups/", include("incienso_shop.apps.backups.urls", namespace="backups")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    path("api/", include("config.api_router")),
    path("api/auth-token/", obtain_auth_token, name="obtain_auth_token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
