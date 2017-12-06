# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from rights.models import *
from rights.forms import *
from orgs.authmixins import *

from django.shortcuts import render, redirect

class RightsCreateView(RACAdminMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

    def get_context_data(self, *args, **kwargs):
        context = super(RightsCreateView, self).get_context_data(**kwargs)
        context['basis_form'] = RightsForm()
        context['copyright_form'] = CopyrightFormSet()
        context['license_form'] = LicenseFormSet()
        context['statute_form'] = StatuteFormSet()
        context['other_form'] = OtherFormSet()
        context['granted_form'] = RightsGrantedFormSet()
        return context

    def post(self, request, *args, **kwargs):
        form = RightsForm(request.POST)
        rights_form = form.save(commit=False)
        rights_form.organization = Organization.objects.get(pk=self.kwargs.get('pk'))
        rights_form.save()
        return redirect('rights-detail', self.kwargs.get('pk'), rights_form.pk )

class RightsDetailView(DetailView):
    template_name = 'rights/detail.html'
    model = RightsStatement

    def get_context_data(self, **kwargs):
        context = super(RightsDetailView, self).get_context_data(**kwargs)
        context['object'] = RightsStatement.objects.get(pk=self.kwargs.get('rights_pk'))
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
