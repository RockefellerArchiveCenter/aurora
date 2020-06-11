from bag_transfer.accession.models import Accession
from bag_transfer.models import Archives, Organization, User
from bag_transfer.rights.models import RightsStatement
from braces.views import (LoginRequiredMixin, SuperuserRequiredMixin,
                          UserPassesTestMixin)
from django.urls import reverse_lazy


class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = reverse_lazy("login")


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


# UNUSED
class SelfOrManagerMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    authenticated_redirect_url = reverse_lazy("app_home")

    def test_func(self, user):
        return (
            user.is_superuser or user.in_group("managing_archivists") or self.kwargs.get("pk") == str(user.pk)
        )


class OrgReadViewMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    def test_func(self, user):

        if user.is_staff:
            return True

        organization = None
        # Most views are using generics, which in return pass models, so we can hook those in and target the org to remove access to reg users not in org
        if self.request.method == "GET":
            if hasattr(self, "suffix"):
                if self.suffix == "List":
                    return True
            if hasattr(self, "model"):
                if self.model == User:
                    # all staff validate to true above, should pass if == request.user
                    try:
                        u = User.objects.get(pk=self.kwargs.get("pk"))
                        if self.request.user == u:
                            return True
                    except User.DoesNotExist as e:
                        print(e)

                elif self.model == Organization:
                    try:
                        org = Organization.objects.get(pk=self.kwargs.get("pk"))
                        organization = org
                    except Organization.DoesNotExist as e:
                        print(e)

                elif self.model == RightsStatement:
                    try:
                        rights_statement = RightsStatement.objects.get(
                            pk=self.kwargs.get("pk")
                        )
                        organization = rights_statement.organization
                    except RightsStatement.DoesNotExist as e:
                        print(e)

                elif self.model == Archives:
                    try:
                        archive = Archives.objects.get(pk=self.kwargs.get("pk"))
                        organization = archive.organization
                    except Archives.DoesNotExist as e:
                        print(e)

                elif self.model == Accession:
                    try:
                        accession = Accession.objects.get(pk=self.kwargs.get("pk"))
                        organization = accession.organization
                    except Accession.DoesNotExist as e:
                        print(e)

                if organization and self.request.user.organization == organization:
                    return True
        return False
