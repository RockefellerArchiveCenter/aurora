from unittest.mock import patch

from bag_transfer.lib.clients import (ArchivesSpaceClient,
                                      ArchivesSpaceClientError)
from django.test import TestCase


class ClientTestCase(TestCase):

    @patch("requests.Session.get")
    @patch("requests.Session.post")
    def test_get_resources(self, mock_post, mock_get):
        """Ensure client handles requests and errors."""
        return_value = {}
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = '{"session": "12345"}'
        client = ArchivesSpaceClient("baseurl", "username", "password", "repo_id")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = return_value
        self.assertEqual(client.get_resource("1"), return_value)
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {"error": "foobar"}
        with self.assertRaisesMessage(ArchivesSpaceClientError, "foobar"):
            client.get_resource("1")
