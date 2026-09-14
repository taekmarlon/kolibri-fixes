import json
from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import RequestFactory
from django.test import TestCase

from kolibri.core.h5p.proxy import H5PProxyView


class H5PProxyViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = H5PProxyView.as_view()

    @patch("kolibri.core.h5p.proxy.requests.request")
    def test_post_new_json_response_not_corrupted_by_bridge(self, mock_request):
        # Simulate Express returning JSON string with default text/html content-type
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "text/html; charset=utf-8"}
        expected_json = {"contentId": 1824971442}
        mock_resp.content = json.dumps(expected_json).encode("utf-8")
        mock_resp.text = json.dumps(expected_json)
        mock_request.return_value = mock_resp

        request = self.factory.post(
            "/h5p/new",
            data=json.dumps({"library": "H5P.TrueFalse 1.8", "params": {}}),
            content_type="application/json",
        )
        response = self.view(request, path="new")

        self.assertEqual(response.status_code, 200)
        # Verify body is valid JSON without appended HTML/scripts
        raw_body = response.content.decode("utf-8")
        parsed = json.loads(raw_body)
        self.assertEqual(parsed.get("contentId"), 1824971442)
        self.assertNotIn("<style>", raw_body)
        self.assertNotIn("<script>", raw_body)
        self.assertEqual(response["Content-Type"], "application/json")

    @patch("kolibri.core.h5p.proxy.requests.request")
    def test_authenticated_user_headers_forwarded(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "text/html"}
        mock_resp.content = b"<html><body>OK</body></html>"
        mock_resp.text = "<html><body>OK</body></html>"
        mock_request.return_value = mock_resp

        request = self.factory.get("/h5p/new")
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.id = "coach-123"
        mock_user.full_name = "Coach Sarah"
        mock_user.username = "csarah"
        mock_user.email = "coach@school.edu"
        request.user = mock_user

        response = self.view(request, path="new")
        self.assertEqual(response.status_code, 200)

        # Verify mock_request received forwarded user headers
        call_kwargs = mock_request.call_args[1]
        forwarded_headers = call_kwargs.get("headers", {})
        self.assertEqual(forwarded_headers.get("X-Kolibri-User-Id"), "coach-123")
        self.assertEqual(forwarded_headers.get("X-Kolibri-User-Name"), "Coach Sarah")
        self.assertEqual(
            forwarded_headers.get("X-Kolibri-User-Email"), "coach@school.edu"
        )
