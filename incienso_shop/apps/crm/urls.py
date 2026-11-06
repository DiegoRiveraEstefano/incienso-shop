from django.urls import path

from incienso_shop.apps.crm import views

app_name = "crm"

urlpatterns = [
    path("funnel/", views.KanbanCanvasView.as_view(), name="kanban"),
    path("deal/move/", views.MoveDealView.as_view(), name="move_deal"),
    path("segments/", views.CustomerSegmentListView.as_view(), name="segment_list"),
    path("campaigns/", views.EmailCampaignListView.as_view(), name="campaign_list"),
    path("campaigns/<int:pk>/send/", views.SendEmailCampaignView.as_view(), name="send_campaign"),
]
