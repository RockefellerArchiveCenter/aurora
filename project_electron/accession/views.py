# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render


class AccessionView(TemplateView):
    template_name = "accession/main.html"
