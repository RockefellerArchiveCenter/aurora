# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from dateutil.relativedelta import relativedelta
from django.views.generic import TemplateView, View, DetailView

from django.db.models import Sum
from django.shortcuts import render

from bag_transfer.models import Archives, Organization, User, BagInfoMetadata
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
            user.uploads = Archives.objects.filter(user_uploaded=user, process_status__gte=20).count()
            data['users'].append(user)
        data['uploads'] = Archives.objects.filter(process_status__gte=20, organization__in=org).order_by('-created_time')[:15]
        data['uploads_count'] = Archives.objects.filter(process_status__gte=20, organization__in=org).count()
        data['validated_count'] = Archives.objects.filter(process_status__gte=40, organization__in=org).count()
        data['accepted_count'] = Archives.objects.filter(process_status__gte=70, organization__in=org).count()
        data['accessioned_count'] = Archives.objects.filter(process_status__gte=90, organization__in=org).count()
        data['month_labels'] = []
        data['upload_count_by_month'] = []
        data['upload_count_by_year'] = 0
        data['upload_size_by_month'] = []
        data['upload_size_by_year'] = 0
        data['record_types_by_year'] = []

        today = datetime.date.today()
        current = today - relativedelta(years=1)
        year_archives = []
        colors = ['#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de', '#f56954', '#00a65a', '#f39c12', '#00c0ef', '#3c8dbc', '#d2d6de']

        while current <= today:
            data['month_labels'].append(current.strftime("%B"))
            archives = Archives.objects.filter(process_status__gte=20, organization__in=org, machine_file_upload_time__year=current.year, machine_file_upload_time__month=current.month)
            for archive in archives:
                year_archives.append(archive)
            upload_count = archives.count()
            data['upload_count_by_month'].append(upload_count)
            data['upload_count_by_year'] += upload_count
            upload_size = archives.aggregate(Sum('machine_file_size'))
            if upload_size['machine_file_size__sum']:
                data['upload_size_by_month'].append(upload_size['machine_file_size__sum']/1000000)
                data['upload_size_by_year'] += upload_size['machine_file_size__sum']/1000000
            else:
                data['upload_size_by_month'].append(0)
            labels = BagInfoMetadata.objects.filter(archive__in=archives).values_list('record_type', flat=True)
            month_record_types = []
            for (n, label) in enumerate(set(labels)):
                number = BagInfoMetadata.objects.filter(archive__in=archives, record_type=label).count()
                if label in data['record_types_by_year']:
                    dict_index = next((index for (index, d) in enumerate(lst) if d["label"] == label), None)
                    data['record_types_by_year'][dict_index]["value"] += number
                else:
                    data['record_types_by_year'].append({"label": label, "value": number, "color": colors[n]})
            current += relativedelta(months=1)

        data['average_size'] = sum(data['upload_size_by_month'])/len(data['upload_size_by_month'])
        data['average_count'] = sum(data['upload_count_by_month'])/len(data['upload_count_by_month'])
        data['size_trend'] = round((data['upload_size_by_month'][-1] - data['average_size'])/100, 2)
        data['count_trend'] = round((data['upload_count_by_month'][-1] - data['average_count'])/100, 2)

        return data

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['data'] = {}
        context['meta_page_title'] = "Dashboard"
        context['sorted_org_list'] = []

        if self.request.user.is_archivist():
            organizations = Organization.objects.all()
            all_orgs_data = self.get_org_data(organizations, 'All Organizations', User.objects.all())
            context['data']['all_orgs'] = {}
            context['data']['all_orgs'].update(all_orgs_data)
            context['sorted_org_list'].append(['all_orgs', 'All Organizations'])
        else:
            organizations = Organization.objects.filter(id=self.request.user.organization.pk)

        user_data = self.get_org_data(Organization.objects.filter(id=self.request.user.organization.pk), 'My Transfers', User.objects.filter(id=self.request.user.pk))
        context['data'][self.request.user] = {}
        context['data'][self.request.user].update(user_data)
        context['sorted_org_list'].append([self.request.user.username, 'My Transfers'])

        for organization in organizations:
            org_data = self.get_org_data(Organization.objects.filter(id=organization.pk), organization.name, User.objects.filter(organization=organization))
            context['data'][organization.machine_name] = {}
            context['data'][organization.machine_name].update(org_data)
            context['sorted_org_list'].append([organization.machine_name, organization.name])

        return context


class TransfersView(LoggedInMixinDefaults, View):
    template_name = 'orgs/transfers.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_archivist():
            organization = Organization.objects.all()
        else:
            organization = Organization.objects.filter(id=self.request.user.organization.pk)
        org_archives = Archives.objects.filter(process_status__gte=20, organization__in=organization).order_by('-created_time')
        for archive in org_archives:
            archive.bag_info_data = archive.get_bag_data()
        user_archives = Archives.objects.filter(process_status__gte=20, organization__in=organization, user_uploaded=request.user).order_by('-created_time')
        for archive in user_archives:
            archive.bag_info_data = archive.get_bag_data()
        return render(request, self.template_name, {
            'meta_page_title': 'Transfers',
            'org_uploads': org_archives,
            'org_uploads_count': Archives.objects.filter(process_status__gte=20, organization__in=organization).count(),
            'user_uploads': user_archives,
            'user_uploads_count': Archives.objects.filter(process_status__gte=20, organization__in=organization, user_uploaded=request.user).count(),
        })


class TransferDataView(CSVResponseMixin, OrgReadViewMixin, View):
    model = Organization

    def get(self, request, *args, **kwargs):
        data = [('Bag Name','Status','Size','Upload Time','Errors')]
        if self.request.user.is_archivist:
            transfers = Archives.objects.filter(process_status__gte=20).order_by('-created_time')
        else:
            self.organization = get_object_or_404(Organization, pk=self.kwargs['pk'])
            transfers = Archives.objects.filter(process_status__gte=20, organization=self.organization).order_by('-created_time')
        for transfer in transfers:
            transfer_errors = transfer.get_errors()
            errors = (', '.join([e.code.code_desc for e in transfer_errors]) if transfer_errors else '')

            data.append((
                transfer.bag_or_failed_name(),
                transfer.process_status,
                transfer.organization,
                transfer.machine_file_size,
                transfer.machine_file_upload_time,
                errors))
        return self.render_to_csv(data)


class TransferDetailView(OrgReadViewMixin, DetailView):
    template_name = 'transfers/transfer_detail.html'
    model = Archives

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = self.object.bag_or_failed_name
        return context
