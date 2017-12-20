from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _

from accession.models import Accession

class AccessionForm(forms.ModelForm):
	class Meta:
		model = Accession
		fields = ('title','start_date','end_date','description','access_restrictions','use_restrictions')
		labels = {
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
			'start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'description': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
			'access_restrictions': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
			'use_restrictions': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
		}
