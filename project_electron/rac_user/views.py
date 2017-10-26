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

    def get(self,request):
        return redirect('login')

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(required=True,
                  widget=forms.EmailInput(attrs={
                    'class': 'form-control has-feedback'}),
                  error_messages={
                    'required': 'Please enter your email'})

class UserPasswordResetView(PasswordResetView):
    template_name = 'rac_user/password_reset.html'
    form_class = UserPasswordResetForm

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'rac_user/password_reset_done.html'

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

class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'rac_user/password_reset_confirm.html'
    form_class = UserPasswordResetConfirmForm

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'rac_user/password_reset_complete.html'
