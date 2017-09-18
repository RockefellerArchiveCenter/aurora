# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse_lazy

from django.shortcuts import render, redirect

from braces.views import AnonymousRequiredMixin

class SplashView(AnonymousRequiredMixin, TemplateView):
    # template_name = 'transfer_app/splash.html'
    # authenticated_redirect_url = reverse_lazy(u"app_home")

    def get(self,request):
        return redirect('login')
