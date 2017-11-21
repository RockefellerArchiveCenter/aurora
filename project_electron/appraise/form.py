from django import forms
from orgs.models import Archives

class AppraisalNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = Archives
        fields = ['appraisal_note']
