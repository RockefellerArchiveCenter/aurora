from django import forms
from django.forms.models import inlineformset_factory

from bag_transfer.rights.models import (RightsStatement,
                                        RightsStatementCopyright,
                                        RightsStatementLicense,
                                        RightsStatementOther,
                                        RightsStatementRightsGranted,
                                        RightsStatementStatute)


class RightsForm(forms.ModelForm):
    class Meta:
        model = RightsStatement
        fields = ("applies_to_type", "rights_basis", "organization")
        labels = {
            "rights_basis": "Rights Basis",
            "applies_to_type": "Applies to Record Type(s)",
        }
        help_texts = {
            "applies_to_type": "The record types for which this rights statement applies. If no options are available here, values must first be added in this organization's BagIt Profile."
        }
        widgets = {
            "rights_basis": forms.widgets.Select(attrs={"class": "form-control"}),
            "applies_to_type": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "list-unstyled"}
            ),
            "organization": forms.widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        applies_to_type_choices = kwargs.pop("applies_to_type_choices", None)
        organization = kwargs.pop("organization", None)
        super(RightsForm, self).__init__(*args, **kwargs)

        if applies_to_type_choices:
            self.fields["applies_to_type"].choices = list(applies_to_type_choices)
            self.fields["applies_to_type"].widget.choices = list(
                applies_to_type_choices
            )
            if "instance" in kwargs:
                self.initial["applies_to_type"] = kwargs[
                    "instance"
                ].applies_to_type.all()
        else:
            self.fields["applies_to_type"].choices = []
            self.fields["applies_to_type"].widget.choices = []

        if organization:
            self.initial["organization"] = organization


class RightsGrantedForm(forms.ModelForm):
    class Meta:
        model = RightsStatementRightsGranted
        fields = (
            "act",
            "restriction",
            "start_date_period",
            "end_date_period",
            "start_date",
            "end_date",
            "end_date_open",
            "rights_granted_note",
        )
        labels = {
            "act": "Act",
            "restriction": "Restriction(s)",
            "start_date": "Start Date",
            "end_date": "End Date",
            "start_date_period": "Years After Start Date",
            "end_date_period": "Years After End Date",
            "end_date_open": "Open end date?",
            "rights_granted_note": "Note",
        }
        help_texts = {
            "act": "The action the preservation repository is allowed to take; eg. replicate, migrate, modify, use, disseminate, delete.",
            # 'start_date': "The beginning date of the rights or restrictions Use 'Start Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'end_date': "The ending date of the rights or restrictions. Use 'End Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'start_date_period': "The number of years after the start date when this grant or restriction begins to apply. Will be used to calculate date ranges based on dates for each transfer.",
            # 'end_date_period': "The number of years after the end date when this grant or restriction no longer applies. Will be used to calculate date ranges based on dates for each transfer.",
            "end_date_open": "Select if this grant or restriction applies in perpetuity.",
            "rights_granted_note": "A prose description of the action or restriction.",
        }
        widgets = {
            "act": forms.widgets.Select(attrs={"class": "form-control"}),
            "restriction": forms.widgets.Select(attrs={"class": "form-control"}),
            "start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "start_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "end_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "rights_granted_note": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


class RightsBasisForm(forms.ModelForm):
    # overrides has_changed to force validation on formsets
    def has_changed(self):
        return True


class RightsCopyrightForm(RightsBasisForm):
    class Meta:
        model = RightsStatementCopyright
        fields = (
            "copyright_status",
            "copyright_jurisdiction",
            "copyright_status_determination_date",
            "copyright_start_date_period",
            "copyright_end_date_period",
            "copyright_applicable_start_date",
            "copyright_applicable_end_date",
            "copyright_end_date_open",
            "copyright_note",
        )
        labels = {
            "copyright_status": "Copyright Status",
            "copyright_jurisdiction": "Copyright Jurisdiction",
            "copyright_status_determination_date": "Copyright Status Determination Date",
            "copyright_applicable_start_date": "Start Date",
            "copyright_applicable_end_date": "End Date",
            "copyright_start_date_period": "Years After Start Date",
            "copyright_end_date_period": "Years After End Date",
            "copyright_end_date_open": "Open end date?",
            "copyright_note": "Note",
        }
        help_texts = {
            "copyright_status": "A coded designation of the copyright status of the object at the time the rights statement is recorded.",
            "copyright_jurisdiction": "The country whose copyright laws apply. Use values from ISO 3166.",
            "copyright_status_determination_date": "The date that the copyright status recorded in 'copyright status' was determined.",
            # 'copyright_applicable_start_date': "The date when this copyright begins to apply. Use 'Start Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'copyright_applicable_end_date': "The date when this copyright no longer applies. Use 'End Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'copyright_start_date_period': "The number of years after the start date when copyright begins to apply. Will be used to calculate date ranges based on dates for each transfer.",
            # 'copyright_end_date_period': "The number of years after the end date when copyright no longer applies. Will be used to calculate date ranges based on dates for each transfer.",
            "copyright_end_date_open": "Select if this copyright applies in perpetuity.",
            "copyright_note": "A prose description of the copyright.",
        }
        widgets = {
            "copyright_status": forms.widgets.Select(attrs={"class": "form-control"}),
            "copyright_jurisdiction": forms.widgets.TextInput(
                attrs={"class": "form-control"}
            ),
            "copyright_status_determination_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "copyright_applicable_start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "copyright_applicable_end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "copyright_start_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "copyright_end_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "copyright_note": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


class RightsStatuteForm(RightsBasisForm):
    class Meta:
        model = RightsStatementStatute
        fields = (
            "statute_jurisdiction",
            "statute_citation",
            "statute_determination_date",
            "statute_start_date_period",
            "statute_end_date_period",
            "statute_applicable_start_date",
            "statute_applicable_end_date",
            "statute_end_date_open",
            "statute_note",
        )
        labels = {
            "statute_jurisdiction": "Statute Jurisdiction",
            "statute_citation": "Statute Citation",
            "statute_determination_date": "Statute Determination Date",
            "statute_applicable_start_date": "Start Date",
            "statute_applicable_end_date": "End Date",
            "statute_start_date_period": "Years After Start Date",
            "statute_end_date_period": "Years After End Date",
            "statute_end_date_open": "Open end date?",
            "statute_note": "Note",
        }
        help_texts = {
            "statute_jurisdiction": "The country or other political body enacting the statute.",
            "statute_citation": "An identifying designation for the statute.",
            "statute_determination_date": "The date that the determination was made that the statue authorized the permission(s) noted.",
            # 'statute_applicable_start_date': "The date when the statute begins to apply. Use 'Start Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'statute_applicable_end_date': "The date when the statute ceasees to apply. Use 'End Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'statute_start_date_period': "The number of years after the start date when the statute begins to apply. Will be used to calculate date ranges based on dates for each transfer",
            # 'statute_end_date_period': "The number of years after the end date when the statute no longer applies. Will be used to calculate date ranges based on dates for each transfer",
            "statute_end_date_open": "Select if this statute applies in perpetuity.",
            "statute_note": "A prose description of the statute.",
        }
        widgets = {
            "statute_jurisdiction": forms.widgets.TextInput(
                attrs={"class": "form-control"}
            ),
            "statute_citation": forms.widgets.TextInput(
                attrs={"class": "form-control"}
            ),
            "statute_determination_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "statute_applicable_start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "statute_applicable_end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "statute_start_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "statute_end_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "statute_note": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


class RightsOtherRightsForm(RightsBasisForm):
    class Meta:
        model = RightsStatementOther
        fields = (
            "other_rights_basis",
            "other_rights_start_date_period",
            "other_rights_end_date_period",
            "other_rights_applicable_start_date",
            "other_rights_applicable_end_date",
            "other_rights_end_date_open",
            "other_rights_note",
        )
        labels = {
            "other_rights_basis": "Other Rights Basis",
            "other_rights_applicable_start_date": "Start Date",
            "other_rights_applicable_end_date": "End Date",
            "other_rights_start_date_period": "Years After Start Date",
            "other_rights_end_date_period": "Years After End Date",
            "other_rights_end_date_open": "Open end date?",
            "other_rights_note": "Note",
        }
        help_texts = {
            "other_rights_basis": "The designation of the basis for the rights or permission described in the rights statement identifier.",
            # 'other_rights_applicable_start_date': "The date when the rights begins to apply. Use 'Start Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'other_rights_applicable_end_date': "The date when the rights no longer applies. Use 'End Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'other_rights_start_date_period': "The number of years after the start date when these rights begin to apply. Will be used to calculate date ranges based on dates for each transfer.",
            # 'other_rights_end_date_period': "The number of years after the end date when these rights no longer apply. Will be used to calculate date ranges based on dates for each transfer.",
            "other_rights_end_date_open": "Select if these rights apply in perpetuity.",
            "other_rights_note": "A prose description of the rights.",
        }
        widgets = {
            "other_rights_basis": forms.widgets.Select(attrs={"class": "form-control"}),
            "other_rights_applicable_start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "other_rights_applicable_end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "other_rights_start_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "other_rights_end_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "other_rights_note": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


class RightsLicenseForm(RightsBasisForm):
    class Meta:
        model = RightsStatementLicense
        fields = (
            "license_terms",
            "license_start_date_period",
            "license_end_date_period",
            "license_applicable_start_date",
            "license_applicable_end_date",
            "license_end_date_open",
            "license_note",
        )
        labels = {
            "license_terms": "License Terms",
            "license_applicable_start_date": "Start Date",
            "license_applicable_end_date": "End Date",
            "license_start_date_period": "Years After Start Date",
            "license_end_date_period": "Years After End Date",
            "license_end_date_open": "Open end date?",
            "license_note": "Note",
        }
        help_texts = {
            "license_terms": "Text describing the license or agreement by which permission was granted.",
            # 'license_applicable_start_date': "The date when the license begins to apply. Use 'Start Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'license_applicable_end_date': "The end date when the license no longer applies. Use 'End Date Period' for dates which should be calculated based on dates of each transfer.",
            # 'license_start_date_period': "The number of years after the start date when the license begins to apply. Will be used to calculate date ranges based on dates for each transfer.",
            # 'license_end_date_period': "The number of years after the end date when this license no longer applies. Will be used to calculate date ranges based on dates for each transfer.",
            "license_end_date_open": "Select if this license applies in perpetuity.",
            "license_note": "A prose description of the license.",
        }
        widgets = {
            "license_terms": forms.widgets.TextInput(attrs={"class": "form-control"}),
            "license_applicable_start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "license_applicable_end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "license_start_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "license_end_date_period": forms.widgets.NumberInput(
                attrs={"class": "form-control"}
            ),
            "license_note": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }


# create inline formsets for child elements
CopyrightFormSet = inlineformset_factory(
    RightsStatement,
    RightsStatementCopyright,
    extra=1,
    max_num=1,
    can_delete=False,
    form=RightsCopyrightForm,
)

StatuteFormSet = inlineformset_factory(
    RightsStatement,
    RightsStatementStatute,
    extra=1,
    max_num=1,
    can_delete=False,
    form=RightsStatuteForm,
)

LicenseFormSet = inlineformset_factory(
    RightsStatement,
    RightsStatementLicense,
    extra=1,
    max_num=1,
    can_delete=False,
    form=RightsLicenseForm,
)

OtherFormSet = inlineformset_factory(
    RightsStatement,
    RightsStatementOther,
    extra=1,
    max_num=1,
    can_delete=False,
    form=RightsOtherRightsForm,
)

RightsGrantedFormSet = inlineformset_factory(
    RightsStatement,
    RightsStatementRightsGranted,
    extra=1,
    max_num=1,
    form=RightsGrantedForm,
)
