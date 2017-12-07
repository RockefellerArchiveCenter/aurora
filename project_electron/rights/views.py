# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from rights.models import *
from rights.forms import *
from orgs.authmixins import *

from django.shortcuts import render, redirect, render_to_response

class RightsManageView(RACAdminMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

    def get_context_data(self, *args, **kwargs):
        context = super(RightsManageView, self).get_context_data(**kwargs)
        context['basis_form'] = RightsForm()
        context['copyright_form'] = CopyrightFormSet()
        context['license_form'] = LicenseFormSet()
        context['statute_form'] = StatuteFormSet()
        context['other_form'] = OtherFormSet()
        return context

    def post(self, request, *args, **kwargs):
        form = RightsForm(request.POST)
        rights_form = form.save(commit=False)
        rights_form.organization = Organization.objects.get(pk=self.kwargs.get('pk'))
        if rights_form.rights_basis == 'Copyright':
            formset = CopyrightFormSet(request.POST, instance=rights_form)
            formset_key = 'copyright_form'
        elif rights_form.rights_basis == 'License':
            formset = LicenseFormSet(request.POST, instance=rights_form)
            formset_key = 'license_form'
        elif rights_form.rights_basis == 'Statute':
            formset = StatuteFormSet(request.POST, instance=rights_form)
            formset_key = 'statute_form'
        else:
            formset = OtherFormSet(request.POST, instance=rights_form)
            formset_key = 'other_form'
        if formset.is_valid():
            rights_form.save()
            formset.save()
            return redirect('rights-grants', self.kwargs.get('pk'), rights_form.pk)
        else:
            return render(request,'rights/manage.html', {formset_key: formset, 'basis_form': form})

class RightsGrantsManageView(RACAdminMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

    def get_context_data(self, *args, **kwargs):
        context = super(RightsGrantsManageView, self).get_context_data(**kwargs)
        context['granted_formset'] = RightsGrantedFormSet()
        return context

    def post(self, request, *args, **kwargs):
        rights_statement = RightsStatement.objects.get(pk=self.kwargs.get('rights_pk'))
        formset = RightsGrantedFormSet(request.POST, instance=rights_statement)
        if formset.is_valid():
            formset.save()
            return redirect('rights-detail', self.kwargs.get('pk'), self.kwargs.get('rights_pk'))
        else:
            return render(request,'rights/manage.html', {'granted_formset': formset})

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
