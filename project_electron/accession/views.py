# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# these two imports may be unnecessary later
import random
from datetime import datetime

from django.views.generic import ListView, CreateView
from django.db.models import CharField, F
from django.db.models.functions import Concat
from django.contrib import messages

from django.shortcuts import render, redirect
from orgs.models import Archives, RecordCreators, Organization
from orgs.authmixins import RACUserMixin
from accession.models import Accession
from accession.forms import AccessionForm
from accession.db_functions import GroupConcat
from rights.models import RightsStatement


class AccessionView(RACUserMixin, ListView):
    template_name = "accession/main.html"
    model = Archives

    def get_context_data(self, **kwargs):
        context = super(AccessionView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Accessioning Queue'
        context['uploads'] = Archives.objects.filter(process_status=70, organization = self.request.user.organization).annotate(transfer_group=Concat('organization', 'baginfometadata__record_type', GroupConcat('baginfometadata__record_creators'), 'baginfometadata__bag_group_identifier', output_field=CharField())).order_by('transfer_group')
        return context

class AccessionRecordView(RACUserMixin, CreateView):
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
        access_note = []
        use_note = []
        creators_list = []
        descriptions_list = []
        start_dates_list = []
        end_dates_list = []
        appraisal_notes_list = []
        extent_files = 0
        extent_size = 0
        for transfer in transfers_list:
            bag_data = transfer.get_bag_data()
            extent_size = extent_size + int(bag_data['payload_oxum'].split('.')[0])
            extent_files = extent_files + int(bag_data['payload_oxum'].split('.')[1])
            descriptions_list.append(bag_data['internal_sender_description'])
            start_dates_list.append(bag_data['date_start'])
            end_dates_list.append(bag_data['date_end'])
            appraisal_notes_list.append(transfer.appraisal_note if transfer.appraisal_note else '')
            creators_list = creators_list + transfer.get_records_creators()
        for statement in rights_statements:
            if statement.rights_basis == 'Copyright':
                rights_info = statement.get_rights_info_object()
                use_note.append(rights_info.copyright_note)
                rights_granted = statement.get_rights_granted_objects()
                for grant in rights_granted:
                    use_note.append(grant.rights_granted_note)
            elif statement.rights_basis == 'Other':
                rights_info = statement.get_rights_info_object()
                access_note.append(rights_info.other_rights_note)
                rights_granted = statement.get_rights_granted_objects()
                for grant in rights_granted:
                    access_note.append(grant.rights_granted_note)
        record_creators = list(set(creators_list))
        form = AccessionForm(initial={
            'title': '{}, {} {}'.format(organization, ', '.join([creator.name for creator in record_creators]), bag_data['record_type']),
            #faked for now, will eventually get this from ArchivesSpace
            'accession_number': '{}.{}'.format(datetime.now().year, random.randint(0, 999)),
            'start_date': sorted(start_dates_list)[0],
            'end_date': sorted(end_dates_list)[-1],
            'description': ' '.join(set(descriptions_list)),
            'extent_files': extent_files,
            'extent_size': extent_size,
            'access_restrictions': ' '.join(set(access_note)),
            'use_restrictions': ' '.join(set(use_note)),
            # needs PR from master to be merged into development
            'acquisition_type': 'deposit',
            'appraisal_note': ' '.join(set(appraisal_notes_list)),
            # We'll need to revisit this once we build out ArchivesSpace integration
            'creators': record_creators,
            })
        return render(request, self.template_name, {
            'form': form,
            'meta_page_title': 'Create Accession Record',
            'transfers' : transfers_list,
            'rights_statements' : rights_statements
            })
