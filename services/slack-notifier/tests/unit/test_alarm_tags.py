"""Tests for alarm_tags module."""

from unittest.mock import MagicMock, patch

from functions.alarm_tags import get_alarm_tags


class TestGetAlarmTags:
    @patch("functions.alarm_tags.logger")
    @patch("functions.alarm_tags.boto3.client")
    def test_get_alarm_tags_success(
        self, mock_boto_client: MagicMock, mock_logger: MagicMock
    ) -> None:
        mock_cloudwatch = MagicMock()
        mock_boto_client.return_value = mock_cloudwatch
        mock_cloudwatch.list_tags_for_resource.return_value = {
            "Tags": [
                {"Key": "api_path", "Value": "/Organization"},
                {"Key": "service", "Value": "DoS Search"},
            ]
        }

        result = get_alarm_tags("arn:aws:cloudwatch:eu-west-2:123456789012:alarm:test")

        assert result == {"api_path": "/Organization", "service": "DoS Search"}
        mock_cloudwatch.list_tags_for_resource.assert_called_once_with(
            ResourceARN="arn:aws:cloudwatch:eu-west-2:123456789012:alarm:test"
        )

    @patch("functions.alarm_tags.logger")
    @patch("functions.alarm_tags.boto3.client")
    def test_get_alarm_tags_missing_tags(
        self, mock_boto_client: MagicMock, mock_logger: MagicMock
    ) -> None:
        mock_cloudwatch = MagicMock()
        mock_boto_client.return_value = mock_cloudwatch
        mock_cloudwatch.list_tags_for_resource.return_value = {"Tags": []}

        result = get_alarm_tags("arn:aws:cloudwatch:eu-west-2:123456789012:alarm:test")

        assert result == {"api_path": "N/A", "service": "Unknown"}

    @patch("functions.alarm_tags.logger")
    @patch("functions.alarm_tags.boto3.client")
    def test_get_alarm_tags_partial_tags(
        self, mock_boto_client: MagicMock, mock_logger: MagicMock
    ) -> None:
        mock_cloudwatch = MagicMock()
        mock_boto_client.return_value = mock_cloudwatch
        mock_cloudwatch.list_tags_for_resource.return_value = {
            "Tags": [{"Key": "api_path", "Value": "/Organization"}]
        }

        result = get_alarm_tags("arn:aws:cloudwatch:eu-west-2:123456789012:alarm:test")

        assert result == {"api_path": "/Organization", "service": "Unknown"}

    @patch("functions.alarm_tags.logger")
    @patch("functions.alarm_tags.boto3.client")
    def test_get_alarm_tags_client_error(
        self, mock_boto_client: MagicMock, mock_logger: MagicMock
    ) -> None:
        mock_cloudwatch = MagicMock()
        mock_boto_client.return_value = mock_cloudwatch
        mock_cloudwatch.list_tags_for_resource.side_effect = Exception("Access denied")

        result = get_alarm_tags("arn:aws:cloudwatch:eu-west-2:123456789012:alarm:test")

        assert result == {"api_path": "N/A", "service": "Unknown"}
        mock_logger.exception.assert_called_once_with("Failed to fetch alarm tags")

    @patch("functions.alarm_tags.logger")
    def test_get_alarm_tags_empty_arn(self, mock_logger: MagicMock) -> None:
        result = get_alarm_tags("")

        assert result == {"api_path": "N/A", "service": "Unknown"}

    @patch("functions.alarm_tags.logger")
    def test_get_alarm_tags_none_arn(self, mock_logger: MagicMock) -> None:
        result = get_alarm_tags(None)  # type: ignore

        assert result == {"api_path": "N/A", "service": "Unknown"}
