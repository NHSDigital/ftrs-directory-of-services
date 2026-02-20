import json
from unittest.mock import MagicMock, patch

import pytest

from functions.slack_alarm_handler import AlarmProcessingError, lambda_handler


class TestLambdaHandler:
    @patch("functions.slack_alarm_handler.send_to_slack")
    @patch("functions.slack_alarm_handler.build_slack_message")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_successful_processing(
        self, mock_webhook, mock_build_message, mock_send
    ):
        mock_webhook.return_value = "https://hooks.slack.com/test"
        mock_build_message.return_value = {"text": "test"}
        mock_send.return_value = True

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm", "NewStateValue": "ALARM"}
                        )
                    }
                }
            ]
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        assert "Processed 1 record(s)" in result["body"]
        mock_send.assert_called_once()

    def test_no_records_in_event(self):
        event = {"Records": []}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "No records found in event" in result["body"]

    def test_missing_records_key(self):
        event = {}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 400
        assert "No records found in event" in result["body"]

    @patch("functions.slack_alarm_handler.send_to_slack")
    @patch("functions.slack_alarm_handler.build_slack_message")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_empty_sns_message_skipped(
        self, mock_webhook, mock_build_message, mock_send
    ):
        mock_webhook.return_value = "https://hooks.slack.com/test"

        event = {"Records": [{"Sns": {"Message": ""}}]}

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        mock_send.assert_not_called()

    @patch("functions.slack_alarm_handler.send_to_slack")
    @patch("functions.slack_alarm_handler.build_slack_message")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_multiple_records_all_success(
        self, mock_webhook, mock_build_message, mock_send
    ):
        mock_webhook.return_value = "https://hooks.slack.com/test"
        mock_build_message.return_value = {"text": "test"}
        mock_send.return_value = True

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm-1", "NewStateValue": "ALARM"}
                        )
                    }
                },
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm-2", "NewStateValue": "ALARM"}
                        )
                    }
                },
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm-3", "NewStateValue": "ALARM"}
                        )
                    }
                },
            ]
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        assert "Processed 3 record(s)" in result["body"]
        assert mock_send.call_count == 3

    @patch("functions.slack_alarm_handler.send_to_slack")
    @patch("functions.slack_alarm_handler.build_slack_message")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_failed_slack_send(self, mock_webhook, mock_build_message, mock_send):
        mock_webhook.return_value = "https://hooks.slack.com/test"
        mock_build_message.return_value = {"text": "test"}
        mock_send.return_value = False

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm", "NewStateValue": "ALARM"}
                        )
                    }
                }
            ]
        }

        with pytest.raises(AlarmProcessingError, match="Failed to process 1 record"):
            lambda_handler(event, None)

    @patch("functions.slack_alarm_handler.send_to_slack")
    @patch("functions.slack_alarm_handler.build_slack_message")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_multiple_records_partial_failure(
        self, mock_webhook, mock_build_message, mock_send
    ):
        mock_webhook.return_value = "https://hooks.slack.com/test"
        mock_build_message.return_value = {"text": "test"}
        mock_send.side_effect = [True, False]

        event = {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm-1", "NewStateValue": "ALARM"}
                        )
                    }
                },
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"AlarmName": "test-alarm-2", "NewStateValue": "ALARM"}
                        )
                    }
                },
            ]
        }

        with pytest.raises(AlarmProcessingError, match="Failed to process 1 record"):
            lambda_handler(event, None)

    @patch("functions.slack_alarm_handler.parse_cloudwatch_alarm")
    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_exception_during_processing(self, mock_webhook, mock_parse):
        mock_webhook.return_value = "https://hooks.slack.com/test"
        mock_parse.side_effect = Exception("Parse error")

        event = {
            "Records": [
                {"Sns": {"Message": json.dumps({"AlarmName": "test-alarm"})}}
            ]
        }

        with pytest.raises(AlarmProcessingError, match="Failed to process 1 record"):
            lambda_handler(event, None)

    @patch("functions.slack_alarm_handler.get_slack_webhook_url")
    def test_webhook_url_error(self, mock_webhook):
        mock_webhook.side_effect = ValueError("Webhook not configured")

        event = {
            "Records": [
                {"Sns": {"Message": json.dumps({"AlarmName": "test-alarm"})}}
            ]
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        assert "Webhook not configured" in result["body"]
