from unittest.mock import MagicMock, patch

import pytest

from functions.slack_notifier.slack_client import get_slack_webhook_url, send_to_slack


class TestGetSlackWebhookUrl:
    def test_valid_webhook_url(self):
        with patch.dict(
            "os.environ", {"SLACK_WEBHOOK_ALARMS_URL": "https://hooks.slack.com/test"}
        ):
            result = get_slack_webhook_url()
            assert result == "https://hooks.slack.com/test"

    def test_webhook_url_with_whitespace(self):
        with patch.dict(
            "os.environ", {"SLACK_WEBHOOK_ALARMS_URL": "  https://hooks.slack.com/test  "}
        ):
            result = get_slack_webhook_url()
            assert result == "https://hooks.slack.com/test"

    def test_missing_webhook_url(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                ValueError, match="SLACK_WEBHOOK_ALARMS_URL environment variable not set"
            ):
                get_slack_webhook_url()

    def test_empty_webhook_url(self):
        with patch.dict("os.environ", {"SLACK_WEBHOOK_ALARMS_URL": ""}):
            with pytest.raises(
                ValueError, match="SLACK_WEBHOOK_ALARMS_URL environment variable not set"
            ):
                get_slack_webhook_url()

    def test_webhook_url_only_whitespace(self):
        with patch.dict("os.environ", {"SLACK_WEBHOOK_ALARMS_URL": "   "}):
            with pytest.raises(
                ValueError, match="SLACK_WEBHOOK_ALARMS_URL environment variable not set"
            ):
                get_slack_webhook_url()


class TestSendToSlack:
    def test_successful_send(self):
        mock_response = MagicMock()
        mock_response.status = 200

        with patch("functions.slack_notifier.slack_client.http") as mock_http:
            mock_http.request.return_value = mock_response
            result = send_to_slack("https://hooks.slack.com/test", {"text": "test"})

            assert result is True
            mock_http.request.assert_called_once()

    def test_failed_send_non_200(self):
        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.data.decode.return_value = "Bad Request"

        with patch("functions.slack_notifier.slack_client.http") as mock_http:
            mock_http.request.return_value = mock_response
            result = send_to_slack("https://hooks.slack.com/test", {"text": "test"})

            assert result is False

    def test_exception_during_send(self):
        with patch("functions.slack_notifier.slack_client.http") as mock_http:
            mock_http.request.side_effect = Exception("Network error")
            result = send_to_slack("https://hooks.slack.com/test", {"text": "test"})

            assert result is False

    def test_json_serialization_failure(self):
        non_serializable = {"text": object()}
        result = send_to_slack("https://hooks.slack.com/test", non_serializable)

        assert result is False
