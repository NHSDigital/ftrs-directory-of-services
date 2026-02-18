"""Unit tests for version history lambda handler."""

import copy
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_data_layer.client import get_dynamodb_resource
from pytest_mock import MockerFixture

from version_history.lambda_handler import lambda_handler


@pytest.fixture
def mock_dynamodb_resource(
    mocker: MockerFixture, mock_version_history_table: MagicMock
) -> None:
    """Mock DynamoDB resource and table name resolution."""
    # Clear the cache before mocking
    get_dynamodb_resource.cache_clear()

    mocker.patch(
        "version_history.lambda_handler.get_dynamodb_resource",
        return_value=Mock(Table=Mock(return_value=mock_version_history_table)),
    )
    mocker.patch(
        "version_history.lambda_handler.get_table_name",
        return_value="test-version-history",
    )


class TestLambdaHandler:
    """Tests for lambda_handler function."""

    def test_lambda_handler_processes_single_record(
        self,
        sample_organisation_stream_record: Dict[str, Any],
        mock_lambda_context: LambdaContext,
        mock_dynamodb_resource: None,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test lambda handler processes single record successfully."""
        event = {"Records": [sample_organisation_stream_record]}

        result = lambda_handler(event, mock_lambda_context)

        assert result == {"batchItemFailures": []}
        mock_version_history_table.put_item.assert_called_once()

    def test_lambda_handler_processes_multiple_records(
        self,
        sample_event_with_multiple_records: Dict[str, Any],
        mock_lambda_context: LambdaContext,
        mock_dynamodb_resource: None,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test lambda handler processes multiple records."""
        result = lambda_handler(sample_event_with_multiple_records, mock_lambda_context)

        assert result == {"batchItemFailures": []}
        # Both Organisation and Location records should be processed
        expected_record_count = 2
        assert mock_version_history_table.put_item.call_count == expected_record_count

    def test_lambda_handler_handles_partial_failures(
        self,
        sample_organisation_stream_record: Dict[str, Any],
        mock_lambda_context: LambdaContext,
        mock_dynamodb_resource: None,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test lambda handler returns batch failures on errors."""
        # Make put_item raise an exception
        mock_version_history_table.put_item.side_effect = Exception("DynamoDB error")

        event = {"Records": [sample_organisation_stream_record]}
        result = lambda_handler(event, mock_lambda_context)

        assert len(result["batchItemFailures"]) == 1
        assert result["batchItemFailures"][0]["itemIdentifier"] == "123456789"

    def test_lambda_handler_handles_empty_records(
        self,
        mock_lambda_context: LambdaContext,
        mock_dynamodb_resource: None,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test lambda handler handles empty Records array."""
        event: Dict[str, Any] = {"Records": []}

        result = lambda_handler(event, mock_lambda_context)

        assert result == {"batchItemFailures": []}
        mock_version_history_table.put_item.assert_not_called()

    def test_lambda_handler_continues_after_single_failure(
        self,
        sample_organisation_stream_record: Dict[str, Any],
        mock_lambda_context: LambdaContext,
        mock_dynamodb_resource: None,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test lambda handler continues processing after a single record fails."""
        # Create second successful record using deepcopy to avoid shared references
        second_record = copy.deepcopy(sample_organisation_stream_record)
        second_record["dynamodb"]["SequenceNumber"] = "987654321"
        second_record["dynamodb"]["Keys"]["field"]["S"] = "status"
        second_record["dynamodb"]["OldImage"]["field"]["S"] = "status"
        second_record["dynamodb"]["OldImage"]["value"]["S"] = "pending"
        second_record["dynamodb"]["NewImage"]["field"]["S"] = "status"
        second_record["dynamodb"]["NewImage"]["value"]["S"] = "active"

        # Make first call fail, second succeed
        mock_version_history_table.put_item.side_effect = [
            Exception("DynamoDB error"),
            None,
        ]

        event = {"Records": [sample_organisation_stream_record, second_record]}
        result = lambda_handler(event, mock_lambda_context)

        # Should have one failure but continue processing
        assert len(result["batchItemFailures"]) == 1
        assert result["batchItemFailures"][0]["itemIdentifier"] == "123456789"
        # Both records attempted (one failed, one succeeded)
        expected_call_count = 2
        assert mock_version_history_table.put_item.call_count == expected_call_count
