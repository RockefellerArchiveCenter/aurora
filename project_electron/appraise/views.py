# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, UpdateView

from django.shortcuts import render, redirect
from orgs.models import Archives
from orgs.authmixins import RACUserMixin
from appraise.form import AppraisalNoteUpdateForm,AppraiseTransferForm

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

class AppraiseTransferView(UpdateView):
    template_name = "appraise/main.html"
    model = Archives
    form_class = AppraiseTransferForm
    action = ''

    def post(self, request, *args, **kwargs):
        print self.kwargs
        if self.kwargs.get('action'):
            obj = Archives.objects.get(pk=self.kwargs.get('pk'))
            obj.process_status = self.kwargs.get('action')
            obj.save()
            return redirect('appraise-main')
        else:
            return redirect('appraise-main')
