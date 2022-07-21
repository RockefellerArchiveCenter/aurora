import random
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.test import TestCase, modify_settings, override_settings
from django.urls import reverse

from bag_transfer.models import Organization, User
from bag_transfer.test.helpers import TestMixin


class UserTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    def test_user_model_methods(self):
        """Test user model methods."""
        self.has_privs()
        self.in_group()
        self.is_user_active()
        self.permissions_by_group()
        self.save_test()

    def has_privs(self):
        for username, assert_true, assert_false, privs in [
                ("donor", [], ["is_archivist", "can_appraise", "is_manager"], None),
                ("manager", ["can_accession", "can_appraise", "is_manager"], [], "MANAGING"),
                ("accessioner", ["can_accession"], ["can_appraise", "is_manager"], "ACCESSIONER"),
                ("appraiser", ["can_appraise"], ["is_manager", "can_accession"], "APPRAISER")]:
            user = User.objects.get(username=username)
            for meth in assert_true:
                self.assertTrue(
                    getattr(user, meth)(),
                    "User {} is unable to perform function {}".format(user, meth))
            for meth in assert_false:
                self.assertFalse(
                    getattr(user, meth)(),
                    "User {} should not be able to perform function {}".format(
                        user, meth))
            if privs:
                self.assertTrue(user.has_privs(privs))
            else:
                for priv in ["MANAGING", "ACCESSIONER", "APPRAISER"]:
                    self.assertFalse(user.has_privs(priv))

    def in_group(self):
        group = random.choice(["appraisal_archivists", "managing_archivists", "accessioning_archivists"])
        user = random.choice(User.objects.filter(groups__name=group))
        self.assertTrue(user.in_group(group))
        self.assertFalse(user.in_group("foo"))

    def is_user_active(self):
        user = random.choice(User.objects.filter(is_active=True))
        self.assertEqual(user.is_user_active(user, user.organization), user)
        self.assertEqual(user.is_user_active(user, 1000), None)
        user.is_active = False
        user.save()
        self.assertEqual(user.is_user_active(user, user.organization), None)

    def permissions_by_group(self):
        user = User.objects.get(username="admin")
        self.assertTrue(user.permissions_by_group(User.APPRAISER_GROUPS))
        user = random.choice(User.objects.filter(groups__name="appraisal_archivists"))
        self.assertTrue(user.permissions_by_group(User.APPRAISER_GROUPS))
        self.assertFalse(user.permissions_by_group(User.ACCESSIONER_GROUPS))

    @patch("bag_transfer.lib.RAC_CMD.del_from_org")
    @patch("bag_transfer.lib.RAC_CMD.add2grp")
    @patch("bag_transfer.lib.RAC_CMD.add_user")
    def save_test(self, mock_add_user, mock_add2grp, mock_del):
        """Asserts behaviors for new and updated users."""
        mock_add_user.return_value = True
        user = random.choice(User.objects.all())
        old_org = user.organization
        user.organization = random.choice(Organization.objects.all().exclude(id=old_org.pk))
        user.save()
        mock_del.assert_called_once()
        mock_add2grp.assert_called_once()

        User.objects.create_user(
            username="jdoe",
            is_active=True,
            first_name="John",
            last_name="Doe",
            email="test@example.org",
            organization=random.choice(Organization.objects.all()))
        mock_add_user.assert_called_once()
        self.assertEqual(mock_add2grp.call_count, 2)

    def test_user_views(self):
        """Ensures correct HTTP status codes are received for views."""
        for view in ["users:detail", "users:edit"]:
            self.assert_status_code(
                "get", reverse(view, kwargs={"pk": random.choice(User.objects.filter(transfers__isnull=False)).pk}), 200)
        for view in ["users:add", "users:list", "users:password-change"]:
            self.assert_status_code("get", reverse(view), 200)

        user_data = {
            "is_active": True,
            "first_name": "John",
            "last_name": "Doe",
            "username": "jdoe",
            "email": "test@example.org",
            "organization": random.choice(Organization.objects.all()).pk
        }
        self.assert_status_code("post", reverse("users:add"), 302, data=user_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Aurora account created")

        user_data["active"] = False
        self.assert_status_code(
            "post", reverse("users:edit", kwargs={"pk": random.choice([1, 2, 3])}), 200, data=user_data)

        # ensure logged out users are redirected to splash page
        self.client.logout()
        response = self.assert_status_code("get", reverse("splash"), 302)
        self.assertTrue(response.url.startswith(reverse("login")))


class CognitoTestCase(TestMixin, TestCase):
    fixtures = ["complete.json"]

    @patch("boto3.client")
    @patch("bag_transfer.lib.RAC_CMD.add2grp")
    @patch("bag_transfer.lib.RAC_CMD.add_user")
    @modify_settings(MIDDLEWARE={"append": "bag_transfer.middleware.cognito.CognitoMiddleware"})
    @override_settings(COGNITO_USE=True)
    def test_cognito_create(self, mock_add_user, mock_add2grp, mock_boto):
        mock_username = "cognito"
        mock_email = "cognito@example.org"
        User.objects.create_user(
            username=mock_username,
            is_active=True,
            first_name="Cognito",
            last_name="User",
            email=mock_email,
            organization=random.choice(Organization.objects.all()))
        self.assertEqual(mock_add_user.call_count, 0)
        self.assertEqual(mock_add2grp.call_count, 0)
        mock_boto.assert_called_once_with(
            'cognito-idp',
            aws_access_key_id=settings.COGNITO_ACCESS_KEY,
            aws_secret_access_key=settings.COGNITO_SECRET_KEY,
            region_name=settings.COGNITO_REGION)
        mock_boto().admin_create_user.assert_called_once_with(
            UserPoolId=settings.COGNITO_USER_POOL,
            Username=mock_username,
            UserAttributes=[{'Name': 'email', 'Value': mock_email}],
            DesiredDeliveryMediums=['EMAIL']
        )

    @patch("boto3.client")
    @patch("bag_transfer.lib.RAC_CMD.add2grp")
    @patch("bag_transfer.lib.RAC_CMD.add_user")
    @modify_settings(MIDDLEWARE={"append": "bag_transfer.middleware.cognito.CognitoMiddleware"})
    @override_settings(COGNITO_USE=True)
    def test_cognito_update(self, mock_add_user, mock_add2grp, mock_boto):
        user = User.objects.get(username="admin")
        user.is_active = False
        user.save()
        self.assertEqual(mock_add_user.call_count, 0)
        self.assertEqual(mock_add2grp.call_count, 0)
        mock_boto.assert_called_once_with(
            'cognito-idp',
            aws_access_key_id=settings.COGNITO_ACCESS_KEY,
            aws_secret_access_key=settings.COGNITO_SECRET_KEY,
            region_name=settings.COGNITO_REGION)
        mock_boto().admin_get_user.assert_called_once_with(
            UserPoolId=settings.COGNITO_USER_POOL,
            Username=user.username)
        mock_boto().admin_disable_user.assert_called_once_with(
            UserPoolId=settings.COGNITO_USER_POOL,
            Username=user.username)

    @patch("boto3.client")
    @patch("authlib.integrations.django_client.apps.DjangoOAuth2App.authorize_access_token")
    @patch("authlib.integrations.django_client.apps.DjangoOAuth2App.get")
    @modify_settings(MIDDLEWARE={"append": "bag_transfer.middleware.cognito.CognitoMiddleware"})
    @override_settings(COGNITO_USE=True)
    def test_cognito_middleware(self, mock_get, mock_authorize_token, mock_boto):
        self.client.logout()

        mock_authorize_token.return_value = {
            'id_token': 'NqB65DYkCr93VJw',
            'access_token': 'eyJraWQiOiJdIY1zoh1kRNwg',
            'refresh_token': 'ey7nfxtH9-0k8fw',
            'expires_in': 3600,
            'token_type':
            'Bearer',
            'expires_at': 1658328143}
        mock_get.status_code = 200
        mock_get.return_value.json.return_value = {
            "username": "admin",
            "email": "admin@example.org"
        }

        # inititial redirect
        resp = self.assert_status_code("get", "/app/", 302)
        self.assertTrue(resp.url.startswith(settings.COGNITO_CLIENT['authorize_url']))

        # login on callback
        resp = self.assert_status_code("get", settings.COGNITO_CLIENT_CALLBACK_URL, 302)
