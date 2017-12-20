# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, ListView
from django.db.models import CharField
from django.db.models.functions import Concat

from django.shortcuts import render
from orgs.models import Archives, RecordCreators
from accession.models import Accession
from accession.db_functions import GroupConcat
from orgs.authmixins import RACUserMixin


class AccessionView(RACUserMixin, ListView):
    template_name = "accession/main.html"
    model = Archives

    def get_context_data(self, **kwargs):
        context = super(AccessionView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accessioning Queue'
        context['uploads'] = Archives.objects.filter(process_status=70, organization = self.request.user.organization).annotate(transfer_group=Concat('organization', 'baginfometadata__record_type', GroupConcat('baginfometadata__record_creators'), 'baginfometadata__bag_group_identifier')).order_by('transfer_group')
        return context

class AccessionRecordView(RACUserMixin, TemplateView):
    template_name = "accession/create.html"
    model = Accession

    def get(self, request, *args, **kwargs):
        id_list = map(int, request.GET.get('transfers').split(','))
        return render(request, self.template_name, {
            'meta_page_title' : 'Create Accession Record',
            'transfers' : Archives.objects.filter(pk__in=id_list)
        })
