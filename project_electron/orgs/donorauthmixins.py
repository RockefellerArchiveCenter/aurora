from orgs.authmixins import LoggedInMixinDefaults
from braces.views import UserPassesTestMixin
from rights.models import RightsStatement

class DonorOrgReadAccessMixin(LoggedInMixinDefaults, UserPassesTestMixin):
    def test_func(self, user):
        if self.request.user.is_staff:
            return True
        organization = None

        # conditionals to make different req types
        if self.model == RightsStatement:
            try:
                rights_statement = RightsStatement.objects.get(pk = self.kwargs.get('pk'))
            except RightsStatement.DoesNotExist as e:
                print e
                return False
            organization = rights_statement.organization


            if self.request.user.organization == organization:
                return True
        return False
