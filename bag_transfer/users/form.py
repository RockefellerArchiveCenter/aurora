import boto3
from django import forms
from django.conf import settings
from django.contrib.auth.forms import (PasswordChangeForm, PasswordResetForm,
                                       SetPasswordForm)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from bag_transfer.models import User


class OrgUserCreateForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "is_active",
            "is_org_admin",
            "username",
            "first_name",
            "last_name",
            "email",
            "organization",
            "groups",
        ]
        help_texts = {
            "is_org_admin": "Should this user be assigned organization administrator privileges?"
        }
        widgets = {
            "is_active": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "is_org_admin": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "username": forms.widgets.TextInput(),
            "first_name": forms.widgets.TextInput(),
            "last_name": forms.widgets.TextInput(),
            "email": forms.widgets.EmailInput(),
            "organization": forms.widgets.Select(),
        }


class OrgUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "is_active",
            "is_org_admin",
            "username",
            "first_name",
            "last_name",
            "email",
            "organization",
            "groups",
        ]
        help_texts = {
            "is_org_admin": "Should this user be assigned organization administrator privileges?"
        }
        widgets = {
            "is_active": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "is_org_admin": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "username": forms.widgets.TextInput(
                attrs={"readonly": "readonly"}
            ),
            "first_name": forms.widgets.TextInput(),
            "last_name": forms.widgets.TextInput(),
            "email": forms.widgets.EmailInput(),
            "organization": forms.widgets.Select(),
        }


class RACSuperUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["is_active", "is_org_admin", "username", "first_name", "last_name", "email", "groups"]
        help_texts = {
            "is_org_admin": "Should this user be assigned organization administrator privileges?"
        }
        widgets = {
            "is_active": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "is_org_admin": forms.widgets.CheckboxInput(attrs={"class": "checkbox checkbox--blue"}),
            "username": forms.widgets.TextInput(
                attrs={"readonly": "readonly"}
            ),
            "first_name": forms.widgets.TextInput(),
            "last_name": forms.widgets.TextInput(),
            "email": forms.widgets.EmailInput(),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    error_css_class = "has-error"

    error_messages = dict(
        PasswordChangeForm.error_messages,
        **{"password_incorrect": _("You entered your current password incorrectly")}
    )

    old_password = forms.CharField(
        required=False,
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={"required": "Please enter your current password"},
    )

    new_password1 = forms.CharField(
        required=True,
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={"required": "Please enter your new password"},
    )
    new_password2 = forms.CharField(
        required=True,
        label="New Password (repeat)",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={"required": "Please confirm your new password"},
    )

    def clean_old_password(self):
        """Custom behavior for old_password field.

        Only validates current password if using local auth.
        """
        data = self.cleaned_data['old_password']
        if settings.COGNITO_USE:
            if not len(data):
                raise ValidationError("Please enter your current password")
            else:
                pass
        else:
            super().clean_old_password()
        return data

    def clean(self):
        """Custom behavior for cleaning form data.

        Attempts to update password in Cognito, raises validation errors if
        errors are encountered.
        """
        cleaned_data = super().clean()

        if settings.COGNITO_USE:
            cognito_client = boto3.client(
                'cognito-idp',
                aws_access_key_id=settings.COGNITO_ACCESS_KEY,
                aws_secret_access_key=settings.COGNITO_SECRET_KEY,
                region_name=settings.COGNITO_REGION)
            try:
                cognito_client.change_password(
                    PreviousPassword=cleaned_data.get("old_password"),
                    ProposedPassword=cleaned_data.get("new_password1"),
                    AccessToken=self.user.token["access_token"]
                )
            except cognito_client.exceptions.InvalidPasswordException as e:
                self.add_error("new_password1", f"The new password is invalid. {e.response['message']}")
                self.add_error("new_password2", f"The new password is invalid. {e.response['message']}")
            except cognito_client.exceptions.NotAuthorizedException:
                self.add_error("old_password", "You entered your current password incorrectly")
            except Exception as e:
                raise ValidationError(f"An error occurred: {e.response['message']}")
        return cleaned_data


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control has-feedback"}),
        error_messages={"required": "Please enter your email"},
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        required=True,
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={"required": "Please enter your new password"},
    )
    new_password2 = forms.CharField(
        required=True,
        label="New Password (repeat)",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        error_messages={"required": "Please confirm your new password"},
    )
