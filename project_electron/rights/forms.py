from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _
from django.forms.models import inlineformset_factory

from rights.models import *
from orgs.models import Organization

class RightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatement
		fields = ('applies_to_type', 'rights_basis',)
		labels = {
			'rights_basis': 'Rights Basis',
			'applies_to_type': 'Applies to Record Type(s)'
		}
		help_texts = {
			'applies_to_type': 'The record types for which this rights statement applies. If no options are available here, values must first be added in this organization\'s BagIt Profile.'
		}
		widgets = {
			'rights_basis': forms.widgets.Select(attrs={'class': 'form-control'}),
			'applies_to_type': forms.widgets.CheckboxSelectMultiple(),
		}

	def __init__(self, *args, **kwargs):
		applies_to_type_choices = kwargs.pop('applies_to_type_choices', None)
		super(RightsForm, self).__init__(*args, **kwargs)

		if applies_to_type_choices:
			self.fields['applies_to_type'].choices = list(applies_to_type_choices)
			self.fields['applies_to_type'].widget.choices = list(applies_to_type_choices)
			if kwargs['instance']:
				self.initial['applies_to_type'] = kwargs['instance'].applies_to_type.all()
		else:
			self.fields['applies_to_type'].choices = []
			self.fields['applies_to_type'].widget.choices = []

class RightsGrantedForm(forms.ModelForm):
	class Meta:
		model = RightsStatementRightsGranted
		fields = ('act', 'restriction', 'start_date', 'end_date', 'start_date_period', 'end_date_period', 'end_date_open', 'rights_granted_note')
		labels = {
			'act': 'Act',
			'restriction': 'Restriction(s)',
			'start_date': 'Start Date',
			'end_date': 'End Date',
			'start_date_period': 'Start Date Period',
			'end_date_period': 'End Date Period',
			'end_date_open': 'Open end date?',
			'rights_granted_note': 'Note',}
		help_texts = {
			'act': "The action the preservation repository is allowed to take; eg replicate, migrate, modify, use, disseminate, delete",
			'restriction': 'Restriction(s)',
			'start_date': "The beginning date of the rights or restrictions granted",
			'end_date': "The ending date of the rights or restrictions granted",
			'start_date_period': "The number of years after the start date for which this grant or restriction applies. Will be used to calculate date ranges based on dates for each transfer",
            'end_date_period': "The number of years after the end date for which this grant or restriction applies. Will be used to calculate date ranges based on dates for each transfer",}
		widgets = {
            'act': forms.widgets.Select(attrs={'class': 'form-control'}),
            'restriction': forms.widgets.Select(attrs={'class': 'form-control'}),
            'start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'start_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'end_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'rights_granted_note': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}), }

class RightsCopyrightForm(forms.ModelForm):
	class Meta:
		model = RightsStatementCopyright
		fields = ('copyright_status', 'copyright_jurisdiction', 'copyright_status_determination_date', 'copyright_applicable_start_date', 'copyright_applicable_end_date', 'copyright_start_date_period', 'copyright_end_date_period', 'copyright_end_date_open', 'copyright_note')
		labels = {
			'copyright_status': 'Copyright Status',
			'copyright_jurisdiction': 'Copyright Jurisdiction',
			'copyright_status_determination_date': 'Copyright Status Determination Date',
			'copyright_applicable_start_date': 'Start Date',
			'copyright_applicable_end_date': 'End Date',
			'copyright_start_date_period': 'Start Date Period',
			'copyright_end_date_period': 'End Date Period',
			'copyright_end_date_open': 'Open end date?',
			'copyright_note': 'Note',}
		help_texts = {
			'copyright_status': "A coded designation of the copyright status of the object at the time the rights statement is recorded. Available options: Copyrighted, Public Domain, Unknown",
			'copyright_jurisdiction': "The country whose copyright laws apply [ISO 3166]",
			'copyright_status_determination_date': "The date that the copyright status recorded in 'copyright status' was determined.",
			'copyright_applicable_start_date': "The date when the particular copyright applies or is applied to the content.",
			'copyright_applicable_end_date': "The date when the particular copyright no longer applies or is applied to the content.",
			'copyright_start_date_period': "The number of years after the start date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",
            'copyright_end_date_period': "The number of years after the end date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",}
		widgets = {
            'copyright_status': forms.widgets.Select(attrs={'class': 'form-control'}),
            'copyright_jurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'copyright_status_determination_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'copyright_applicable_start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'copyright_applicable_end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'copyright_start_date_period': forms.widgets.TextInput(attrs={'class': 'form-control', }),
			'copyright_end_date_period': forms.widgets.TextInput(attrs={'class': 'form-control', }),
			'copyright_note': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}), }

class RightsStatuteForm(forms.ModelForm):
	class Meta:
		model = RightsStatementStatute
		fields = ('statute_jurisdiction', 'statute_citation', 'statute_determination_date', 'statute_applicable_start_date', 'statute_applicable_end_date', 'statute_start_date_period', 'statute_end_date_period', 'statute_end_date_open', 'statute_note')
		labels = {
			'statute_jurisdiction': 'Statute Jurisdiction',
            'statute_citation': 'Statute Citation',
            'statute_determination_date': 'Statute Determination Date',
            'statute_applicable_start_date': 'Start Date',
            'statute_applicable_end_date': 'End Date',
			'statute_start_date_period': 'Start Date Period',
            'statute_end_date_period': 'End Date Period',
			'statute_end_date_open': 'Open end date?',
			'statute_note': 'Note'}
		help_texts = {
			'statute_jurisdiction': "The country or other political body enacting the statute.",
			'statute_citation': "An identifying designation for the statute.",
			'statute_determination_date': "The date that the determination was made that the statue authorized the permission(s) noted.",
			'statute_applicable_start_date': "The date when the statute begins to apply or is applied to the content.",
			'statute_applicable_end_date': "The date when the statute ceasees to apply or be applied to the content.",
			'statute_start_date_period': "The number of years after the start date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",
            'statute_end_date_period': "The number of years after the end date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",}
		widgets = {
            'statute_jurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statute_citation': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statute_determination_date': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statute_applicable_start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'statute_applicable_end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'statute_start_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statute_end_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'statute_note': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}) }

class RightsOtherRightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatementOther
		fields = ('other_rights_basis', 'other_rights_applicable_start_date', 'other_rights_applicable_end_date', 'other_rights_start_date_period', 'other_rights_end_date_period', 'other_rights_end_date_open', 'other_rights_note')
		labels = {
			'other_rights_basis': 'Other Rights Basis',
			'other_rights_applicable_start_date': 'Start Date',
			'other_rights_applicable_end_date': 'End Date',
			'other_rights_start_date_period': 'Start Date Period',
			'other_rights_end_date_period': 'End Date Period',
			'other_rights_end_date_open': 'Open end date?',
			'other_rights_note': 'Note', }
		help_texts = {
			'other_rights_basis': "The designation of the basis for the other right or permission described in the rights statement identifier.",
            'other_rights_applicable_start_date': "The date when the other right applies or is applied to the content.",
            'other_rights_applicable_end_date': "The date when the other right no longer applies or is applied to the content.",
			'other_rights_start_date_period': "The number of years after the start date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",
            'other_rights_end_date_period': "The number of years after the end date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",}
		widgets = {
            'other_rights_basis': forms.widgets.Select(attrs={'class': 'form-control'}),
            'other_rights_applicable_start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'other_rights_applicable_end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'other_rights_start_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'other_rights_end_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'other_rights_note': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}), }

class RightsLicenseForm(forms.ModelForm):
	class Meta:
		model = RightsStatementLicense
		fields = ('license_terms', 'license_applicable_start_date', 'license_applicable_end_date', 'license_start_date_period', 'license_end_date_period', 'license_end_date_open', 'license_note')
		labels = {
			'license_terms': 'Licence Terms',
            'license_applicable_start_date': 'Start Date',
            'license_applicable_end_date': 'End Date',
			'license_start_date': 'Start Date Period',
            'license_end_date': 'End Date Period',
			'license_end_date_open': 'Open end date?',
			'license_note': 'Note',
		}
		help_texts = {
			'license_terms': "Text describing the license or agreement by which permission as granted.",
            'license_applicable_start_date': "The date at which the license first applies or is applied to the content.",
            'license_applicable_end_date': "The end date at which the license no longer applies or is applied to the content.",
			'license_start_date_period': "The number of years after the start date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",
            'license_end_date_period': "The number of years after the end date for which this rights basis applies. Will be used to calculate date ranges based on dates for each transfer",}
		widgets = {
            'license_terms': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'license_applicable_start_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'license_applicable_end_date': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'license_start_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'license_end_date_period': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'license_note': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}), }

# create inline formsets for child elements
CopyrightFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementCopyright,
	extra=1,
	max_num=1,
	can_delete=False,
	form=RightsCopyrightForm
)

StatuteFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementStatute,
	extra=1,
	max_num=1,
	can_delete=False,
	form=RightsStatuteForm
)

LicenseFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementLicense,
	extra=1,
	max_num=1,
	can_delete=False,
	form=RightsLicenseForm
)

OtherFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementOther,
	extra=1,
	max_num=1,
	can_delete=False,
	form=RightsOtherRightsForm
)

RightsGrantedFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementRightsGranted,
	extra=1,
	max_num=1,
	form=RightsGrantedForm
)
