# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, View, DetailView

from django.shortcuts import render
from orgs.models import Archives
from orgs.authmixins import LoggedInMixinDefaults

class MainView(LoggedInMixinDefaults, TemplateView):
    template_name = "transfer_app/main.html"


    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)

        context['uploads'] = Archives.objects.filter(organization = self.request.user.organization).order_by('-created_time')[:15]
        context['uploads_count'] = Archives.objects.filter(organization = self.request.user.organization).count()
        return context

class RecentTransfersView(LoggedInMixinDefaults, View):
    template_name = 'orgs/recent_transfers.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'page_title' : 'Organization Transfers',
            'org_uploads' : Archives.objects.filter(organization = request.user.organization).order_by('-created_time')[:25],
            'org_uploads_count' : Archives.objects.filter(organization = request.user.organization).count(),
            'user_uploads' : Archives.objects.filter(organization = request.user.organization, user_uploaded=request.user).order_by('-created_time')[:25],
            'user_uploads_count' : Archives.objects.filter(organization = request.user.organization, user_uploaded = request.user).count(),
        })

class TransferDetailView(DetailView):
    template_name = 'transfer_app/transfer_detail.html'
    model = Archives
