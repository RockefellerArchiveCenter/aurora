# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from rights.models import *
from rights.forms import RightsForm
from orgs.authmixins import *

from django.shortcuts import render

class RightsCreateView(RACAdminMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

class RightsDetailView(RACAdminMixin, DetailView):
    template_name = 'rights/detail.html'
    model = RightsStatement

    def get_context_data(self, **kwargs):
        context = super(RightsDetailView, self).get_context_data(**kwargs)
        context['object'] = RightsStatement.objects.get(pk=self.object.pk)
        context['meta_page_title'] = '{} PREMIS rights statement'.format(self.object.organization)
        context['rights_basis_info'] = context['object'].get_rights_info_object
        context['rights_granted_info'] = context['object'].get_rights_granted_objects
        return context

class RightsUpdateView(RACAdminMixin, UpdateView):
    template_name = 'rights/manage.html'
    model = RightsStatement

class RightsDeleteView(RACAdminMixin, DeleteView):
    template_name = 'rights/manage.html'
    model = RightsStatement
