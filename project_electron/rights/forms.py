from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _

from rights.models import *

class RightsForm(forms.ModelForm):
	class Meta:
		model = RightsStatement
		exclude = []
