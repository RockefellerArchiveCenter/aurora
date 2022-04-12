import random

from django.http import HttpRequest, HttpResponse
from django.test import TestCase

from bag_transfer.mixins.authmixins import ArchivistMixin, OrgReadViewMixin
from bag_transfer.mixins.formatmixins import CSVResponseMixin
from bag_transfer.models import BagItProfile, Organization, Transfer, User


class MixinTestCase(TestCase):
    fixtures = ["complete.json"]

    def test_csv_mixin(self):
        """Asserts that the CSV mixin returns a streaming CSV response."""
        csv = CSVResponseMixin().render_to_csv(["foo", "bar", "baz"])
        self.assertTrue(isinstance(csv, HttpResponse))

    def test_archivist_mixin(self):
        """Ensures that ArchivistMixin correctly tests whether user is_staff."""
        mixin = ArchivistMixin()
        self.assertTrue(mixin.test_func(User(is_staff=True)))
        self.assertFalse(mixin.test_func(User(is_staff=False)))
        self.assertFalse(mixin.test_func(User()))

    def test_org_read_view_mixin(self):
        """Asserts that the OrgReadViewMixin correctly determines permissions."""
        non_staff_user = random.choice(User.objects.filter(is_staff=False))
        mixin = OrgReadViewMixin()
        self.assertTrue(mixin.test_func(User(is_staff=True)))
        mixin.request = HttpRequest()
        mixin.request.method = "POST"
        self.assertFalse(mixin.test_func(non_staff_user))
        mixin.request.method = "GET"
        mixin.suffix = "List"
        self.assertTrue(mixin.test_func(User(non_staff_user)))

        mixin.suffix = "Detail"
        mixin.request.user = non_staff_user
        self.object_permissions(mixin, non_staff_user)
        self.bagit_profile_permissions(mixin, non_staff_user)

    def object_permissions(self, mixin, non_staff_user):
        for obj, model_cls in [
                (non_staff_user, User),
                (non_staff_user.organization, Organization),
                (random.choice(Transfer.objects.filter(organization=non_staff_user.organization)), Transfer)]:
            mixin.model = model_cls
            mixin.user = non_staff_user
            failed_obj = (
                random.choice(Organization.objects.exclude(pk=obj.pk)) if model_cls == Organization else
                random.choice(model_cls.objects.exclude(organization=non_staff_user.organization)))
            mixin.kwargs = {"pk": obj.pk}
            self.assertTrue(mixin.test_func(non_staff_user))
            mixin.kwargs["pk"] = failed_obj.pk
            self.assertFalse(mixin.test_func(non_staff_user))
            mixin.kwargs["pk"] = 1000
            self.assertFalse(mixin.test_func(non_staff_user))

    def bagit_profile_permissions(self, mixin, non_staff_user):
        org_profile = random.choice(BagItProfile.objects.filter(organization=non_staff_user.organization))
        non_org_profile = random.choice(BagItProfile.objects.exclude(organization=non_staff_user.organization))
        mixin.model = BagItProfile
        mixin.user = non_staff_user
        mixin.kwargs = {"pk": org_profile.pk}
        self.assertTrue(mixin.test_func(non_staff_user))
        mixin.kwargs["pk"] = non_org_profile.pk
        self.assertFalse(mixin.test_func(non_staff_user))
        mixin.kwargs["pk"] = 1000
        self.assertFalse(mixin.test_func(non_staff_user))
