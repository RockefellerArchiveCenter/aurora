# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django_datatables_view.base_datatable_view import BaseDatatableView
from datetime import date
from dateutil import tz
from dateutil.relativedelta import relativedelta

from django.views.generic import TemplateView, View, DetailView
from django.db.models import Sum
from django.db.models.functions import Concat
from django.shortcuts import render
from django.utils.html import escape

from bag_transfer.lib.view_helpers import file_size, label_class
from bag_transfer.models import Archives, Organization, User, BagInfoMetadata, DashboardMonthData, DashboardRecordTypeData
from bag_transfer.rights.models import RightsStatement
from bag_transfer.mixins.authmixins import LoggedInMixinDefaults, OrgReadViewMixin, ArchivistMixin
from bag_transfer.mixins.formatmixins import CSVResponseMixin


class MainView(LoggedInMixinDefaults, TemplateView):
    template_name = "transfers/main.html"

    def get_org_data(self, org, org_name, users):
        data = {}
        data['name'] = org_name
        data['users'] = []
        data['user_uploads'] = []
        for user in users:
            user.uploads = Archives.objects.filter(
                user_uploaded=user,
                process_status__gte=Archives.TRANSFER_COMPLETED).count()
            data['users'].append(user)
        data['uploads'] = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            organization__in=org).order_by('-created_time')[:15]
        data['uploads_count'] = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            organization__in=org).count()
        data['validated_count'] = Archives.objects.filter(
            process_status__gte=Archives.VALIDATED,
            organization__in=org).count()
        data['accepted_count'] = Archives.objects.filter(
            process_status__gte=Archives.ACCEPTED,
            organization__in=org).count()
        data['accessioned_count'] = Archives.objects.filter(
            process_status__gte=Archives.ACCESSIONING_COMPLETE,
            organization__in=org).count()
        data['month_labels'] = []
        data['upload_count_by_month'] = []
        data['upload_count_by_year'] = 0
        data['upload_size_by_month'] = []
        data['upload_size_by_year'] = 0
        data['record_types_by_year'] = []

        today = date.today()
        current = today - relativedelta(years=1)
        colors = ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de',
                  '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de',
                  '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']

        while current <= today:
            sort_date = int(str(current.year)+str(current.month))
            if DashboardMonthData.objects.filter(organization__in=org, sort_date=sort_date).exists():
                upload_count = 0
                upload_size = 0
                for month_data in DashboardMonthData.objects.filter(organization__in=org, sort_date=sort_date):
                    upload_count += month_data.upload_count
                    upload_size += month_data.upload_size
                data['month_labels'].append(str(month_data.month_label))
                data['upload_count_by_month'].append(upload_count)
                data['upload_count_by_year'] += upload_count
                data['upload_size_by_month'].append(upload_size)
                data['upload_size_by_year'] += upload_size
            else:
                data['month_labels'].append(current.strftime("%B"))
                data['upload_count_by_month'].append(0)
                data['upload_size_by_month'].append(0)
            current += relativedelta(months=1)

        for (n, label) in enumerate(set(DashboardRecordTypeData.objects.all().values_list('label', flat=True))):
            record_type_count = 0
            for count in DashboardRecordTypeData.objects.filter(label=label, organization__in=org).values_list('count', flat=True):
                record_type_count += count
            data['record_types_by_year'].append({"label": label, "value": record_type_count, "color": colors[n]})

        data['size_trend'] = round((data['upload_size_by_month'][-1] - (data['upload_size_by_year']/12))/100, 2)
        data['count_trend'] = round((data['upload_count_by_month'][-1] - (data['upload_count_by_year']/12))/100, 2)

        return data

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['data'] = {}
        context['meta_page_title'] = "Dashboard"
        context['sorted_org_list'] = []

        organizations = Organization.objects.all() if (self.request.user.is_archivist()) else Organization.objects.filter(id=self.request.user.organization.pk)

        if self.request.user.is_archivist():
            all_orgs_data = self.get_org_data(organizations, 'All Organizations', User.objects.all())
            context['data']['all_orgs'] = {}
            context['data']['all_orgs'].update(all_orgs_data)
            context['sorted_org_list'].append(['all_orgs', 'All Organizations'])

        user_data = self.get_org_data(Organization.objects.filter(
            id=self.request.user.organization.pk), 'My Transfers',
            User.objects.filter(id=self.request.user.pk))
        context['data'][self.request.user] = {}
        context['data'][self.request.user].update(user_data)
        context['sorted_org_list'].append([self.request.user.username, 'My Transfers'])

        for organization in organizations:
            org_data = self.get_org_data(Organization.objects.filter(
                id=organization.pk), organization.name,
                User.objects.filter(organization=organization))
            context['data'][organization.machine_name] = {}
            context['data'][organization.machine_name].update(org_data)
            context['sorted_org_list'].append([organization.machine_name, organization.name])

        return context


class TransfersView(LoggedInMixinDefaults, View):
    template_name = 'orgs/transfers.html'

    def get(self, request, *args, **kwargs):
        organization = Organization.objects.all() if (self.request.user.is_archivist()) else Organization.objects.filter(id=self.request.user.organization.pk)
        return render(request, self.template_name, {
            'meta_page_title': 'Transfers',
            'org_uploads_count': Archives.objects.filter(
                process_status__gte=Archives.TRANSFER_COMPLETED,
                organization__in=organization).count(),
            'user_uploads_count': Archives.objects.filter(
                process_status__gte=Archives.TRANSFER_COMPLETED,
                organization__in=organization, user_uploaded=request.user).count(),
        })


class TransferDataView(CSVResponseMixin, OrgReadViewMixin, View):
    model = Organization

    def process_status_display(self, status):
        for s in Archives.processing_statuses:
            if s[0] == status:
                return s[1]

    def get(self, request, *args, **kwargs):
        data = [('Bag Name', 'Identifier', 'Status', 'Dates', 'Organization', 'Record Creators', 'Record Type', 'Size', 'Upload Time')]
        if self.request.user.is_archivist:
            transfers = Archives.objects.filter(
                process_status__gte=Archives.TRANSFER_COMPLETED).order_by('-created_time')
        else:
            self.organization = get_object_or_404(Organization, pk=self.kwargs['pk'])
            transfers = Archives.objects.filter(
                process_status__gte=Archives.TRANSFER_COMPLETED,
                organization=self.organization).order_by('-created_time')
        for transfer in transfers:
            dates = ''
            creators = ''
            upload_time = transfer.machine_file_upload_time.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M:%S %p')
            bag_info_data = transfer.get_bag_data()
            if bag_info_data:
                dates = "{} - {}".format(
                    bag_info_data.get('date_start').strftime('%b %e, %Y'),
                    bag_info_data.get('date_end').strftime('%b %e, %Y'))
                creators = (', ').join(bag_info_data.get('record_creators'))

            data.append((
                transfer.bag_or_failed_name(),
                transfer.machine_file_identifier,
                self.process_status_display(transfer.process_status),
                dates,
                transfer.organization.name,
                creators,
                bag_info_data.get('record_type'),
                file_size(int(transfer.machine_file_size)),
                upload_time))
        return self.render_to_csv(data)


class TransferDataTableView(LoggedInMixinDefaults, BaseDatatableView):
    model = Archives
    columns = ['metadata__external_identifier', 'title', 'machine_file_identifier', 'process_status', 'metadata__date_start',
               'organization__name', 'metadata__record_creators__name',
               'metadata__record_type', 'machine_file_size', 'machine_file_upload_time',]
    order_columns = ['title', 'machine_file_identifier', 'process_status', 'metadata__date_start',
                     'organization__name', 'metadata__record_creators__name',
                     'metadata__record_type', 'machine_file_size', 'machine_file_upload_time']
    max_display_length = 500

    def get_filter_method(self): return self.FILTER_ICONTAINS

    def process_status_display(self, status):
        for s in Archives.processing_statuses:
            if s[0] == status:
                return s[1]

    def process_status_tag(self, status):
        percentage = int(round(status/Archives.ACCESSIONING_COMPLETE * 100))
        return "{label} <div class='progress progress-xs'>\
                    <div class='progress-bar progress-bar-{label_class}' style='width: {percentage}%' aria-label='{percentage}% complete'></div>\
                </div>".format(label=self.process_status_display(status), label_class=label_class(status), percentage=percentage)

    def get_initial_queryset(self):
        organization = Organization.objects.all() if (self.request.user.is_archivist()) else Organization.objects.filter(id=self.request.user.organization.pk)
        if self.request.GET.get('q', None) == 'user':
            return Archives.objects.filter(
                process_status__gte=Archives.TRANSFER_COMPLETED,
                organization__in=organization,
                user_uploaded=self.request.user
                ).annotate(title=Concat('metadata__title', 'bag_it_name'))
        return Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            organization__in=organization
            ).annotate(title=Concat('metadata__title', 'bag_it_name'))

    def prepare_results(self, qs):
        json_data = []
        for transfer in qs:
            dates = ''
            creators = ''
            upload_time = transfer.machine_file_upload_time.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M:%S %p')
            bag_info_data = transfer.get_bag_data()
            if bag_info_data:
                dates = "{} - {}".format(
                    bag_info_data.get('date_start').strftime('%b %e, %Y'),
                    bag_info_data.get('date_end').strftime('%b %e, %Y'))
                creators = ('<br/>').join(bag_info_data.get('record_creators'))
            if self.request.user.is_archivist():
                json_data.append([
                    transfer.bag_or_failed_name(),
                    transfer.machine_file_identifier,
                    self.process_status_tag(transfer.process_status),
                    dates,
                    transfer.organization.name,
                    creators,
                    bag_info_data.get('record_type'),
                    file_size(int(transfer.machine_file_size)),
                    upload_time,
                    "/app/transfers/{}".format(transfer.pk)
                ])
            else:
                json_data.append([
                    transfer.bag_or_failed_name(),
                    transfer.machine_file_identifier,
                    self.process_status_tag(transfer.process_status),
                    dates,
                    creators,
                    bag_info_data.get('record_type'),
                    file_size(int(transfer.machine_file_size)),
                    upload_time,
                    "/app/transfers/{}".format(transfer.pk)
                ])
        return json_data


class TransferDetailView(OrgReadViewMixin, DetailView):
    template_name = 'transfers/detail.html'
    model = Archives

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = self.object.bag_or_failed_name
        context['metadata'] = sorted(self.object.get_bag_data().iteritems())
        return context
