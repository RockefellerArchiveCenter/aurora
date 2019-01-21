# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect

from braces.views import AnonymousRequiredMixin

from bag_transfer.mixins.authmixins import *
from bag_transfer.users.form import *


class SplashView(AnonymousRequiredMixin, TemplateView):

    def get(self, request):
        return redirect('login')


class UsersListView(ArchivistMixin, SuccessMessageMixin, ListView):
    template_name = 'users/list.html'
    model = User

    def get(self, request, *args, **kwargs):
        users_list = [{'org': {}, 'users': []}]
        users_list[0]['org'] = {'pass': 'pass'}
        users_list[0]['users'] = User.objects.all().order_by('username')
        org_users_list = [{'org': {}, 'users': []}]
        org_users_list = Organization.users_by_org()

        return render(request, self.template_name, {
            'meta_page_title': 'Users',
            'users_list': users_list,
            'org_users_list': org_users_list,
            })


class UsersCreateView(ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = 'users/update.html'
    model = User
    success_message = "New User Saved!"

    def get_form_class(self):
        return (OrgUserCreateForm)

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.object.pk})


class UsersDetailView(OrgReadViewMixin, DetailView):
    template_name = 'users/detail.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UsersDetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = self.object.username
        context['uploads'] = []
        archives = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            user_uploaded=context['object']).order_by('-created_time')[:9]
        for archive in archives:
            archive.bag_info_data = archive.get_bag_data()
            context['uploads'].append(archive)
        context['uploads_count'] = Archives.objects.filter(
            process_status__gte=Archives.TRANSFER_COMPLETED,
            user_uploaded=context['object']).count()
        return context


class UsersEditView(ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/update.html'
    model = User
    success_message = "Your changes have been saved!"

    def get_form_class(self):
        return (RACSuperUserUpdateForm if self.object.is_staff else OrgUserUpdateForm)

    def get_context_data(self, **kwargs):
        context = super(UsersEditView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit {}".format(self.object.username)
        context['meta_page_title'] = "Edit {}".format(self.object.username)
        return context

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.object.pk})


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    model = User
    success_message = "New password saved."
    form_class = UserPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super(UserPasswordChangeView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Change Password'
        return context

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.request.user.pk})


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
            required=True,
            widget=forms.EmailInput(attrs={'class': 'form-control has-feedback'}),
            error_messages={'required': 'Please enter your email'})


class UserPasswordResetView(AnonymousRequiredMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    form_class = UserPasswordResetForm

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Reset Password'
        return context


class UserPasswordResetDoneView(AnonymousRequiredMixin, PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetDoneView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Password Reset Link Sent'
        return context


class UserPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
                    required=True, label='New Password',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                    error_messages={'required': 'Please enter your new password'})
    new_password2 = forms.CharField(
                    required=True, label='New Password (repeat)',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                    error_messages={'required': 'Please confirm your new password'})


class UserPasswordResetConfirmView(AnonymousRequiredMixin, PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = UserPasswordResetConfirmForm

    def get_context_data(self, **kwargs):
        context = super(PasswordResetConfirmView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Change Password'
        return context


class UserPasswordResetCompleteView(AnonymousRequiredMixin, PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetCompleteView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Password Change Complete'
        return context
