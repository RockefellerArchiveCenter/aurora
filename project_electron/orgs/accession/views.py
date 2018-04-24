# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# these two imports may be unnecessary later
import random
from datetime import datetime

from django.views.generic import ListView, View
from django.db.models import CharField, F
from django.db.models.functions import Concat
from django.contrib import messages

from django.shortcuts import render, redirect
from orgs.models import Archives, RecordCreators, Organization, BAGLog
from orgs.mixins.authmixins import AccessioningArchivistMixin
from orgs.accession.models import Accession
from orgs.accession.forms import AccessionForm
from orgs.accession.db_functions import GroupConcat
from orgs.rights.models import RightsStatement


class AccessionView(AccessioningArchivistMixin, ListView):
    template_name = "accession/main.html"
    model = Archives

    def get_context_data(self, **kwargs):
        context = super(AccessionView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accessioning Queue'
        context['uploads'] = Archives.objects.filter(
            process_status=70).annotate(transfer_group=Concat('organization', 'metadata__record_type', GroupConcat('metadata__record_creators'), 'metadata__bag_group_identifier', output_field=CharField())).order_by('transfer_group')
        return context


class AccessionRecordView(AccessioningArchivistMixin, View):
    template_name = "accession/create.html"
    model = Accession
    form_class = AccessionForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        id_list = map(int, request.GET.get('transfers').split(','))
        transfers_list = Archives.objects.filter(pk__in=id_list)
        rights_statements = RightsStatement.objects.filter(archive__in=id_list).annotate(rights_group=F('rights_basis')).order_by('rights_group')
        if form.is_valid():
            accession = form.save()
            merged_rights_statements = RightsStatement.merge_rights(rights_statements)
            for transfer in transfers_list:
                BAGLog.log_it('BACC', transfer)
                transfer.process_status = 75
                transfer.save()
            for statement in merged_rights_statements:
                statement.accession = accession
                statement.save()
            messages.success(request, ' Accession {} created successfully!'.format(accession.accession_number))
            return redirect('accession-main')
        return render(request, self.template_name, {
            'meta_page_title': 'Create Accession Record',
            'form': form,
            'rights_statements': rights_statements,
            'transfers': transfers_list
            })

    def get(self, request, *args, **kwargs):
        id_list = map(int, request.GET.get('transfers').split(','))
        transfers_list = Archives.objects.filter(pk__in=id_list)
        rights_statements = RightsStatement.objects.filter(archive__in=id_list).annotate(rights_group=F('rights_basis')).order_by('rights_group')
        # should this get the source_organization from bag_data instead? Need to coordinate with data in other views
        organization = transfers_list[0].organization
        notes = {'appraisal': []}
        dates = {'start': [], 'end': []}
        creators_list = []
        descriptions_list = []
        extent_files = 0
        extent_size = 0
        for transfer in transfers_list:
            bag_data = transfer.get_bag_data()
            extent_size = extent_size + int(bag_data.get('payload_oxum', '0.0').split('.')[0])
            extent_files = extent_files + int(bag_data.get('payload_oxum', '0.0').split('.')[1])
            dates['start'].append(bag_data.get('date_start', ''))
            dates['end'].append(bag_data.get('date_end', ''))
            notes['appraisal'].append(bag_data.get('appraisal_note', ''))
            descriptions_list.append(bag_data.get('internal_sender_description', ''))
            creators_list = creators_list + transfer.get_records_creators()
        for statement in rights_statements:
            rights_info = statement.get_rights_info_object()
            rights_granted = statement.get_rights_granted_objects()
            if not statement.rights_basis.lower() in notes:
                notes[statement.rights_basis.lower()] = []
            notes[statement.rights_basis.lower()].append(next(value for key, value in rights_info.__dict__.iteritems() if '_note' in key.lower()))
            for grant in rights_granted:
                notes[statement.rights_basis.lower()].append(grant.rights_granted_note)
        record_creators = list(set(creators_list))
        form = AccessionForm(initial={
            'title': '{}, {} {}'.format(organization, ', '.join([creator.name for creator in record_creators]), bag_data.get('record_type', '')),
            # faked for now, will eventually get this from ArchivesSpace
            'accession_number': '{}.{}'.format(datetime.now().year, random.randint(0, 999)),
            'start_date': sorted(dates.get('start', []))[0],
            'end_date': sorted(dates.get('end', []))[-1],
            'description': ' '.join(set(descriptions_list)),
            'extent_files': extent_files,
            'extent_size': extent_size,
            'access_restrictions': ' '.join(set(notes.get('other', [])+notes.get('license', [])+notes.get('statute', []))),
            'use_restrictions': ' '.join(set(notes.get('copyright', []))),
            'acquisition_type': organization.acquisition_type,
            'appraisal_note': ' '.join(set(notes.get('appraisal', []))),
            # We'll need to revisit this once we build out ArchivesSpace integration
            'creators': record_creators,
            })
        return render(request, self.template_name, {
            'form': form,
            'meta_page_title': 'Create Accession Record',
            'transfers': transfers_list,
            'rights_statements': rights_statements
            })
