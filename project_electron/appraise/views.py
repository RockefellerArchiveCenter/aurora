# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, UpdateView

from django.shortcuts import render, redirect

from orgs.models import Archives
from orgs.authmixins import RACUserMixin
from appraise.form import AppraisalNoteUpdateForm

class AppraiseView(RACUserMixin, TemplateView):
    template_name = "appraise/main.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Appraisal Queue'
        context['uploads'] = Archives.objects.filter(process_status=40, organization = self.request.user.organization).order_by('created_time')
        return context

class AppraisalNoteUpdateView(UpdateView):
    model = Archives
    form_class = AppraisalNoteUpdateForm
    template_name = 'appraise/edit_note.html'

    def form_valid(self, form):
        form.save()
        return redirect('appraise-main')

class RejectTransferView(UpdateView):
    template_name = "appraise/main.html"
    model = Archives

    def get(self, request, *args, **kwargs):
        obj = Archives.objects.get(pk=self.kwargs.get('pk'))
        Archives.reject_transfer(obj)
        return redirect('appraise-main')

class AcceptTransferView(UpdateView):
    template_name = "appraise/main.html"
    model = Archives

    def get(self, request, *args, **kwargs):
        obj = Archives.objects.get(pk=self.kwargs.get('pk'))
        Archives.accept_transfer(obj)
        return redirect('appraise-main')
