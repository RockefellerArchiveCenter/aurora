from bag_transfer.lib.RAC_CMD import set_server_password
from bag_transfer.mixins.authmixins import (ArchivistMixin,
                                            ManagingArchivistMixin,
                                            OrgReadViewMixin)
from bag_transfer.mixins.viewmixins import PageTitleMixin
from bag_transfer.models import Organization, Transfer, User
from bag_transfer.users.form import (OrgUserCreateForm, OrgUserUpdateForm,
                                     RACSuperUserUpdateForm,
                                     UserPasswordChangeForm,
                                     UserPasswordResetForm,
                                     UserSetPasswordForm)
from braces.views import AnonymousRequiredMixin
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)


class SplashView(AnonymousRequiredMixin, TemplateView):
    def get(self, request):
        return redirect("login")


class UsersListView(PageTitleMixin, ArchivistMixin, SuccessMessageMixin, ListView):
    template_name = "users/list.html"
    page_title = "Users"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users_list"] = [{"users": User.objects.all().order_by("username")}]
        context["org_users_list"] = Organization.users_by_org()
        return context


class UsersCreateView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = "users/update.html"
    page_title = "Create New User"
    model = User
    success_message = "New User Saved!"
    form_class = OrgUserCreateForm

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """Set a random password to and send a password reset email."""
        password_form = PasswordResetForm({"email": self.request.POST.get("email")})
        if password_form.is_valid():
            try:
                password_form.save(
                    request=self.request,
                    subject_template_name="users/password_initial_set_subject.txt",
                    email_template_name="users/password_initial_set_email.html",
                )
            except Exception:
                messages.error(self.request, "Unable to send email to new user because SMTP settings are not properly configured.")
        return super().form_valid(form)


class UsersDetailView(PageTitleMixin, OrgReadViewMixin, DetailView):
    template_name = "users/detail.html"
    page_title = "User Profile"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uploads"] = []
        transfers = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            user_uploaded=context["object"],
        ).order_by("-created_time")[:9]
        for transfer in transfers:
            transfer.bag_info_data = transfer.bag_data
            context["uploads"].append(transfer)
        context["uploads_count"] = Transfer.objects.filter(
            process_status__gte=Transfer.TRANSFER_COMPLETED,
            user_uploaded=context["object"],
        ).count()
        return context


class UsersEditView(PageTitleMixin, ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = "users/update.html"
    model = User
    success_message = "Your changes have been saved!"

    def get_form_class(self):
        return RACSuperUserUpdateForm if self.object.is_staff else OrgUserUpdateForm

    def get_page_title(self, context):
        return "Edit {}".format(self.object.username)

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.object.pk})


class UserPasswordChangeView(PageTitleMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = "users/password_change.html"
    page_title = "Change Password"
    model = User
    success_message = "New password saved."
    form_class = UserPasswordChangeForm

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})

    def form_valid(self, form):
        """Set the user's server password."""
        set_server_password(form.user.username, form.cleaned_data["new_password1"])
        return super().form_valid(form)


class UserPasswordResetView(PageTitleMixin, AnonymousRequiredMixin, PasswordResetView):
    template_name = "users/password_reset_form.html"
    page_title = "Reset Password"
    form_class = UserPasswordResetForm


class UserPasswordResetDoneView(PageTitleMixin, AnonymousRequiredMixin, PasswordResetDoneView):
    template_name = "users/password_reset_done.html"
    page_title = "Password Reset Email Sent"


class UserPasswordResetConfirmView(PageTitleMixin, AnonymousRequiredMixin, PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    page_title = "Confirm Password"
    form_class = UserSetPasswordForm

    def form_valid(self, form):
        """Set the user's server password."""
        set_server_password(form.user.username, form.cleaned_data["new_password1"])
        return super().form_valid(form)


class UserPasswordResetCompleteView(PageTitleMixin, AnonymousRequiredMixin, PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
    page_title = "Password Reset Complete"
