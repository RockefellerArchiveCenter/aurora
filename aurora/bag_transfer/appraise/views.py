# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django_datatables_view.base_datatable_view import BaseDatatableView
from dateutil import tz
import json

from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.shortcuts import render, redirect

from bag_transfer.lib.files_helper import remove_file_or_dir
from bag_transfer.models import Archives, BAGLog
from bag_transfer.mixins.formatmixins import JSONResponseMixin
from bag_transfer.mixins.authmixins import ArchivistMixin


class AppraiseView(ArchivistMixin, JSONResponseMixin, View):
    template_name = "appraise/main.html"

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            rdata = {}
            rdata['success'] = 0

            if request.user.has_privs('APPRAISER'):

                if 'upload_id' in request.GET:
                    try:
                        upload = Archives.objects.get(pk=request.GET['upload_id'])
                    except Archives.DoesNotExist as e:
                        rdata['emess'] = e
                        return self.render_to_json_response(rdata)

                    if 'req_form' in request.GET:
                        if request.GET['req_form'] == 'detail':
                            rdata['object'] = upload.id
                            rdata['success'] = 1

                        elif request.GET['req_form'] == 'appraise':
                            if 'req_type' in request.GET:
                                if request.GET['req_type'] == 'edit':
                                    rdata['appraisal_note'] = upload.appraisal_note
                                elif request.GET['req_type'] == 'submit':
                                    upload.appraisal_note = request.GET['appraisal_note']
                                elif request.GET['req_type'] == 'delete':
                                    upload.appraisal_note = None
                                elif request.GET['req_type'] == 'decision' and 'appraisal_decision' in request.GET:
                                    appraisal_decision = 0
                                    try:
                                        appraisal_decision = int(request.GET['appraisal_decision'])
                                    except Exception as e:
                                        print e
                                    upload.process_status = (Archives.ACCEPTED if appraisal_decision else Archives.REJECTED)
                                    BAGLog.log_it(('BACPT' if appraisal_decision else 'BREJ'), upload)
                                    if not appraisal_decision:
                                        remove_file_or_dir(upload.machine_file_path)
                                upload.save()
                                print upload
                                rdata['success'] = 1

            return self.render_to_json_response(rdata)

        return render(request, self.template_name, {
            'meta_page_title': 'Appraisal Queue',
            'uploads_count': len(Archives.objects.filter(process_status=Archives.VALIDATED).order_by('created_time'))
        })


class AppraiseDataTableView(ArchivistMixin, BaseDatatableView):
    model = Archives
    columns = ['bag_it_name', 'organization__name', 'metadata__record_creators__name', 'metadata__record_type', 'machine_file_upload_time', 'bag_it_name']
    order_columns = ['bag_it_name', 'organization__name', 'metadata__record_creators__name', 'metadata__record_type', 'machine_file_upload_time', 'bag_it_name']
    max_display_length = 500

    def get_filter_method(self): return self.FILTER_ICONTAINS

    def appraise_buttons(self):
        return '<a type=button class="btn btn-xs btn-primary appraisal-accept" href="#">Accept</a>\
                <a type="button" class="btn btn-xs btn-danger appraisal-reject" href="#">Reject</a>\
                <a type="button" class="appraisal-note btn btn-xs btn-info edit-note" data-toggle="modal" data-target="#modal-appraisal-note" href="#">Note</a>\
                <a type="button" class="transfer-detail btn btn-xs btn-warning" data-toggle="modal" data-target="#modal-detail" aria-expanded="false" href="#">Details</a>'

    def get_initial_queryset(self):
        return Archives.objects.filter(process_status=Archives.VALIDATED)

    def prepare_results(self, qs):
        json_data = []
        for transfer in qs:
            creators = ''
            bag_info_data = transfer.get_bag_data()
            if bag_info_data:
                creators = ('<br/>').join(bag_info_data.get('record_creators'))
            json_data.append([
                transfer.bag_it_name,
                transfer.organization.name,
                creators,
                bag_info_data.get('record_type'),
                transfer.machine_file_upload_time.astimezone(tz.tzlocal()).strftime('%b %e, %Y %I:%M %p'),
                self.appraise_buttons(),
                transfer.id
            ])
        return json_data
