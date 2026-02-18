"""Shared fixtures for version history tests."""

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_version_history_table(mocker: MockerFixture) -> MagicMock:
    """Mock DynamoDB version history table."""
    table = mocker.MagicMock()
    table.put_item = mocker.MagicMock()
    return table


@pytest.fixture
def sample_organisation_stream_record() -> Dict[str, Any]:
    """Sample DynamoDB stream record for Organisation table."""
    return {
        "eventID": "test-event-id",
        "eventName": "MODIFY",
        "eventVersion": "1.1",
        "eventSource": "aws:dynamodb",
        "awsRegion": "eu-west-2",
        "eventSourceARN": (
            "arn:aws:dynamodb:eu-west-2:123456789012:table/"
            "ftrs-dos-local-database-organisation-test/stream/"
            "2025-01-01T00:00:00.000"
        ),
        "dynamodb": {
            "ApproximateCreationDateTime": 1640995200,
            "Keys": {
                "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "name"},
            },
            "OldImage": {
                "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "name"},
                "value": {"S": "Old Organisation Name"},
            },
            "NewImage": {
                "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "name"},
                "value": {"S": "New Organisation Name"},
                "lastUpdatedBy": {
                    "M": {
                        "type": {"S": "app"},
                        "value": {"S": "INTERNAL001"},
                        "display": {"S": "Data Migration"},
                    }
                },
            },
            "SequenceNumber": "123456789",
            "SizeBytes": 123,
            "StreamViewType": "NEW_AND_OLD_IMAGES",
        },
    }


@pytest.fixture
def sample_location_stream_record() -> Dict[str, Any]:
    """Sample DynamoDB stream record for Location table."""
    return {
        "eventID": "test-event-id-2",
        "eventName": "MODIFY",
        "eventVersion": "1.1",
        "eventSource": "aws:dynamodb",
        "awsRegion": "eu-west-2",
        "eventSourceARN": (
            "arn:aws:dynamodb:eu-west-2:123456789012:table/"
            "ftrs-dos-local-database-location-test/stream/"
            "2025-01-01T00:00:00.000"
        ),
        "dynamodb": {
            "Keys": {
                "id": {"S": "660e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "status"},
            },
            "OldImage": {
                "id": {"S": "660e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "status"},
                "value": {"S": "pending"},
            },
            "NewImage": {
                "id": {"S": "660e8400-e29b-41d4-a716-446655440000"},
                "field": {"S": "status"},
                "value": {"S": "active"},
                "lastUpdatedBy": {
                    "M": {
                        "type": {"S": "user"},
                        "value": {"S": "user-123"},
                        "display": {"S": "John Doe"},
                    }
                },
            },
            "SequenceNumber": "123456790",
        },
    }


@pytest.fixture
def sample_event_with_multiple_records(
    sample_organisation_stream_record: Dict[str, Any],
    sample_location_stream_record: Dict[str, Any],
) -> Dict[str, Any]:
    """Sample Lambda event with multiple stream records."""
    return {
        "Records": [
            sample_organisation_stream_record,
            sample_location_stream_record,
        ]
    }
