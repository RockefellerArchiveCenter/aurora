from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _

from rights.models import *

class RightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatement
		fields = ('rightsbasis', 'appliestotype')
        widgets = {
            'rightsbasis': forms.TextInput(attrs={'class': 'form-control',}),
			'appliestotype': forms.CheckboxInput(attrs={'class': 'form-control',}),}

class RightsGrantedForm(forms.ModelForm):
    class Meta:
        model = RightsStatementRightsGranted
        fields = ('act', 'startdate', 'enddate', 'enddateopen', 'rightsgrantednote')
        widgets = {
            'act': forms.TextInput(attrs={'class': 'form-control', 'title': "The action the preservation repository is allowed to take; eg replicate, migrate, modify, use, disseminate, delete"}),
            'restriction': forms.TextInput(attrs={'class': 'form-control',}),
            'startdate': forms.TextInput(attrs={'class': 'form-control', 'title': "The beginning date of the rights or restrictions granted"}),
            'enddate': forms.TextInput(attrs={'class': 'form-control', 'title': "The ending date of the rights or restrictions granted"}),
            'enddateopen': forms.CheckboxInput(attrs={'class': 'form-control', 'title': 'Use "OPEN" for an open ended term of restriction. Omit end date if the ending date is unknown or the permission statement applies to many objects with different end dates.'}),
			'rightsgrantednote': forms.TextInput(attrs={'class': 'form-control',}), }

class RightsCopyrightForm(forms.ModelForm):
    class Meta:
        model = RightsStatementCopyright
        fields = ('copyrightstatus', 'copyrightjurisdiction', 'copyrightstatusdeterminationdate', 'copyrightapplicablestartdate', 'copyrightapplicableenddate', 'copyrightenddateopen', 'copyrightnote')
        widgets = {
            'copyrightstatus': forms.widgets.Select(attrs={'class': 'form-control', 'title': "A coded designation of the copyright status of the object at the time the rights statement is recorded. Available options: Copyrighted, Public Domain, Unknown"}),
            'copyrightjurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The country whose copyright laws apply [ISO 3166]"}),
            'copyrightstatusdeterminationdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date that the copyright status recorded in 'copyright status' was determined."}),
            'copyrightapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the particular copyright applies or is applied to the content."}),
            'copyrightapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the particular copyright no longer applies or is applied to the content."}),
			'copyrightnote': forms.widgets.Textarea(attrs={'class': 'form-control',}), }

class RightsStatuteForm(forms.ModelForm):
    class Meta:
        model = RightsStatementStatuteInformation
        fields = ('statutejurisdiction', 'statutecitation', 'statutedeterminationdate', 'statuteapplicablestartdate', 'statuteapplicableenddate', 'statuteenddateopen', 'statutenote')
        widgets = {
            'statutejurisdiction': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The country or other political body enacting the statute."}),
            'statutecitation': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "An identifying designation for the statute."}),
            'statutedeterminationdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date that the determination was made that the statue authorized the permission(s) noted."}),
            'statuteapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the statute begins to apply or is applied to the content."}),
            'statuteapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the statute ceasees to apply or be applied to the content."}),
			'statutenote': forms.widgets.Textarea(attrs={'class': 'form-control',}), }

class RightsOtherRightsForm(forms.ModelForm):
    class Meta:
        model = RightsStatementOtherRightsInformation
        fields = ('otherrightsbasis', 'otherrightsapplicablestartdate', 'otherrightsapplicableenddate', 'otherrightsenddateopen', 'otherrightsnote')
        widgets = {
            'otherrightsbasis': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The designation of the basis for the other right or permission described in the rights statement identifier."}),
            'otherrightsapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the other right applies or is applied to the content."}),
            'otherrightsapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date when the other right no longer applies or is applied to the content."}),
			'otherrightsnote': forms.widgets.Textarea(attrs={'class': 'form-control',}), }

class RightsLicenseForm(forms.ModelForm):
    class Meta:
        model = RightsStatementLicense
        fields = ('licenseterms', 'licenseapplicablestartdate', 'licenseapplicableenddate', 'licenseenddateopen', 'licensenote')
        widgets = {
            'licenseterms': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "Text describing the license or agreement by which permission as granted."}),
            'licenseapplicablestartdate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The date at which the license first applies or is applied to the content."}),
            'licenseapplicableenddate': forms.widgets.TextInput(attrs={'class': 'form-control', 'title': "The end date at which the license no longer applies or is applied to the content."}),
			'licensenote': forms.widgets.Textarea(attrs={'class': 'form-control',}), }
