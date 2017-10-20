from django.urls import reverse, reverse_lazy

from braces.views import GroupRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin, LoginRequiredMixin, UserPassesTestMixin

class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = '/app'

class RACAdminMixin(LoggedInMixinDefaults, SuperuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")

class RACUserMixin(LoggedInMixinDefaults, StaffuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")

class SelfOrSuperUserMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")
    def test_func(self, user):
        return (user.is_superuser or self.kwargs.get('pk') == str(user.pk))
