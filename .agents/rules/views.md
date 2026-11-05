---
trigger: always_on
---

# Incienso Shop: Views & Controllers Guidelines

## Core Principles

1. **Thin Class-Based Views (CBVs) with Native Django Permissions**:
   - Views act strictly as HTTP orchestrators.
   - Responsibilities: validate authentication (`LoginRequiredMixin`) and native Django permissions (`PermissionRequiredMixin`), apply filters (`FilterView`), render tables (`SingleTableMixin`), call `Service` or `Selector`, and return response.
2. **Leverage `django-tables2` and `django-filter`**:
   - List views MUST combine `SingleTableMixin` (from `django_tables2`) and `FilterView` (from `django_filters.views`) rather than implementing manual sorting, pagination, or `request.GET` filtering.
3. **Zero Business Logic in Views**:
   - Never write database mutations directly in `form_valid()`, `post()`, or wizard `done()`.
   - Always delegate mutations to the corresponding `Service` classmethod.
4. **Multi-Step Workflows with `django-formtools` (`SessionWizardView`)**:
   - Any flow requiring more than one sequential step (e.g. Creator Onboarding, Campaign Setup, Settlement Approval, Batch Import Mapping) MUST use `formtools.wizard.views.SessionWizardView` rather than ad-hoc session dictionaries, cookie hacks, or monolithic single-page forms.
   - All state is maintained securely in the Django session backend.
   - The final consolidation happens strictly in `done()`, which extracts cleaned data and delegates the multi-step transaction to a single atomic `Service` method.

## Canonical CBV Pattern

```python
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import StreamingSessionFilter
from .forms import StreamingSessionForm
from .models import StreamingSession
from .selectors import StreamingSessionSelector
from .services import StreamingSessionService
from .tables import StreamingSessionTable


class StreamingSessionListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleTableMixin,
    FilterView,
):
    model = StreamingSession
    permission_required = "streams.view_streamingsession"
    table_class = StreamingSessionTable
    filterset_class = StreamingSessionFilter
    template_name = "streams/session_list.html"
    paginate_by = 25

    def get_queryset(self):
        return StreamingSessionSelector.get_visible_queryset(user=self.request.user)


class StreamingSessionCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = StreamingSession
    permission_required = "streams.add_streamingsession"
    form_class = StreamingSessionForm
    template_name = "streams/session_form.html"
    success_url = reverse_lazy("streams:list")

    def form_valid(self, form):
        self.object = StreamingSessionService.record_session(
            creator_id=form.cleaned_data["creator"].id,
            channel_id=form.cleaned_data["channel"].id if form.cleaned_data.get("channel") else None,
            session_title=form.cleaned_data["session_title"],
            game_or_category=form.cleaned_data["game_or_category"],
            platform=form.cleaned_data["platform"],
            streamed_at=form.cleaned_data["streamed_at"],
            duration_seconds=form.cleaned_data["duration_seconds"],
            peak_viewers=form.cleaned_data["peak_viewers"],
            avg_ccv=form.cleaned_data["avg_ccv"],
            ad_revenue=form.cleaned_data["ad_revenue"],
            subs_revenue=form.cleaned_data["subs_revenue"],
            donations_revenue=form.cleaned_data["donations_revenue"],
        )
        messages.success(self.request, "Sesión de streaming registrada exitosamente.")
        return redirect(self.success_url)
```

## Canonical Multi-Step Wizard Pattern (`django-formtools`)

When implementing multi-step processes, subclass `SessionWizardView` combined with permission mixins:

```python
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from formtools.wizard.views import SessionWizardView

from .forms import (
    CreatorProfileStepForm,
    CreatorChannelsStepForm,
    CreatorContractStepForm,
)
from .services import CreatorOnboardingService

FORMS = [
    ("profile", CreatorProfileStepForm),
    ("channels", CreatorChannelsStepForm),
    ("contract", CreatorContractStepForm),
]

TEMPLATES = {
    "profile": "creators/wizards/onboarding_step_profile.html",
    "channels": "creators/wizards/onboarding_step_channels.html",
    "contract": "creators/wizards/onboarding_step_contract.html",
}


class CreatorOnboardingWizardView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SessionWizardView,
):
    form_list = FORMS
    permission_required = "creators.add_creator"

    def get_template_names(self) -> list[str]:
        return [TEMPLATES.get(self.steps.current, "creators/wizards/wizard_base.html")]

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        # Pass contextual information (such as user or request) if required by form
        kwargs["user"] = self.request.user
        return kwargs

    def done(self, form_list, **kwargs) -> HttpResponse:
        # Extract validated cleaned data from all steps
        profile_data = self.get_cleaned_data_for_step("profile") or {}
        channels_data = self.get_cleaned_data_for_step("channels") or {}
        contract_data = self.get_cleaned_data_for_step("contract") or {}

        # Delegate the entire transaction to the Service layer
        creator = CreatorOnboardingService.onboard_creator(
            user=self.request.user,
            profile_payload=profile_data,
            channels_payload=channels_data.get("channels", []),
            contract_payload=contract_data,
        )

        messages.success(
            self.request,
            f"Creador '{creator.display_name}' incorporado exitosamente.",
        )
        return redirect(reverse_lazy("creators:detail", kwargs={"pk": creator.pk}))
```
