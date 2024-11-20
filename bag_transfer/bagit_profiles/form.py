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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['external_description'].initial = "BagIt Profile for transferring records to the Rockefeller Archive Center."
        self.fields['serialization'].required = True
        self.fields['serialization'].choices = [choice for choice in self.fields['serialization'].choices if choice[0]]  # Exclude blank choice


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
