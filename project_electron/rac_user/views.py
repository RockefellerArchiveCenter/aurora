# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse_lazy
from django import forms

from django.shortcuts import render, redirect

from braces.views import AnonymousRequiredMixin

class SplashView(AnonymousRequiredMixin, TemplateView):
    # template_name = 'transfer_app/splash.html'
    # authenticated_redirect_url = reverse_lazy(u"app_home")

    def get(self, request):
        return redirect('login')

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(required=True,
                  widget=forms.EmailInput(attrs={
                    'class': 'form-control has-feedback'}),
                  error_messages={
                    'required': 'Please enter your email'})

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

class UserPasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(required=True, label='New Password',
                  widget=forms.PasswordInput(attrs={
                    'class': 'form-control'}),
                  error_messages={
                    'required': 'Please enter your new password'})
    new_password2 = forms.CharField(required=True, label='New Password (repeat)',
                  widget=forms.PasswordInput(attrs={
                    'class': 'form-control'}),
                  error_messages={
                    'required': 'Please confirm your new password'})

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
