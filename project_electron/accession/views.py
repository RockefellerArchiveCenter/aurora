# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView

from django.shortcuts import render
from orgs.authmixins import RACUserMixin


class AccessionView(RACUserMixin, TemplateView):
    template_name = "accession/main.html"

class AccessionRecordView(RACUserMixin, TemplateView):
    template_name = "accession/create.html"
