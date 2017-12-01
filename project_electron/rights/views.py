# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from orgs.models import Organization
from rights.forms import RightsForm
from orgs.authmixins import *

from django.shortcuts import render

class RightsCreateView(RACAdminMixin, CreateView):
    template_name = 'orgs/rights/manage.html'
    model = Organization
    form_class = RightsForm

class RightsDetailView(RACAdminMixin, DetailView):
    template_name = 'orgs/rights/detail.html'

class RightsUpdateView(RACAdminMixin, UpdateView):
    template_name = 'orgs/rights/manage.html'

class RightsDeleteView(RACAdminMixin, DeleteView):
    template_name = 'orgs/rights/manage.html'
