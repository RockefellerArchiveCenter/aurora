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

    def get_rights_basis_info(self):
        if self.object.rights_basis == 'Copyright':
            data = RightsStatementCopyright.objects.get(rights_statement=self.object.pk)
        elif self.object.rights_basis == 'License':
            data = RightsStatementLicense.objects.get(rights_statement=self.object.pk)
        elif self.object.rights_basis == 'Statute':
            data = RightsStatementStatute.objects.get(rights_statement=self.object.pk)
        else:
            data = RightsStatementOther.objects.get(rights_statement=self.object.pk)
        return data

    def get_rights_granted_info(self):
        return RightsStatementRightsGranted.objects.filter(rights_statement=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super(RightsDetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = '{} PREMIS rights statement'.format(self.object.organization)
        context['rights_basis_info'] = self.get_rights_basis_info
        context['rights_granted_info'] = self.get_rights_granted_info

        return context

class RightsUpdateView(RACAdminMixin, UpdateView):
    template_name = 'rights/manage.html'
    model = RightsStatement

class RightsDeleteView(RACAdminMixin, DeleteView):
    template_name = 'rights/manage.html'
    model = RightsStatement
