# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render
from orgs.models import Archives
from orgs.authmixins import ArchivistMixin, AccessioningArchivistMixin


class AccessionView(ArchivistMixin, TemplateView):
    template_name = "accession/main.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accessioning Queue'
        context['uploads'] = Archives.objects.filter(process_status=70, organization = self.request.user.organization).order_by('created_time')
        return context

class AccessionRecordView(AccessioningArchivistMixin, TemplateView):
    template_name = "accession/create.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accession Record'
        return context
