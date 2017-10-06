from django.urls import reverse, reverse_lazy

from braces.views import GroupRequiredMixin, StaffuserRequiredMixin, SuperuserRequiredMixin, LoginRequiredMixin

class LoggedInMixinDefaults(LoginRequiredMixin):
    login_url = '/app'

class RACAdminMixin(LoggedInMixinDefaults, SuperuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")

class RACUserMixin(LoggedInMixinDefaults, StaffuserRequiredMixin):
    authenticated_redirect_url = reverse_lazy(u"app_home")