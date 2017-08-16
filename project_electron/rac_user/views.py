# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render, redirect

# Create your views here.
class SplashView(TemplateView):
    # template_name = 'transfer_app/splash.html'

    def get(self,request):
        return redirect('login')
