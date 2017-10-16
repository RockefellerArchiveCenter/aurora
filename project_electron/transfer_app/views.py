# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render
from orgs.models import Archives
from orgs.authmixins import LoggedInMixinDefaults

class MainView(LoggedInMixinDefaults, TemplateView):
    template_name = "transfer_app/main.html"


    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        context['uploads'] = Archives.objects.filter(process_status=99, organization = self.request.user.organization).order_by('-created_time')[:15]
        context['uploads_count'] = Archives.objects.filter(process_status=99, organization = self.request.user.organization).count()
        return context