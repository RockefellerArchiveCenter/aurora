# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# these two imports may be unnecessary later
import random
from datetime import datetime

import json

from django.views.generic import ListView, View
from django.db.models import CharField, F
from django.db.models.functions import Concat
from django.contrib import messages
from django.shortcuts import render, redirect

from aurora import settings
from bag_transfer.accession.models import Accession, AccessionExternalIdentifier
from bag_transfer.accession.forms import AccessionForm, CreatorsFormSet
from bag_transfer.accession.db_functions import GroupConcat
from bag_transfer.api.clients import AquariusClient, FornaxClient, AltairClient
from bag_transfer.api.serializers import AccessionSerializer
from bag_transfer.mixins.authmixins import AccessioningArchivistMixin
from bag_transfer.models import Archives, RecordCreators, Organization, BAGLog, LanguageCode
from bag_transfer.rights.models import RightsStatement


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

    def deliver_data(self, consumer, client, data):
        if hasattr(settings, consumer.upper()):
            try:
                client = client()
                resp = client.save_accession(data)
                print data
                if resp:
                    return True
                else:
                    return False
            except Exception as e:
                return False
        else:
            return True

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        creators_formset = CreatorsFormSet(request.POST)
        id_list = map(int, request.GET.get('transfers').split(','))
        transfers_list = Archives.objects.filter(pk__in=id_list)
        rights_statements = RightsStatement.objects.filter(archive__in=id_list).annotate(rights_group=F('rights_basis')).order_by('rights_group')
        if form.is_valid():
            accession = form.save()
            accession.process_status = 10
            accession.save()
            merged_rights_statements = RightsStatement.merge_rights(rights_statements)
            for transfer in transfers_list:
                BAGLog.log_it('BACC', transfer)
                transfer.process_status = 75
                transfer.accession = accession
                transfer.save()
            for statement in merged_rights_statements:
                statement.accession = accession
                statement.save()
            if creators_formset.is_valid():
                creators_formset.save()
                serializer = AccessionSerializer(accession, context={'request': request})
                if self.deliver_data('aquarius', AquariusClient, json.dumps(serializer.data)):
                    messages.success(
                        request,
                        ' Accession {} created successfully and sent to {}.'.format(
                            accession.accession_number, 'ArchivesSpace'))
                    accession.process_status = 20
                    accession.save()
                    if self.deliver_data(request, 'fornax', FornaxClient, json.dumps(serializer.data)):
                        messages.success(
                            request,
                            ' Accession {} created successfully and sent to {}.'.format(
                                accession.accession_number, 'Archivematica'))
                        accession.process_status = 30
                        accession.save()
                return redirect('accession-main')
        return render(request, self.template_name, {
            'meta_page_title': 'Create Accession Record',
            'form': form,
            'creators_formset': creators_formset,
            'rights_statements': rights_statements,
            'transfers': transfers_list
            })

    def get(self, request, *args, **kwargs):
        id_list = map(int, request.GET.get('transfers').split(','))
        transfers_list = Archives.objects.filter(pk__in=id_list)
        rights_statements = RightsStatement.objects.filter(archive__in=id_list).annotate(rights_group=F('rights_basis')).order_by('rights_group')
        # should this get the source_organization from bag_data instead? Need to coordinate with data in other views
        organization = transfers_list[0].organization
        accession_number = AltairClient().get_next_accession_number()
        notes = {'appraisal': []}
        dates = {'start': [], 'end': []}
        creators_list = []
        descriptions_list = []
        languages_list = []
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
            for language in bag_data.get('language', []):
                languages_list.append(language)
            creators_list += transfer.get_records_creators()
        for statement in rights_statements:
            rights_info = statement.get_rights_info_object()
            rights_granted = statement.get_rights_granted_objects()
            if not statement.rights_basis.lower() in notes:
                notes[statement.rights_basis.lower()] = []
            notes[statement.rights_basis.lower()].append(next(value for key, value in rights_info.__dict__.iteritems() if '_note' in key.lower()))
            for grant in rights_granted:
                notes[statement.rights_basis.lower()].append(grant.rights_granted_note)
        record_creators = list(set(creators_list))
        languages_list = list(set(languages_list))
        language = LanguageCode.objects.get_or_create(code='und')[0]
        if len(languages_list) == 1:
            LanguageCode.objects.get_or_create(code=languages_list[0])[0]
        if len(languages_list) > 1:
            language = LanguageCode.objects.get_or_create(code='mul')[0]
        title = '{} {}'.format(organization, bag_data.get('record_type', ''))
        if len(record_creators) > 0:
            title = '{}, {} {}'.format(
                organization, ', '.join([creator.name for creator in record_creators]),
                bag_data.get('record_type', ''))
        form = AccessionForm(initial={
            'title': title,
            # faked for now, will eventually get this from ArchivesSpace
            'accession_number': accession_number,
            'start_date': sorted(dates.get('start', []))[0],
            'end_date': sorted(dates.get('end', []))[-1],
            'description': ' '.join(set(descriptions_list)),
            'extent_files': extent_files,
            'extent_size': extent_size,
            'access_restrictions': ' '.join(set(notes.get('other', [])+notes.get('license', [])+notes.get('statute', []))),
            'use_restrictions': ' '.join(set(notes.get('copyright', []))),
            'acquisition_type': organization.acquisition_type,
            'appraisal_note': ' '.join(set(notes.get('appraisal', []))),
            'organization': organization,
            'language': language,
            'creators': record_creators,
            })
        creators_formset = CreatorsFormSet(queryset=RecordCreators.objects.filter(name__in=record_creators))
        return render(request, self.template_name, {
            'form': form,
            'creators_formset': creators_formset,
            'meta_page_title': 'Create Accession Record',
            'transfers': transfers_list,
            'rights_statements': rights_statements,
            })
                                                                                                                                                                                                                                                                                                                                
