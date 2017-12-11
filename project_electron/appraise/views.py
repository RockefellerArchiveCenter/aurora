# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView, UpdateView

from django.shortcuts import render, redirect
from orgs.models import Archives
from orgs.authmixins import RACUserMixin
from appraise.form import AppraisalNoteUpdateForm

class AppraiseView(RACUserMixin, View):
    template_name = "appraise/main.html"

    # def get_context_data(self, **kwargs):
    #     context = super(TemplateView, self).get_context_data(**kwargs)
    #     context['meta_page_title'] = 'Appraisal Queue'
    #     context['uploads'] = Archives.objects.filter(process_status=40, organization = self.request.user.organization).order_by('created_time')
    #     return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            rdata = {}
            rdata['success'] = 0

            #
            if 'req_form' in request.GET:
                if request.GET['req_form'] == 'appraise':
                    if 'req_type' in request.GET and 'upload_id' in request.GET:
                        try:
                            upload = Archives.objects.get(pk=request.GET['upload_id'])
                        except Archives.DoesNotExist as e:
                            rdata['emess'] = e
                        else:
                            if request.GET['req_type'] == 'edit':
                                rdata['appraisal_note'] = upload.appraisal_note
                                rdata['success'] = 1
                            elif request.GET['req_type'] == 'submit':
                                upload.appraisal_note = request.GET['appraisal_note']
                                upload.save()
                                rdata['success'] = 1

            return self.render_to_json_response(rdata)

        return render(request, self.template_name, {
            'meta_page_title' : 'Appraisal Queue',
            'uploads' : Archives.objects.filter(process_status=40).order_by('created_time')
        })

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


class AppraisalNoteUpdateView(UpdateView):
    model = Archives
    form_class = AppraisalNoteUpdateForm
    template_name = 'appraise/edit_note.html'

    def form_valid(self, form):
        form.save()
        return redirect('appraise-main')
