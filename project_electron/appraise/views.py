# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render


class AppraiseView(TemplateView):
    template_name = "appraise/main.html"

    def get_context_data(self, **kwargs):
        context = super(AppraiseView, self).get_context_data(**kwargs)
        context['uploads'] = Archives.objects.filter(process_status__status_short=40, organization = context['object']).order_by('created_time')
        return context
