# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render

class MainView(TemplateView):
    template_name = "transfer_app/main.html"
