from django.urls import path

from incienso_shop.apps.analytics import views

app_name = "analytics"

urlpatterns = [
    path("dashboard/", views.AnalyticsDashboardView.as_view(), name="dashboard"),
]
