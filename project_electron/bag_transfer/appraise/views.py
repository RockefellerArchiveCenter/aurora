# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView, UpdateView

from django.shortcuts import render, redirect

from bag_transfer.models import Archives, BAGLog
from bag_transfer.mixins.authmixins import ArchivistMixin

class AppraiseView(ArchivistMixin, View):
    template_name = "appraise/main.html"

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            rdata = {}
            rdata['success'] = 0

            if request.user.has_privs('APPRAISER'):

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
                                elif request.GET['req_type'] == 'decision' and 'appraisal_decision' in request.GET:
                                    appraisal_decision = 0
                                    try:
                                        appraisal_decision = int(request.GET['appraisal_decision'])
                                    except Exception as e:
                                        print e
                                    upload.process_status = (70 if appraisal_decision else 60)
                                    BAGLog.log_it(('BACPT' if appraisal_decision else 'BREJ'), upload)
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
