from django import forms

from bag_transfer.models import (BagItProfile, BagItProfileBagInfo,
                                 BagItProfileBagInfoValues)


class BagItProfileForm(forms.ModelForm):
    class Meta:
        model = BagItProfile
        exclude = []
        labels = {
            "external_description": "Description",
            "allow_fetch": "Allow Fetch.txt?",
            "tag_files_required": "Tag Files Required"
        }
        widgets = {
            "organization": forms.widgets.HiddenInput(),
            "contact_email": forms.widgets.HiddenInput(),
            "source_organization": forms.widgets.HiddenInput(),
            "version": forms.widgets.HiddenInput(),
            "bagit_profile_identifier": forms.widgets.HiddenInput(),
            "external_description": forms.widgets.Textarea(
                attrs={
                    "rows": 3,
                    "aria-describedby": "id_external_description-help"
                }
            ),
            "allow_fetch": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "serialization": forms.widgets.RadioSelect(),
            "manifests_allowed": forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox--blue"}),
            "manifests_required": forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox--blue"}),
            "accept_serialization": forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox--blue"}),
            "accept_bagit_version": forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox--blue"}),
            "tag_manifests_required": forms.CheckboxSelectMultiple(attrs={"class": "checkbox checkbox--blue"}),
            "tag_files_required": forms.widgets.Textarea(attrs={"rows": 3}),
        }
        legends = {
            "manifests_allowed": "Allowed Algorithm(s) for Manifest Files *",
            "manifests_required": "Manifests Required",
            "accept_serialization": "Serializations Accepted",
            "accept_bagit_version": "BagIt Versions Accepted",
            "tag_manifests_required": "Tag Manifests Required"
        }
        help_texts = {
            "external_description": "A short description of this BagIt Profile.",
            "tag_files_required": "List required tag files, if any, separated by commas.",
            "manifests_allowed": "Select at least one.",
            "manifests_required": "If no value is selected, any algorithm is valid.",
            "accept_serialization": "Select all accepted formats. If no values are selected, the serialization format will not be checked.",
            "accept_bagit_version": "Select all versions of the BagIt Specification accepted. If no values are selected, the BagIt version will not be checked.",
            "tag_manifests_required": "If no values are selected, the tag format algorithm will not be checked."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legends = self.Meta.legends  # Make legends accessible
        self.help_texts = self.Meta.help_texts  # Make help_texts accessible
        self.fields["external_description"].initial = "BagIt Profile for transferring records to the Rockefeller Archive Center."
        self.fields["manifests_allowed"].initial = [1, 2]
        self.fields["accept_serialization"].initial = [1, 2, 3]
        self.fields["accept_bagit_version"].initial = [2]


class BagItProfileBagInfoForm(forms.ModelForm):
    class Meta:
        model = BagItProfileBagInfo
        exclude = []
        labels = {
            "field": "Field",
            "required": "Required?",
            "repeatable": "Repeatable?",
        }
        widgets = {
            "field": forms.widgets.Select(
                attrs={
                    "required": "required",
                }
            ),
            "required": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "repeatable": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
        }


class BagItProfileBagInfoValuesForm(forms.ModelForm):
    class Meta:
        model = BagItProfileBagInfoValues
        fields = ("name",)
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={"aria-labelledby": "values-label", })
        }


BagItProfileBagInfoValuesFormset = forms.inlineformset_factory(
    BagItProfileBagInfo,
    BagItProfileBagInfoValues,
    fields=("name",),
    extra=1,
    form=BagItProfileBagInfoValuesForm,
)


# Based on https://micropyramid.com/blog/how-to-use-nested-formsets-in-django/
class BaseBagInfoFormset(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseBagInfoFormset, self).add_fields(form, index)

        form.nested = BagItProfileBagInfoValuesFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix="nested_%s_%s"
            % (form.prefix, BagItProfileBagInfoValuesFormset.get_default_prefix()),
        )

    def is_valid(self):
        result = super(BaseBagInfoFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "nested"):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        result = super(BaseBagInfoFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, "nested"):
                if not self._should_delete_form(form):
                    try:
                        form.nested.save(commit=commit)
                    except Exception:
                        result = False
        return result


BagItProfileBagInfoFormset = forms.inlineformset_factory(
    BagItProfile,
    BagItProfileBagInfo,
    fields=("field", "required", "repeatable"),
    extra=1,
    form=BagItProfileBagInfoForm,
    formset=BaseBagInfoFormset,
)
