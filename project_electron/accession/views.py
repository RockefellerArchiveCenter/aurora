# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, ListView
from django.db.models import CharField
from django.db.models.functions import Concat

from django.shortcuts import render
from orgs.models import Archives, RecordCreators
from orgs.authmixins import RACUserMixin
from accession.models import Accession
from accession.db_functions import GroupConcat
from rights.models import RightsStatement


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
        transfers_list = Archives.objects.filter(pk__in=id_list)
        rights_statements_list = RightsStatement.objects.filter(archive__in=id_list)
        access_note = []
        use_note = []
        creators_list = []
        descriptions_list = []
        extent_files = 0
        extent_size = 0
        for transfer in transfers_list:
            bag_data = transfer.get_bag_data()
            extent_size = extent_size + int(bag_data['payload_oxum'].split('.')[0])
            extent_files = extent_files + int(bag_data['payload_oxum'].split('.')[1])
            descriptions_list.append(bag_data['internal_sender_description'])
            for creator in bag_data['record_creators']:
                creators_list.append(creator)
        for statement in rights_statements_list:
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
        return render(request, self.template_name, {
            'meta_page_title' : 'Create Accession Record',
            'transfers' : transfers_list,
            'creators' : set(creators_list),
            'descriptions' : set(descriptions_list),
            'extent' : {
                'files' : extent_files,
                'size'  : extent_size
            },
            'rights_statements' : rights_statements_list,
            'access_restrictions_notes' : set(access_note),
            'use_restrictions_notes' : set(use_note)
        })
