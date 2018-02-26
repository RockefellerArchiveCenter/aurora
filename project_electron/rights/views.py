# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from django.views.generic import CreateView, UpdateView, DetailView, TemplateView

from rights.models import *
from rights.forms import *
from orgs.authmixins import *
from transfer_app.mixins import JSONResponseMixin

from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from orgs.authmixins import OrgReadViewMixin

class RightsManageView(ManagingArchivistMixin, CreateView):
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
        if self.kwargs.get('pk'):
            rights_statement = RightsStatement.objects.get(pk=self.kwargs.get('pk'))
            context['basis_form'] = RightsForm(instance=rights_statement)
            context['organization'] = Organization.objects.get(pk=rights_statement.organization.pk)
            if rights_statement.rights_basis == 'Copyright':
                context['copyright_form'] = CopyrightFormSet(instance=rights_statement)
            elif rights_statement.rights_basis == 'License':
                context['license_form'] = LicenseFormSet(instance=rights_statement)
            elif rights_statement.rights_basis == 'Statute':
                context['Statute'] = StatuteFormSet(instance=rights_statement)
            else:
                context['other_form'] = OtherFormSet(instance=rights_statement)
        else:
            context['organization'] = Organization.objects.get(pk=self.request.GET.get('org'))
        return context

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            rights_statement = RightsStatement.objects.get(pk=self.kwargs.get('pk'))
            form = RightsForm(request.POST, instance=rights_statement)
        else:
            form = RightsForm(request.POST)
            rights_statement = form.save(commit=False)
            rights_statement.organization = Organization.objects.get(pk=request.GET.get('org'))

        if rights_statement.rights_basis == 'Copyright':
            formset = CopyrightFormSet(request.POST, instance=rights_statement)
            formset_key = 'copyright_form'
        elif rights_statement.rights_basis == 'License':
            formset = LicenseFormSet(request.POST, instance=rights_statement)
            formset_key = 'license_form'
        elif rights_statement.rights_basis == 'Statute':
            formset = StatuteFormSet(request.POST, instance=rights_statement)
            formset_key = 'statute_form'
        else:
            formset = OtherFormSet(request.POST, instance=rights_statement)
            formset_key = 'other_form'
        if formset.is_valid():
            rights_statement.save()
            formset.save()
            return redirect('rights-grants', rights_statement.pk)
        else:
            return render(request,'rights/manage.html', {formset_key: formset, 'basis_form': form})

class RightsAPIAdminView(ManagingArchivistMixin, JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        resp = {'success': 0}

        if 'action' in self.kwargs:
            obj = get_object_or_404(RightsStatement,pk=context['pk'])
            if self.kwargs['action'] == 'delete':
                obj.delete()
                resp['success'] = 1


        return self.render_to_json_response(resp, **kwargs)

class RightsGrantsManageView(ManagingArchivistMixin, CreateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
    form_class = RightsForm

    def get_context_data(self, *args, **kwargs):
        context = super(RightsGrantsManageView, self).get_context_data(**kwargs)
        if self.kwargs.get('pk'):
            instance = RightsStatement.objects.get(pk=self.kwargs.get('pk'))
        context['granted_formset'] = RightsGrantedFormSet(instance=instance)
        context['rights_statement'] = RightsStatement.objects.get(pk=self.kwargs.get('pk'))
        context['rights_basis_info'] = context['rights_statement'].get_rights_info_object
        context['organization'] = context['rights_statement'].organization
        return context

    def post(self, request, *args, **kwargs):
        rights_statement = RightsStatement.objects.get(pk=self.kwargs.get('pk'))
        formset = RightsGrantedFormSet(request.POST, instance=rights_statement)
        if formset.is_valid():
            formset.save()
            return redirect('rights-detail', self.kwargs.get('pk'))
        else:
            return render(request,'rights/manage.html', {'granted_formset': formset})

class RightsDetailView(OrgReadViewMixin, DetailView):
    template_name = 'rights/detail.html'
    model = RightsStatement
    pk_url_kwarg = 'rights_pk'

    def get_context_data(self, *args, **kwargs):
        context = super(RightsDetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = '{} PREMIS rights statement'.format(self.object.organization)
        context['rights_basis_info'] = context['object'].get_rights_info_object
        context['rights_granted_info'] = context['object'].get_rights_granted_objects
        return context

class RightsUpdateView(ManagingArchivistMixin, UpdateView):
    template_name = 'rights/manage.html'
    model = RightsStatement
