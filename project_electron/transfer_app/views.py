# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from dateutil.relativedelta import relativedelta
from django.views.generic import TemplateView

from django.db.models import Sum
from django.shortcuts import render
from orgs.models import Archives
from orgs.authmixins import LoggedInMixinDefaults

class MainView(LoggedInMixinDefaults, TemplateView):
    template_name = "transfer_app/main.html"


    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        context['uploads'] = Archives.objects.filter(process_status=99, organization = self.request.user.organization).order_by('-created_time')[:15]
        context['uploads_count'] = Archives.objects.filter(process_status=99, organization = self.request.user.organization).count()
        context['month_labels'] = []
        context['upload_count_by_month'] = []
        context['upload_size_by_month'] = []

        today = datetime.date.today()
        current = today - relativedelta(years=1)

        while current <= today:
            context['month_labels'].append(current.strftime("%B"))
            upload_count = Archives.objects.filter(process_status=99, organization=self.request.user.organization, machine_file_upload_time__year=current.year, machine_file_upload_time__month=current.month).count()
            context['upload_count_by_month'].append(upload_count)
            upload_size = Archives.objects.filter(process_status=99, organization = self.request.user.organization, machine_file_upload_time__year=current.year, machine_file_upload_time__month=current.month).aggregate(Sum('machine_file_size'))
            if upload_size['machine_file_size__sum']:
                context['upload_size_by_month'].append(upload_size['machine_file_size__sum']/1000000000)
            else:
                context['upload_size_by_month'].append(0)
            current += relativedelta(months=1)

        context['average_size'] = sum(context['upload_size_by_month'])/len(context['upload_size_by_month'])
        context['average_count'] = sum(context['upload_count_by_month'])/len(context['upload_count_by_month'])
        return context
