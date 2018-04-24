from django import forms

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.utils.translation import ugettext, ugettext_lazy as _

from orgs.models import User


class OrgUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active', 'first_name', 'last_name', 'email', 'organization', 'groups', 'from_ldap']


class RACSuperUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # NO ORG -- SET TO PRIMARY
        fields = ['is_active','email','groups']


class UserPasswordChangeForm(PasswordChangeForm):
    error_css_class = 'has-error'
    # error_messages['password_incorrect'] = "You entered your current password incorrectly"

    error_messages = dict(PasswordChangeForm.error_messages, **{
        'password_incorrect': _("You entered your current password incorrectly"),
    })

    old_password = forms.CharField(
        required=True,
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please enter your current password'}
        )

    new_password1 = forms.CharField(
        required=True,
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please enter your new password'}
        )
    new_password2 = forms.CharField(
        required=True,
        label='New Password (repeat)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please confirm your new password'}
        )

    def clean_old_password(self):
        if self.user.from_ldap:
            old_password = self.cleaned_data["old_password"]
            if not self.user.check_password_ldap(old_password):
                raise forms.ValidationError(
                    self.error_messages['password_incorrect'],
                    code='password_incorrect',
                    )
            return old_password
        else:
            return super(UserPasswordChangeForm, self).clean_old_password()

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        try:
            self.user.set_password_ldap(password)
        except Exception as e:
            print e
            # raise exception
        else:
            if commit:
                self.user.save()
            return self.user
        return None
