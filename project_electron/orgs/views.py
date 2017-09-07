# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView, UpdateView, CreateView

from orgs.models import Organization, User
from django.utils import timezone

class OrganizationListView(ListView):
    
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
        return context


class UsersCreateView(CreateView):
    template_name = 'orgs/users/create.html'
    model = User
    fields = ['username']

class UsersEditView(UpdateView):
    template_name = 'orgs/users/update.html'
    model = User
    fields = ['username','email','organization']
