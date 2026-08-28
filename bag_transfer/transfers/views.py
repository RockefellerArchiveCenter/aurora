from django.db.models import Sum
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, View

from bag_transfer.lib.view_helpers import file_size, label_class
from bag_transfer.mixins.authmixins import (LoggedInMixinDefaults,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import CSVResponseMixin
from bag_transfer.mixins.viewmixins import BaseDatatableView, PageTitleMixin
from bag_transfer.models import Organization, Transfer, User


class DashboardView(PageTitleMixin, LoggedInMixinDefaults, TemplateView):
    template_name = "transfers/main.html"
    page_title = "Dashboard"

    def get_upload_size(self, queryset):
        return file_size(queryset.aggregate(Sum('machine_file_size'))['machine_file_size__sum'] or 0)

    def compile_data(self, orgs, org_name, users):
        """Compiles dashboard data for a list of organizations.

        Args:
            orgs (Queryset): list of organizations
            org_name (str): a label for the list of organizations
            users (Queryset): list of users associated with the organizations
        """
        org_uploads = Transfer.objects.filter(process_status__gte=Transfer.TRANSFER_COMPLETED, organization__in=orgs)
        validated_uploads = org_uploads.filter(process_status__gte=Transfer.VALIDATED)
        accepted_uploads = org_uploads.filter(process_status__gte=Transfer.ACCEPTED)
        accessioned_uploads = org_uploads.filter(process_status__gte=Transfer.ACCESSIONING_COMPLETE)

        data = {
            "name": org_name,
            "users": users,
            "uploads": org_uploads.order_by("-created_time")[:10],
            "uploads_count": org_uploads.count(),
            "validated_count": validated_uploads.count(),
            "accepted_count": accepted_uploads.count(),
            "accessioned_count": accessioned_uploads.count(),
            "uploads_size": self.get_upload_size(org_uploads),
            "validated_size": self.get_upload_size(validated_uploads),
            "accepted_size": self.get_upload_size(accepted_uploads),
            "accessioned_size": self.get_upload_size(accessioned_uploads),
        }

        return data

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context["data"] = {}
        context["sorted_org_list"] = []

        organizations = (
            Organization.objects.all() if (self.request.user.is_archivist()) else
            Organization.objects.filter(id=self.request.user.organization.pk))

        if self.request.user.is_archivist():
            all_orgs_data = self.compile_data(organizations, "All Organizations", User.objects.all())
            context["data"]["all_orgs"] = all_orgs_data
            context["sorted_org_list"].append(["all_orgs", "All Organizations"])

        for organization in organizations:
            org_data = self.compile_data(
                Organization.objects.filter(id=organization.pk),
                organization.name,
                User.objects.filter(organization=organization))
            context["data"][organization.machine_name] = org_data
            context["sorted_org_list"].append([organization.machine_name, organization.name])

        return context


class TransfersView(PageTitleMixin, LoggedInMixinDefaults, TemplateView):
    page_title = "Transfers"
    template_name = "orgs/transfers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organizations = (
            Organization.objects.all()
            if (self.request.user.is_archivist())
            else Organization.objects.filter(id=self.request.user.organization.pk))
        transfers = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization__in=organizations)
        context["org_uploads_count"] = transfers.count()
        return context


class TransferDataView(CSVResponseMixin, View):
    model = Transfer
    prefix = 'transfers'

    def process_status_display(self, status):
        for s in Transfer.processing_statuses:
            if s[0] == status:
                return s[1]

    def get_dates(self, bag_info_data):
        return "{} - {}".format(
            bag_info_data.get("date_start").strftime("%b %e, %Y"),
            bag_info_data.get("date_end").strftime("%b %e, %Y")) if bag_info_data else ""

    def get_creators(self, bag_info_data):
        return (", ").join(bag_info_data.get("record_creators")) if bag_info_data else ""

    def get(self, request, *args, **kwargs):
        data = [
            (
                "Bag Name",
                "Identifier",
                "Status",
                "Dates",
                "Organization",
                "Record Creators",
                "Record Type",
                "Size",
                "Upload Time",
            )
        ]
        transfers = Transfer.objects.filter(process_status__gte=Transfer.TRANSFER_COMPLETED)
        if not self.request.user.is_archivist():
            self.organization = get_object_or_404(Organization, pk=self.request.user.organization.pk)
            transfers.filter(organization=self.organization)
        for transfer in transfers.order_by("-created_time"):
            bag_info_data = transfer.bag_data
            data.append(
                (
                    transfer.bag_or_failed_name,
                    transfer.machine_file_identifier,
                    self.process_status_display(transfer.process_status),
                    self.get_dates(bag_info_data),
                    transfer.organization.name,
                    self.get_creators(bag_info_data),
                    bag_info_data.get("record_type"),
                    file_size(transfer.machine_file_size),
                    transfer.upload_time_display,
                )
            )
        return self.render_to_csv(data)


class TransferDataTableView(LoggedInMixinDefaults, BaseDatatableView):
    model = Transfer
    max_display_length: 500

    def get_columns(self):
        columns = [
            "metadata__external_identifier",
            "title",
            "machine_file_identifier",
            "process_status",
            "metadata__date_start",
            "metadata__record_creators__name",
            "metadata__record_type",
            "machine_file_size",
            "machine_file_upload_time",
        ]
        if self.request.user.is_archivist():
            columns.insert(5, "organization__name")
        return columns

    def get_order_columns(self):
        order_columns = [
            "title",
            "machine_file_identifier",
            "process_status",
            "metadata__date_start",
            "metadata__record_creators__name",
            "metadata__record_type",
            "machine_file_size",
            "machine_file_upload_time",
        ]
        if self.request.user.is_archivist():
            order_columns.insert(4, "organization__name")
        return order_columns

    def get_filter_method(self):
        return self.FILTER_ICONTAINS

    def process_status_display(self, status):
        for integer, label in Transfer.processing_statuses:
            if integer == status:
                return label

    def process_status_tag(self, status):
        percentage = int(round(status / Transfer.ACCESSIONING_COMPLETE * 100))
        return "{label} <progress class='progress-bar--{label_class}' max='100' value='{percentage}' aria-label='{percentage}% complete'></progress>".format(
            label=self.process_status_display(status),
            label_class=label_class(status),
            percentage=percentage)

    def get_initial_queryset(self):
        organizations = (
            Organization.objects.all()
            if (self.request.user.is_archivist())
            else Organization.objects.filter(id=self.request.user.organization.pk))
        qs = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            organization__in=organizations).annotate(title=Concat("metadata__title", "bag_it_name"))
        return qs

    def get_dates(self, bag_info_data):
        return "{} - {}".format(
            bag_info_data.get("date_start").strftime("%b %e, %Y"),
            bag_info_data.get("date_end").strftime("%b %e, %Y")) if bag_info_data else ""

    def get_creators(self, bag_info_data):
        return ("<br/>").join(bag_info_data.get("record_creators")) if bag_info_data else ""

    def prepare_results(self, qs):
        json_data = []
        for transfer in qs:
            bag_info_data = transfer.bag_data
            transfer_data = [
                transfer.bag_or_failed_name,
                transfer.machine_file_identifier,
                self.process_status_tag(transfer.process_status),
                self.get_dates(bag_info_data),
                self.get_creators(bag_info_data),
                bag_info_data.get("record_type"),
                file_size(transfer.machine_file_size),
                transfer.upload_time_display,
                "/app/transfers/{}".format(transfer.pk),
            ]
            if self.request.user.is_archivist():
                transfer_data.insert(4, transfer.organization.name)
            json_data.append(transfer_data)
        return json_data


class TransferDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "transfers/detail.html"
    model = Transfer

    def get_page_title(self, context):
        return "Transfer: {}".format(context["object"].bag_or_failed_name)
