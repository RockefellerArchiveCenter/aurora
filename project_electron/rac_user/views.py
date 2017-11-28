# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.urlresolvers import reverse_lazy
from django import forms

from django.shortcuts import render, redirect

from rac_user.form import UserPasswordResetForm, UserPasswordResetConfirmForm

from braces.views import AnonymousRequiredMixin

class SplashView(AnonymousRequiredMixin, TemplateView):
    # template_name = 'transfer_app/splash.html'
    # authenticated_redirect_url = reverse_lazy(u"app_home")

    def get(self, request):
        return redirect('login')

class UserPasswordResetView(AnonymousRequiredMixin, PasswordResetView):
    template_name = 'rac_user/password_reset.html'
    form_class = UserPasswordResetForm

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Reset Password'
        return context

class UserPasswordResetDoneView(AnonymousRequiredMixin, PasswordResetDoneView):
    template_name = 'rac_user/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetDoneView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Password Reset Link Sent'
        return context

class UserPasswordResetConfirmView(AnonymousRequiredMixin, PasswordResetConfirmView):
    template_name = 'rac_user/password_reset_confirm.html'
    form_class = UserPasswordResetConfirmForm

    def get_context_data(self, **kwargs):
        context = super(PasswordResetConfirmView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Change Password'
        return context

class UserPasswordResetCompleteView(AnonymousRequiredMixin, PasswordResetCompleteView):
    template_name = 'rac_user/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super(PasswordResetCompleteView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Password Change Complete'
        return context
