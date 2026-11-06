from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import View

from incienso_shop.apps.crm.models import CustomerSegment
from incienso_shop.apps.crm.models import EmailCampaign
from incienso_shop.apps.crm.models import SalesFunnel
from incienso_shop.apps.crm.selectors import get_all_segments
from incienso_shop.apps.crm.selectors import get_default_sales_funnel
from incienso_shop.apps.crm.selectors import get_funnel_stages_with_deals
from incienso_shop.apps.crm.services import move_deal_stage
from incienso_shop.apps.crm.services import send_email_campaign


class KanbanCanvasView(LoginRequiredMixin, TemplateView):
    """Vista de tablero Canvas / Kanban para el embudo de ventas."""

    template_name = "crm/kanban.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funnel_id = self.request.GET.get("funnel")
        funnel = get_object_or_404(SalesFunnel, id=funnel_id) if funnel_id else get_default_sales_funnel()

        context["current_funnel"] = funnel
        context["all_funnels"] = SalesFunnel.objects.filter(is_active=True)
        if funnel:
            context["stages"] = get_funnel_stages_with_deals(funnel.id)
        else:
            context["stages"] = []
        return context


class MoveDealView(LoginRequiredMixin, View):
    """Endpoint para mover un trato a otra etapa en el tablero Canvas."""

    def post(self, request, *args, **kwargs):
        deal_id = request.POST.get("deal_id")
        stage_id = request.POST.get("stage_id")
        if deal_id and stage_id:
            move_deal_stage(deal_id=int(deal_id), new_stage_id=int(stage_id))
            messages.success(request, "Etapa del trato actualizada correctamente.")

        funnel_id = request.POST.get("funnel_id")
        redirect_url = reverse("crm:kanban")
        if funnel_id:
            redirect_url += f"?funnel={funnel_id}"
        return HttpResponseRedirect(redirect_url)


class CustomerSegmentListView(LoginRequiredMixin, ListView):
    model = CustomerSegment
    template_name = "crm/segment_list.html"
    context_object_name = "segments"

    def get_queryset(self):
        return get_all_segments()


class EmailCampaignListView(LoginRequiredMixin, ListView):
    model = EmailCampaign
    template_name = "crm/campaign_list.html"
    context_object_name = "campaigns"


class SendEmailCampaignView(LoginRequiredMixin, View):
    """Dispara el envío de una campaña de correo a los clientes."""

    def post(self, request, pk, *args, **kwargs):
        campaign = get_object_or_404(EmailCampaign, pk=pk)
        sent_count = send_email_campaign(campaign)
        messages.success(request, f"Campaña '{campaign.title}' enviada a {sent_count} destinatarios.")
        return HttpResponseRedirect(reverse("crm:campaign_list"))
