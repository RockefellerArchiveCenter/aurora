from django import forms

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.utils.translation import ugettext, ugettext_lazy as _

from bag_transfer.models import BagItProfile, BagItProfileBagInfo, BagItProfileBagInfoValues, ManifestsRequired, AcceptSerialization, AcceptBagItVersion, TagManifestsRequired, TagFilesRequired


class BagItProfileForm(forms.ModelForm):
    class Meta:
        model = BagItProfile
        exclude = []
        labels = {
            'external_description': 'Description',
            'allow_fetch': 'Allow Fetch.txt?',
            'serialization': 'Serialization allowed?'
        }
        widgets = {
            'applies_to_organization': forms.widgets.HiddenInput(),
            'contact_email': forms.widgets.HiddenInput(),
            'source_organization': forms.widgets.HiddenInput(),
            'version': forms.widgets.HiddenInput(),
            'bagit_profile_identifier': forms.widgets.HiddenInput(),
            'external_description': forms.widgets.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'serialization': forms.widgets.Select(attrs={'class': 'form-control', 'aria-labelledby': 'id_serialization-label'}),
        }
        help_texts = {
            'external_description': 'A short description of this BagIt Profile.',
            'serialization': 'Specify whether serialization of bags is required, forbidden, or optional.',
        }


class BagItProfileBagInfoForm(forms.ModelForm):
    class Meta:
        model = BagItProfileBagInfo
        exclude = []
        labels = {
            'field': 'Field',
            'required': 'Required?',
            'repeatable': 'Repeatable?',
        }
        widgets = {
            'field': forms.widgets.Select(attrs={'class': 'form-control multi-value'}),
            'required': forms.widgets.CheckboxInput(),
            'repeatable': forms.widgets.CheckboxInput(),
        }


class BagItProfileBagInfoValuesForm(forms.ModelForm):
    class Meta:
        model = BagItProfileBagInfoValues
        fields = ('name',)
        widgets = {'name': forms.widgets.TextInput(attrs={'class': 'form-control multi-value', 'aria-labelledby': 'values-label'})}


class ManifestsRequiredForm(forms.ModelForm):
    class Meta:
        model = ManifestsRequired
        fields = ('name',)
        widgets = {'name': forms.widgets.Select(attrs={'class': 'form-control multi-value', 'aria-labelledby': 'manifests-label'})}


class AcceptSerializationForm(forms.ModelForm):
    class Meta:
        model = AcceptSerialization
        fields = ('name',)
        widgets = {'name': forms.widgets.Select(attrs={'class': 'form-control multi-value', 'aria-labelledby': 'serialization-label'})}


class AcceptBagItVersionForm(forms.ModelForm):
    class Meta:
        model = AcceptBagItVersion
        fields = ('name',)
        widgets = {'name': forms.widgets.Select(attrs={'class': 'form-control multi-value', 'aria-labelledby': 'version-label'})}


class TagManifestsRequiredForm(forms.ModelForm):
    class Meta:
        model = TagManifestsRequired
        fields = ('name',)
        widgets = {'name': forms.widgets.Select(attrs={'class': 'form-control multi-value', 'aria-labelledby': 'tag_manifests-label'})}


class TagFilesRequiredForm(forms.ModelForm):
    class Meta:
        model = TagFilesRequired
        fields = ('name',)
        widgets = {'name': forms.widgets.TextInput(attrs={'class': 'form-control', 'aria-labelledby': 'tag_files-label'})}

BagItProfileBagInfoValuesFormset = forms.inlineformset_factory(
    BagItProfileBagInfo,
    BagItProfileBagInfoValues,
    fields=('name',),
    extra=1,
    form=BagItProfileBagInfoValuesForm
)


# Based on https://micropyramid.com/blog/how-to-use-nested-formsets-in-django/
class BaseBagInfoFormset(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(BaseBagInfoFormset, self).add_fields(form, index)

        form.nested = BagItProfileBagInfoValuesFormset(
                        instance=form.instance,
                        data=form.data if form.is_bound else None,
                        files=form.files if form.is_bound else None,
                        prefix='nested_%s_%s' % (
                            form.prefix,
                            BagItProfileBagInfoValuesFormset.get_default_prefix()),

                        )

    def is_valid(self):
        result = super(BaseBagInfoFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        result = super(BaseBagInfoFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    try:
                        form.nested.save(commit=commit)
                    except:
                        result = False
        return result

BagItProfileBagInfoFormset = forms.inlineformset_factory(
    BagItProfile,
    BagItProfileBagInfo,
    fields=('field', 'required', 'repeatable'),
    extra=1,
    form=BagItProfileBagInfoForm,
    formset=BaseBagInfoFormset
)

ManifestsRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    ManifestsRequired,
    fields=('name',),
    extra=1,
    max_num=2,
    form=ManifestsRequiredForm,
)

AcceptSerializationFormset = forms.inlineformset_factory(
    BagItProfile,
    AcceptSerialization,
    fields=('name',),
    extra=1,
    max_num=3,
    form=AcceptSerializationForm,
)

AcceptBagItVersionFormset = forms.inlineformset_factory(
    BagItProfile,
    AcceptBagItVersion,
    fields=('name',),
    extra=1,
    max_num=2,
    form=AcceptBagItVersionForm,
)

TagManifestsRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    TagManifestsRequired,
    fields=('name',),
    extra=1,
    max_num=2,
    form=TagManifestsRequiredForm,
)

TagFilesRequiredFormset = forms.inlineformset_factory(
    BagItProfile,
    TagFilesRequired,
    fields=('name',),
    extra=1,
    form=TagFilesRequiredForm,
)
