from django import forms
from orgs.models import Archives

class AppraisalNoteUpdateForm(forms.ModelForm):
    class Meta:
        model = Archives
        fields = ['appraisal_note']

    def __init__(self, *args, **kwargs):
        form = super(AppraisalNoteUpdateForm, self).__init__(*args, **kwargs)
        for visible in form.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
