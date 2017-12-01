from django import forms

from django.utils.translation import ugettext, ugettext_lazy as _

from orgs.models import User

class RightsForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['is_active']
