# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView, UpdateView, CreateView, DetailView, View

from orgs.models import Organization, User
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.messages.views import SuccessMessageMixin

from braces import views

from orgs.models import Archives

from django.contrib import messages

class LoggedInMixinDefaults(views.LoginRequiredMixin):
    login_url = '/login'

class OrganizationCreateView(LoggedInMixinDefaults, CreateView):
    template_name = 'orgs/create.html'
    model = Organization
    fields = ['name']
class OrganizationDetailView(DetailView):
    template_name = 'orgs/detail.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        print context
        context['uploads'] = Archives.objects.filter(organization = context['object']).order_by('-pk')
        return context

class OrganizationEditView(UpdateView):
    template_name = 'orgs/update.html'
    model =         Organization
    fields =        ['is_active','name','machine_name']

class OrganizationListView(LoggedInMixinDefaults, ListView):

    template_name = 'orgs/list.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class UsersListView(ListView):
    template_name = 'orgs/users/list.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()

        refresh_ldap = User.refresh_ldap_accounts()
        if refresh_ldap:
            messages.info(self.request, '{} new accounts were just synced!'.format(refresh_ldap))

        context['users_list'] = [{'org' : {}, 'users' : []}]
        page_type = self.kwargs.get('page_type',None)
        if page_type:
            if page_type == 'company':
                context['users_list'] = Organization.users_by_org()
            elif page_type == 'unassigned':
                context['users_list'][0]['org'] = {'pass':'pass'}
                context['users_list'][0]['users'] = User.objects.filter(from_ldap=True,is_new_account=True).order_by('username')
        else:
            context['users_list'][0]['org'] = {'pass':'pass'}
            context['users_list'][0]['users'] = User.objects.all().order_by('username') 
        context['page_type'] = page_type

        return context

class UsersCreateView(CreateView):
    template_name = 'orgs/users/create.html'
    model = User
    fields = ['username','is_machine_account','email','organization']

class UsersEditView(SuccessMessageMixin, UpdateView):
    template_name = 'orgs/users/update.html'
    model = User
    fields = ['is_active','email','organization']
    success_url = '/app/users/'
    success_message = "saved!"