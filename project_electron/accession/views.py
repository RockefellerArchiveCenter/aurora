# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render
from orgs.authmixins import RACUserMixin


class AccessionView(RACUserMixin, TemplateView):
    template_name = "accession/main.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accessioning Queue'
        context['uploads'] = Archives.objects.filter(process_status__status_short=70, organization = self.request.user.organization).order_by('created_time')

class AccessionRecordView(RACUserMixin, TemplateView):
    template_name = "accession/create.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accession Record'
