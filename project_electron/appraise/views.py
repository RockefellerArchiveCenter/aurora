# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, UpdateView

from django.shortcuts import render
from orgs.models import Archives
from orgs.authmixins import RACUserMixin
from appraise.form import AppraisalNoteUpdateForm

class AppraiseView(RACUserMixin, TemplateView):
    template_name = "appraise/main.html"

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Appraisal Queue'
        context['uploads'] = Archives.objects.filter(process_status__status_short=40, organization = self.request.user.organization).order_by('created_time')
        return context

class AppraisalNoteUpdateView(UpdateView):
    model = Archives
    form_class = AppraisalNoteUpdateForm
    template_name = 'appraise/edit_note.html'

    # def dispatch(self, *args, **kwargs):
    #     self.item_id = kwargs['pk']
    #     return super(AppraisalNoteUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect('appraise-main')
