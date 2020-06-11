from bag_transfer.models import BagItProfile, Organization, User
from braces.views import (LoginRequiredMixin, SuperuserRequiredMixin,
                          UserPassesTestMixin)
from django.urls import reverse_lazy


class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = "/app"


class ArchivistMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    authenticated_redirect_url = reverse_lazy("app_home")

    def test_func(self, user):
        if user.is_staff:
            return True
        return False


class AppraisalArchivistMixin(ArchivistMixin, UserPassesTestMixin):
    def test_func(self, user):
        return user.has_privs("APPRAISER")


class AccessioningArchivistMixin(ArchivistMixin, UserPassesTestMixin):
    def test_func(self, user):
        return user.has_privs("ACCESSIONER")


class ManagingArchivistMixin(ArchivistMixin, UserPassesTestMixin):
    def test_func(self, user):
        return user.has_privs("MANAGING")


class SysAdminMixin(LoggedInMixinDefaults, SuperuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy("app_home")


class OrgReadViewMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    """Provides read-only access to objects associated with a user's organization.

    Since most of Aurora's views provide a model attribute, we target the Organization
    associated with the object to remove access to non-archivists users not in
    that Organization.
    """

    def test_func(self, user):

        if user.is_staff:
            return True

        organization = None

        if self.request.method == "GET":
            if hasattr(self, "suffix"):
                if self.suffix == "List":
                    return True
            if hasattr(self, "model"):
                if self.model == User:
                    try:
                        if User.objects.get(pk=self.kwargs.get("pk")) == self.user:
                            return True
                    except User.DoesNotExist as e:
                        print(e)

                elif self.model == Organization:
                    try:
                        organization = Organization.objects.get(pk=self.kwargs.get("pk"))
                    except Organization.DoesNotExist as e:
                        print(e)

                elif self.model == BagItProfile:
                    try:
                        profile = BagItProfile.objects.get(pk=self.kwargs.get("pk"))
                        organization = profile.applies_to_organization
                    except BagItProfile.DoesNotExist as e:
                        print(e)

                else:
                    try:
                        obj = self.model.objects.get(pk=self.kwargs.get("pk"))
                        organization = obj.organization
                    except self.model.DoesNotExist as e:
                        print(e)

                if organization and self.request.user.organization == organization:
                    return True
        return False
