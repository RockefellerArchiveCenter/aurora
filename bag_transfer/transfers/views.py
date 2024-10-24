from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, View

from aurora import settings
from bag_transfer.lib.view_helpers import file_size, label_class
from bag_transfer.mixins.authmixins import (LoggedInMixinDefaults,
                                            OrgReadViewMixin)
from bag_transfer.mixins.formatmixins import CSVResponseMixin
from bag_transfer.mixins.viewmixins import BaseDatatableView, PageTitleMixin
from bag_transfer.models import (DashboardMonthData, DashboardRecordTypeData,
                                 Organization, Transfer, User)


class DashboardView(PageTitleMixin, LoggedInMixinDefaults, TemplateView):
    template_name = "transfers/main.html"
    page_title = "Dashboard"

    def org_uploads_by_month(self, orgs):
        """Compiles monthly upload data for a list of organizations."""
        data = {
            "month_labels": [],
            "upload_count_by_month": [],
            "upload_count_by_year": 0,
            "upload_size_by_month": [],
            "upload_size_by_year": 0,
            "record_types_by_year": [],
        }
        today = date.today()
        prev_year = today - relativedelta(years=1)
        while prev_year <= today:
            sort_date = int(str(prev_year.year) + str(prev_year.month))
            if DashboardMonthData.objects.filter(
                organization__in=orgs, sort_date=sort_date
            ).exists():
                month_datas = DashboardMonthData.objects.filter(organization__in=orgs, sort_date=sort_date)
                upload_count = sum(month.upload_count for month in month_datas)
                upload_size = sum(month.upload_size for month in month_datas)
                data["month_labels"].append(str(month_datas[0].month_label))
                data["upload_count_by_month"].append(upload_count)
                data["upload_count_by_year"] += upload_count
                data["upload_size_by_month"].append(upload_size)
                data["upload_size_by_year"] += upload_size
            else:
                data["month_labels"].append(prev_year.strftime("%B"))
                data["upload_count_by_month"].append(0)
                data["upload_size_by_month"].append(0)
            prev_year += relativedelta(months=1)

        for (n, label) in enumerate(set(DashboardRecordTypeData.objects.filter(organization__in=orgs).values_list("label", flat=True))):
            record_type_count = 0
            color_index = n
            while color_index >= len(settings.RECORD_TYPE_COLORS):
                color_index = color_index - len(settings.RECORD_TYPE_COLORS)
            for count in DashboardRecordTypeData.objects.filter(label=label, organization__in=orgs).values_list("count", flat=True):
                record_type_count += count
            if record_type_count > 0:
                data["record_types_by_year"].append(
                    {"label": label, "value": record_type_count, "color": settings.RECORD_TYPE_COLORS[color_index]})
        return data

    def compile_data(self, orgs, org_name, users):
        """Compiles dashboard data for a list of organizations.

        Args:
            orgs (Queryset): list of organizations
            org_name (str): a label for the list of organizations
            users (Queryset): list of users associated with the organizations
        """
        org_uploads = Transfer.objects.filter(process_status__gte=Transfer.TRANSFER_COMPLETED, organization__in=orgs)
        data = {
            "name": org_name,
            "users": users,
            "uploads": org_uploads.order_by("-created_time")[:15],
            "uploads_count": org_uploads.count(),
            "validated_count": org_uploads.filter(process_status__gte=Transfer.VALIDATED).count(),
            "accepted_count": org_uploads.filter(process_status__gte=Transfer.ACCEPTED).count(),
            "accessioned_count": org_uploads.filter(process_status__gte=Transfer.ACCESSIONING_COMPLETE).count(),
        }
        data.update(self.org_uploads_by_month(orgs))
        data["size_trend"] = round((data["upload_size_by_month"][-1] - (data["upload_size_by_year"] / 12)) / 100, 2,)
        data["count_trend"] = round((data["upload_count_by_month"][-1] - (data["upload_count_by_year"] / 12)) / 100, 2,)
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
                    file_size(int(transfer.machine_file_size)),
                    transfer.upload_time_display,
                )
            )
        return self.render_to_csv(data)


class TransferDataTableView(LoggedInMixinDefaults, BaseDatatableView):
    model = Transfer
    columns = [
        "metadata__external_identifier",
        "title",
        "machine_file_identifier",
        "process_status",
        "metadata__date_start",
        "organization__name",
        "metadata__record_creators__name",
        "metadata__record_type",
        "machine_file_size",
        "machine_file_upload_time",
    ]
    order_columns = [
        "title",
        "machine_file_identifier",
        "process_status",
        "metadata__date_start",
        "organization__name",
        "metadata__record_creators__name",
        "metadata__record_type",
        "machine_file_size",
        "machine_file_upload_time",
    ]
    max_display_length = 500

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
                file_size(int(transfer.machine_file_size)),
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
        return context["object"].bag_or_failed_name
