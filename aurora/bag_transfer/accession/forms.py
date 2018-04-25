from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from bag_transfer.accession.models import Accession


class AccessionForm(forms.ModelForm):
    class Meta:
        model = Accession
        exclude = ('accession_date',)
        labels = {
            'resource': 'Related Resource',
            'title': 'Title',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'description': 'Content Description',
            'access_restrictions': 'Access Restrictions Note',
            'use_restrictions': 'Use Restrictions Note',
        }
        help_texts = {}
        widgets = {
            'title': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.widgets.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'access_restrictions': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'use_restrictions': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resource': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'accession_number': forms.widgets.HiddenInput(),
            'extent_files': forms.widgets.HiddenInput(),
            'extent_size': forms.widgets.HiddenInput(),
            'acquisition_type': forms.widgets.HiddenInput(),
            'appraisal_note': forms.widgets.HiddenInput(),
            # this should be revisited once ArchivesSpace integration is completed
            'creators': forms.widgets.MultipleHiddenInput(),
        }
