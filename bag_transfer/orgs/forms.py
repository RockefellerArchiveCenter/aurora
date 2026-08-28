from django import forms

from bag_transfer.models import Organization

EMPTY_LABEL = "--- Select an acquisition type ---"


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "acquisition_type"]
        labels = {
            "name": "Organization Name",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acquisition_type"].choices = [
            ("", EMPTY_LABEL)
        ] + list(Organization.ACQUISITION_TYPE_CHOICES)


class OrganizationUpdateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["is_active", "name", "acquisition_type"]
        labels = {
            "name": "Organization Name",
        }
        widgets = {
            "is_active": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["acquisition_type"].choices = [
            ("", EMPTY_LABEL)
        ] + list(Organization.ACQUISITION_TYPE_CHOICES)
