# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render


class AccessionView(TemplateView):
    template_name = "accession/main.html"

    def get_context_data(self, **kwargs):
        context = super(AccessionView, self).get_context_data(**kwargs)
        context['uploads'] = Archives.objects.filter(process_status=70, organization = context['object']).order_by('created_time')
        return context
