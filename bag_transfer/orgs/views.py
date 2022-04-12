from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from bag_transfer.mixins.authmixins import (ArchivistMixin,
                                            ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import Organization, Transfer


class OrganizationCreateView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = "orgs/create.html"
    page_title = "Add an Organization"
    model = Organization
    fields = ["name", "acquisition_type"]
    success_message = "New Organization Saved!"

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "orgs/detail.html"
    page_title = "Organization Profile"
    model = Organization

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = []
        transfers = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization=context["object"],
        ).order_by("-created_time")[:8]
        for transfer in transfers:
            transfer.bag_info_data = transfer.bag_data
            context["uploads"].append(transfer)
        context["uploads_count"] = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization=context["object"],
        ).count()
        return context


class OrganizationEditView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = "orgs/update.html"
    model = Organization
    fields = ["is_active", "name", "acquisition_type"]
    success_message = "Organization Saved!"

    def get_page_title(self, context):
        return "Edit {}".format(context["object"].name)

    def get_success_url(self):
        return reverse("orgs:detail", kwargs={"pk": self.object.pk})


class OrganizationListView(PageTitleMixin, ArchivistMixin, ListView):
    template_name = "orgs/list.html"
    page_title = "Organizations"
    model = Organization
