from django import forms

from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import ugettext, ugettext_lazy as _

from bag_transfer.models import User


class OrgUserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active', 'username', 'first_name', 'last_name', 'email', 'organization', 'groups']
        widgets = {
            'username': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'email': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
            'organization': forms.widgets.Select(attrs={'class': 'form-control'}),
        }


class OrgUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active', 'username', 'first_name', 'last_name', 'email', 'organization', 'groups']
        widgets = {
            'username': forms.widgets.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'email': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
            'organization': forms.widgets.Select(attrs={'class': 'form-control'}),
        }


class RACSuperUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active', 'username', 'first_name', 'last_name', 'email', 'groups']
        widgets = {
            'username': forms.widgets.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.widgets.TextInput(attrs={'class': 'form-control'}),
            'email': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    error_css_class = 'has-error'

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


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
            required=True,
            widget=forms.EmailInput(attrs={'class': 'form-control has-feedback'}),
            error_messages={'required': 'Please enter your email'})


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
                    required=True, label='New Password',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                    error_messages={'required': 'Please enter your new password'})
    new_password2 = forms.CharField(
                    required=True, label='New Password (repeat)',
                    widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                    error_messages={'required': 'Please confirm your new password'})
