from django import forms
from orgs.models import Archives

class AppraisalNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = Archives
        fields = ['appraisal_note']

    def __init__(self, *args, **kwargs):
        super(AppraisalNoteUpdateForm, self).__init__(*args, **kwargs)
        self.fields['appraisal_note'].widget = forms.Textarea(attrs={'class': 'form-control'})

class AppraiseTransferForm(forms.ModelForm):
    class Meta:
        model = Archives
        fields = ['process_status']

    def __init__(self, *args, **kwargs):
        super(AppraisalNoteUpdateForm, self).__init__(*args, **kwargs)
