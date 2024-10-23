from django import forms

from bag_transfer.models import (AcceptBagItVersion, AcceptSerialization,
                                 BagItProfile, BagItProfileBagInfo,
                                 BagItProfileBagInfoValues, ManifestsAllowed,
                                 ManifestsRequired, TagFilesRequired,
                                 TagManifestsRequired)


class BagItProfileForm(forms.ModelForm):
    class Meta:
        model = BagItProfile
        exclude = []
        labels = {
            "external_description": "Description",
            "allow_fetch": "Allow Fetch.txt?",
            "serialization": "Serialization Allowed?",
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
        }
        help_texts = {
            "external_description": "A short description of this BagIt Profile.",
            "serialization": "Specify whether serialization of bags is required, forbidden, or optional.",
        }
    # Set most common initial values

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['external_description'].initial = "BagIt Profile for transferring records to the Rockefeller Archive Center."
        self.fields['serialization'].required = True


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
            "field": forms.widgets.Select(),
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


class ManifestsAllowedForm(forms.ModelForm):
    class Meta:
        model = ManifestsAllowed
        fields = ("name",)
        widgets = {
            "name": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "checkbox checkbox--blue"})
        }
        help_texts = {
            "name": "Select at least one."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend_text = "Allowed algorithm(s) for manifest files *"
        self.help_text_id = "manifests_allowed-help"
        self.fields['name'].required = True


class ManifestsRequiredForm(forms.ModelForm):
    class Meta:
        model = ManifestsRequired
        fields = ("name",)
        widgets = {
            "name": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "checkbox checkbox--blue"})
        }
        help_texts = {
            "name": "If no value is selected, any algorithm is valid."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend_text = "Manifests Required"
        self.help_text_id = "manifests_required-help"


class AcceptSerializationForm(forms.ModelForm):
    class Meta:
        model = AcceptSerialization
        fields = ("name",)
        widgets = {
            "name": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "checkbox checkbox--blue"})
        }
        help_texts = {
            "name": "Select all accepted formats. If no values are selected, the serialization format will not be checked."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend_text = "Serializations Accepted"
        self.help_text_id = "serializations_accepted-help"


class AcceptBagItVersionForm(forms.ModelForm):
    class Meta:
        model = AcceptBagItVersion
        fields = ("name",)
        widgets = {
            "name": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "checkbox checkbox--blue"})
        }
        help_texts = {
            "name": "Select all versions of the BagIt Specification accepted. If no values are selected, the BagIt version will not be checked."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend_text = "BagIt Versions Accepted"
        self.help_text_id = "bagit_versions_accepted-help"


class TagManifestsRequiredForm(forms.ModelForm):
    class Meta:
        model = TagManifestsRequired
        fields = ("name",)
        widgets = {
            "name": forms.widgets.CheckboxSelectMultiple(
                attrs={"class": "checkbox checkbox--blue"})
        }
        help_texts = {
            "name": "If no values are selected, the tag format algorithm will not be checked."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend_text = "Tag Manifests Required"
        self.help_text_id = "tag_manifests_required-help"


class TagFilesRequiredForm(forms.ModelForm):
    class Meta:
        model = TagFilesRequired
        fields = ("name",)
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={"aria-describedby": "tag_files-help", "aria-labelledby": "tag_files-label"})
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

ManifestsAllowedFormset = forms.inlineformset_factory(
    BagItProfile,
    ManifestsAllowed,
    fields=("name",),
    extra=1,
    max_num=len(ManifestsAllowed.MANIFESTS_ALLOWED_CHOICES),
    min_num=1,
    validate_min=True,
    form=ManifestsAllowedForm,
)

ManifestsRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    ManifestsRequired,
    fields=("name",),
    extra=1,
    max_num=len(ManifestsRequired.MANIFESTS_REQUIRED_CHOICES),
    form=ManifestsRequiredForm,
)

AcceptSerializationFormset = forms.inlineformset_factory(
    BagItProfile,
    AcceptSerialization,
    fields=("name",),
    extra=1,
    max_num=len(AcceptSerialization.ACCEPT_SERIALIZATION_CHOICES),
    form=AcceptSerializationForm,
)

AcceptBagItVersionFormset = forms.inlineformset_factory(
    BagItProfile,
    AcceptBagItVersion,
    fields=("name",),
    extra=1,
    max_num=len(AcceptBagItVersion.BAGIT_VERSION_NAME_CHOICES),
    form=AcceptBagItVersionForm,
)

TagManifestsRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    TagManifestsRequired,
    fields=("name",),
    extra=1,
    max_num=len(TagManifestsRequired.TAG_MANIFESTS_REQUIRED_CHOICES),
    form=TagManifestsRequiredForm,
)

TagFilesRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    TagFilesRequired,
    fields=("name",),
    extra=1,
    form=TagFilesRequiredForm,
)
