# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from rights.models import *
from rights.forms import *
from orgs.authmixins import *

from django.shortcuts import render

class RightsCreateView(RACAdminMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

    def get_context_data(self, *args, **kwargs):
        context = super(RightsCreateView, self).get_context_data(**kwargs)
        self.object = None
        form_class = self.get_form_class()
        context['basis_form'] = self.get_form(form_class)
        context['copyright_form'] = CopyrightFormSet()
        context['license_form'] = LicenseFormSet()
        context['statute_form'] = StatuteFormSet()
        context['other_form'] = OtherFormSet()
        context['granted_form'] = RightsGrantedFormSet()
        return context

class RightsDetailView(RACAdminMixin, DetailView):
    template_name = 'rights/detail.html'
    model = RightsStatement

class RightsUpdateView(RACAdminMixin, UpdateView):
    template_name = 'rights/manage.html'
    model = RightsStatement

class RightsDeleteView(RACAdminMixin, DeleteView):
    template_name = 'rights/manage.html'
    model = RightsStatement
