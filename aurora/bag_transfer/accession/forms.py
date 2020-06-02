from bag_transfer.accession.models import Accession
from bag_transfer.models import RecordCreators
from django import forms


class AccessionForm(forms.ModelForm):
    class Meta:
        model = Accession
        exclude = ("accession_date",)
        labels = {
            "resource": "Related Resource",
            "title": "Title",
            "start_date": "Start Date",
            "end_date": "End Date",
            "description": "Content Description",
            "access_restrictions": "Access Restrictions Note",
            "use_restrictions": "Use Restrictions Note",
        }
        help_texts = {}
        widgets = {
            "title": forms.widgets.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.widgets.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "description": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "access_restrictions": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "use_restrictions": forms.widgets.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "resource": forms.widgets.HiddenInput(),
            "accession_number": forms.widgets.HiddenInput(),
            "extent_files": forms.widgets.HiddenInput(),
            "extent_size": forms.widgets.HiddenInput(),
            "acquisition_type": forms.widgets.HiddenInput(),
            "appraisal_note": forms.widgets.HiddenInput(),
            "organization": forms.widgets.HiddenInput(),
            "language": forms.widgets.HiddenInput(),
            "creators": forms.widgets.MultipleHiddenInput(),
        }


CreatorsFormSet = forms.modelformset_factory(
    RecordCreators,
    fields=("name", "type"),
    extra=0,
    widgets={
        "name": forms.widgets.TextInput(attrs={"class": "form-control col-sm-8 disabled", "disabled":"True"}),
        "type": forms.widgets.Select(attrs={"class": "form-control"}),
    },
)
