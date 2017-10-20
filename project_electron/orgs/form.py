from django import forms
from orgs.models import User

class OrgUserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['is_active','email','organization','is_org_admin']

# class RACUserUpdateForm(forms.ModelForm):
# 	class Meta:
# 		model = User
# 		fields = ['is_active','email']

class RACSuperUserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		# NO ORG -- SET TO PRIMARY
		fields = ['is_active','email','is_superuser']