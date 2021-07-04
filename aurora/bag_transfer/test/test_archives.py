from bag_transfer.models import Archives, User
from django.test import TestCase
from django.urls import reverse


class BagTestCase(TestCase):
    fixtures = ["complete.json"]

    def setUp(self):
        self.client.force_login(User.objects.get(username="admin"))

    def assert_status_code(self, url, status_code):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status_code, "Unexpected status code {} for url {}".format(resp.status_code, url))

    def assert_all_views(self, organization=None):
        archives = Archives.objects.filter(organization=organization) if organization else Archives.objects.all()
        for view in ["transfers:list", "transfers:data", "transfers:datatable", "app_home"]:
            self.assert_status_code(reverse(view), 200)
        for arc in archives:
            self.assert_status_code(reverse("transfers:detail", kwargs={"pk": arc.pk}), 200)
        self.assert_status_code("{}?q=user".format(reverse("transfers:datatable")), 200)

    def test_views(self):
        """Asserts views return expected responses for admin and donor users."""
        self.assert_all_views()
        self.client.logout()
        donor_user = User.objects.get(username="donor")
        self.client.force_login(donor_user)
        self.assert_all_views(donor_user.organization)

    def test_model_methods(self):
        # L260 - L533
        pass
        # bag_or_failed_name
        # gen_identifier
        # initial_save (Can this just be a save with a default value on process_status?)
        # get_error_codes
        # get_errors
        # get_bag_validations
        # get_bag_failure
        # get_additional_errors
        # get_transfer_logs
        # setup_save
        # save_mtm_fields (needs renaming)
        # save_bag_data
        # get_bag_data
        # get_records_creators
        # assign_rights
