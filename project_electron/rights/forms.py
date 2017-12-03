from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _
from django.forms.models import inlineformset_factory

from rights.models import *

class RightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatement
		fields = ('appliestotype', 'rightsbasis')
		labels = {
			'rightsbasis': 'Rights Basis',
			'appliestotype': 'Applies to Type'
		}
        widgets = {
			'appliestotype': forms.widgets.CheckboxInput(attrs={'class': 'form-control',}),
			'rightsbasis': forms.widgets.TextInput(attrs={'class': 'form-control',}),}

class RightsGrantedForm(forms.ModelForm):
	class Meta:
		model = RightsStatementRightsGranted
		fields = ('act', 'startdate', 'enddate', 'enddateopen', 'rightsgrantednote')
		labels = {
			'act': 'Act',
			'restriction': 'Restriction(s)',
			'startdate': 'Start Date',
			'enddate': 'End Date',
			'enddateopen': 'Open end date?',
			'rightsgrantednote': 'Note',}
		help_texts = {
			'act': "The action the preservation repository is allowed to take; eg replicate, migrate, modify, use, disseminate, delete",
			'restriction': 'Restriction(s)',
			'startdate': "The beginning date of the rights or restrictions granted",
			'enddate': "The ending date of the rights or restrictions granted",
			'rightsgrantednote': 'Note',}
		widgets = {
            'act': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'restriction': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'startdate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'enddate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'rightsgrantednote': forms.widgets.TextInput(attrs={'class': 'form-control', 'rows': 2}), }

class RightsCopyrightForm(forms.ModelForm):
	class Meta:
		model = RightsStatementCopyright
		fields = ('copyrightstatus', 'copyrightjurisdiction', 'copyrightstatusdeterminationdate', 'copyrightapplicablestartdate', 'copyrightapplicableenddate', 'copyrightenddateopen', 'copyrightnote')
		labels = {
			'copyrightstatus': 'Copyright Status',
			'copyrightjurisdiction': 'Copyright Jurisdiction',
			'copyrightstatusdeterminationdate': 'Copyright Status Determination Date',
			'copyrightapplicablestartdate': 'Start Date',
			'copyrightapplicableenddate': 'End Date',
			'copyrightenddateopen': 'Open end date?',
			'copyrightnote': 'Note',}
		help_texts = {
			'copyrightstatus': "A coded designation of the copyright status of the object at the time the rights statement is recorded. Available options: Copyrighted, Public Domain, Unknown",
			'copyrightjurisdiction': "The country whose copyright laws apply [ISO 3166]",
			'copyrightstatusdeterminationdate': "The date that the copyright status recorded in 'copyright status' was determined.",
			'copyrightapplicablestartdate': "The date when the particular copyright applies or is applied to the content.",
			'copyrightapplicableenddate': "The date when the particular copyright no longer applies or is applied to the content.",}
		widgets = {
            'copyrightstatus': forms.widgets.Select(attrs={'class': 'form-control'}),
            'copyrightjurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'copyrightstatusdeterminationdate': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'copyrightapplicablestartdate': forms.widgets.DateInput(attrs={'class': 'form-control'}),
            'copyrightapplicableenddate': forms.widgets.DateInput(attrs={'class': 'form-control'}),
			'copyrightnote': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 2}), }

class RightsStatuteForm(forms.ModelForm):
	class Meta:
		model = RightsStatementStatuteInformation
		fields = ('statutejurisdiction', 'statutecitation', 'statutedeterminationdate', 'statuteapplicablestartdate', 'statuteapplicableenddate', 'statuteenddateopen', 'statutenote')
		labels = {
			'statutejurisdiction': 'Statute Jurisdiction',
            'statutecitation': 'Statute Citation',
            'statutedeterminationdate': 'Statute Determination Date',
            'statuteapplicablestartdate': 'Start Date',
            'statuteapplicableenddate': 'End Date',
			'statuteenddateopen': 'Open end date?',
			'statutenote': 'Note'}
		help_texts = {
			'statutejurisdiction': "The country or other political body enacting the statute.",
			'statutecitation': "An identifying designation for the statute.",
			'statutedeterminationdate': "The date that the determination was made that the statue authorized the permission(s) noted.",
			'statuteapplicablestartdate': "The date when the statute begins to apply or is applied to the content.",
			'statuteapplicableenddate': "The date when the statute ceasees to apply or be applied to the content.",}
		widgets = {
            'statutejurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statutecitation': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statutedeterminationdate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statuteapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'statuteapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'statutenote': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 2}) }

class RightsOtherRightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatementOtherRightsInformation
		fields = ('otherrightsbasis', 'otherrightsapplicablestartdate', 'otherrightsapplicableenddate', 'otherrightsenddateopen', 'otherrightsnote')
		labels = {
			'otherrightsbasis': 'Other Rights Basis',
			'otherrightsapplicablestartdate': 'Start Date',
			'otherrightsapplicableenddate': 'End Date',
			'otherrightsenddateopen': 'Open end date?',
			'otherrightsnote': 'Note', }
		help_texts = {
			'otherrightsbasis': "The designation of the basis for the other right or permission described in the rights statement identifier.",
            'otherrightsapplicablestartdate': "The date when the other right applies or is applied to the content.",
            'otherrightsapplicableenddate': "The date when the other right no longer applies or is applied to the content.",
		}
		widgets = {
            'otherrightsbasis': forms.widgets.Select(attrs={'class': 'form-control'}),
            'otherrightsapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'otherrightsapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'otherrightsnote': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 2}), }

class RightsLicenseForm(forms.ModelForm):
	class Meta:
		model = RightsStatementLicense
		fields = ('licenseterms', 'licenseapplicablestartdate', 'licenseapplicableenddate', 'licenseenddateopen', 'licensenote')
		labels = {
			'licenseterms': 'Licence Terms',
            'licenseapplicablestartdate': 'Start Date',
            'licenseapplicableenddate': 'End Date',
			'licenseenddateopen': 'Open end date?',
			'licensenote': 'Note',
		}
		help_texts = {
			'licenseterms': "Text describing the license or agreement by which permission as granted.",
            'licenseapplicablestartdate': "The date at which the license first applies or is applied to the content.",
            'licenseapplicableenddate': "The end date at which the license no longer applies or is applied to the content.",
		}
		widgets = {
            'licenseterms': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'licenseapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'licenseapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control'}),
			'licensenote': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 2}), }

# create inline formsets for child elements
CopyrightFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementCopyright,
	extra=1,
	can_delete=False,
	form=RightsCopyrightForm
)

StatuteFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementStatuteInformation,
	extra=1,
	can_delete=False,
	form=RightsStatuteForm
)

LicenseFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementLicense,
	extra=1,
	can_delete=False,
	form=RightsLicenseForm
)

OtherFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementOtherRightsInformation,
	extra=1,
	can_delete=False,
	form=RightsOtherRightsForm
)

RightsGrantedFormSet = inlineformset_factory(
	RightsStatement,
	RightsStatementRightsGranted,
	extra=1,
	can_delete=False,
	form=RightsGrantedForm
)
