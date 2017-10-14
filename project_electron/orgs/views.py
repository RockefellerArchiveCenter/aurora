# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import ListView, UpdateView, CreateView, DetailView, View

from orgs.models import Organization, User
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.messages.views import SuccessMessageMixin

from orgs.models import Archives
from orgs.form import OrgUserUpdateForm, RACSuperUserUpdateForm

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from orgs.authmixins import *


class OrganizationCreateView(RACAdminMixin, SuccessMessageMixin, CreateView):
    template_name = 'orgs/create.html'
    model = Organization
    fields = ['name']
    success_message = "New Organization Saved!"
    def get_success_url(self):
        return reverse('orgs-detail', kwargs={'pk': self.object.pk})

class OrganizationDetailView(RACUserMixin, DetailView):
    template_name = 'orgs/detail.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)
        context['trans_lst'] = self.object.build_transfer_timeline_list()

        context['uploads'] = Archives.objects.filter(process_status=99, organization = context['object']).order_by('-created_time')[:15]
        context['uploads_count'] = Archives.objects.filter(process_status=99, organization = context['object']).count()
        return context

class OrganizationEditView(RACAdminMixin, SuccessMessageMixin,UpdateView):
    template_name = 'orgs/update.html'
    model =         Organization
    fields =        ['is_active','name']
    success_message = "Organization Saved!"

    def get_success_url(self):
        return reverse('orgs-detail', kwargs={'pk': self.object.pk})

class OrganizationTransfersView(RACUserMixin, ListView):

    template_name = 'orgs/all_transfers.html'
    def get_context_data(self,**kwargs):
        context = super(OrganizationTransfersView, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        return context

    def get_queryset(self):
        self.organization = get_object_or_404(Organization, pk=self.kwargs['pk'])
        return Archives.objects.filter(process_status=99, organization=self.organization).order_by('-created_time')

class OrganizationListView(RACUserMixin, ListView):

    template_name = 'orgs/list.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        return context

class UsersListView(RACUserMixin, ListView):
    template_name = 'orgs/users/list.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)

        refresh_ldap = User.refresh_ldap_accounts()
        if refresh_ldap:
            messages.info(self.request, '{} new accounts were just synced!'.format(refresh_ldap))

        context['users_list'] = [{'org' : {}, 'users' : []}]
        context['users_list'][0]['org'] = {'pass':'pass'}
        context['users_list'][0]['users'] = User.objects.all().order_by('username')

        context['org_users_list'] = [{'org' : {}, 'users' : []}]
        context['org_users_list'] = Organization.users_by_org()

        context['unassigned_users_list'] = [{'org' : {}, 'users' : []}]
        context['unassigned_users_list'][0]['org'] = {'pass':'pass'}
        context['unassigned_users_list'][0]['users'] = User.objects.filter(from_ldap=True,is_new_account=True,organization=None).order_by('username')

        return context

class UsersCreateView(RACAdminMixin, SuccessMessageMixin, CreateView):
    template_name = 'orgs/users/update.html'
    model = User
    fields = ['is_new_account']
    success_message = "New User Saved!"
    def get_context_data(self, **kwargs):
        context = super(UsersCreateView, self).get_context_data(**kwargs)
        context['page_title'] = "Add User"
        return context
    def get_success_url(self):
        return reverse('users-detail', kwargs={'pk': self.object.pk})


class UsersDetailView(SelfOrSuperUserMixin, DetailView):
    template_name = 'orgs/users/detail.html'
    model = User
    def get_context_data(self, **kwargs):
        context = super(UsersDetailView, self).get_context_data(**kwargs)
        context['uploads'] = Archives.objects.filter(process_status=99, organization = context['object'].organization).order_by('-created_time')[:5]
        context['uploads_count'] = Archives.objects.filter(process_status=99, organization = context['object'].organization).count()

        return context

class UsersEditView(SelfOrSuperUserMixin, SuccessMessageMixin, UpdateView):
    template_name = 'orgs/users/update.html'
    model = User
    page_title = "Edit User"
    success_message = "saved!"

    def get_form_class(self):
        return (RACSuperUserUpdateForm if self.if_editing_staffer() else OrgUserUpdateForm)

    def if_editing_staffer(self):
        return (True if self.object.username[:2] == "va" else False)

    def get_context_data(self, **kwargs):
        context = super(UsersEditView, self).get_context_data(**kwargs)
        context['editing_staffer'] = self.if_editing_staffer()
        context['page_title'] = "Edit User"
        return context

    def get_success_url(self):
        return reverse('users-detail', kwargs={'pk': self.object.pk})

class UsersTransfersView(RACUserMixin, ListView):

    template_name = 'orgs/all_transfers.html'
    def get_context_data(self,**kwargs):
        context = super(UsersTransfersView, self).get_context_data(**kwargs)
        context['user'] = self.user
        return context

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs['pk'])
        return Archives.objects.filter(user_uploaded=self.user).order_by('-created_time')
