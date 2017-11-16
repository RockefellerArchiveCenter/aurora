# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views import View
from django.shortcuts import render

from orgs.models import Archives

from braces.views import LoginRequiredMixin

class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = '/app'


class OrgTransfersView(LoggedInMixinDefaults, View):
    template_name = 'orgs/guser/detail.html'

    def get(self, request, *args, **kwargs):


        return render(request, self.template_name, {
            'page_title' : 'Organization Transfers',
            'uploads' : Archives.objects.filter(process_status__status_short__gte=20, organization = request.user.organization).order_by('-created_time')[:25],
            'uploads_count' : Archives.objects.filter(process_status__status_short__gte=20, organization = request.user.organization).count()
        })

class MyTransfersView(LoggedInMixinDefaults, View):
    template_name = 'orgs/guser/detail.html'

    def get(self, request, *args, **kwargs):


        return render(request, self.template_name, {
            'page_title' : 'My Transfers',
            'uploads' : Archives.objects.filter(process_status__status_short__gte=20, organization = request.user.organization, user_uploaded=request.user).order_by('-created_time')[:25],
            'uploads_count' : Archives.objects.filter(process_status__status_short__gte=20, organization = request.user.organization,user_uploaded = request.user).count()
        })
