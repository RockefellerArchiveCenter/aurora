from django.urls import reverse, reverse_lazy

from braces.views import GroupRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin, LoginRequiredMixin, UserPassesTestMixin

class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = '/app'

class ArchivistMixin(LoggedInMixinDefaults, GroupRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")
    group_required = [u"appraisal_archivists", u"accessioning_archivists", u"managing_archivists"]

class AppraisalArchivistMixin(ArchivistMixin, GroupRequiredMixin):
    group_required = u"appraisal_archivists"

class AccessioningArchivistMixin(ArchivistMixin, GroupRequiredMixin):
    group_required = u"accessioning_archivists"

class ManagingArchivistMixin(ArchivistMixin, GroupRequiredMixin):
    group_required = u"managing_archivists"

class SysAdminMixin(LoggedInMixinDefaults, SuperuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")

class SelfOrSuperUserMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")
    def test_func(self, user):
        return (user.is_superuser or self.kwargs.get('pk') == str(user.pk))
