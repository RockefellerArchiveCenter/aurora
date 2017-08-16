# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView

from orgs.models import Organization
from django.utils import timezone

class OrganizationListView(ListView):
    
    template_name = 'orgs/list.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context