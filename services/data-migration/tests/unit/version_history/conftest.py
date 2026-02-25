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
def sample_organisation_document_stream_record() -> Dict[str, Any]:
    """Sample DynamoDB stream record for Organisation document field (full document storage)."""
    return {
        "eventID": "test-event-doc-1",
        "eventName": "MODIFY",
        "eventVersion": "1.1",
        "eventSource": "aws:dynamodb",
        "awsRegion": "eu-west-2",
        "eventSourceARN": (
            "arn:aws:dynamodb:eu-west-2:123456789012:table/"
            "ftrs-dos-dev-database-organisation/stream/"
            "2026-02-20T00:00:00.000"
        ),
        "dynamodb": {
            "Keys": {
                "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                "field": {"S": "document"},
            },
            "OldImage": {
                "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                "field": {"S": "document"},
                "created": {"S": "2026-02-17T14:28:01.640710Z"},
                "lastUpdated": {"S": "2026-02-17T14:28:01.640710Z"},
                "createdBy": {
                    "M": {
                        "type": {"S": "app"},
                        "value": {"S": "INTERNAL001"},
                        "display": {"S": "Data Migration"},
                    }
                },
                "lastUpdatedBy": {
                    "M": {
                        "type": {"S": "app"},
                        "value": {"S": "INTERNAL001"},
                        "display": {"S": "Data Migration"},
                    }
                },
                "name": {"S": "Old Practice Name"},
                "active": {"BOOL": True},
                "identifier_ODS_ODSCode": {"S": "A12345"},
                "type": {"S": "GP Practice"},
            },
            "NewImage": {
                "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                "field": {"S": "document"},
                "created": {"S": "2026-02-17T14:28:01.640710Z"},
                "lastUpdated": {"S": "2026-02-20T14:45:00.000000Z"},
                "createdBy": {
                    "M": {
                        "type": {"S": "app"},
                        "value": {"S": "INTERNAL001"},
                        "display": {"S": "Data Migration"},
                    }
                },
                "lastUpdatedBy": {
                    "M": {
                        "type": {"S": "app"},
                        "value": {"S": "INTERNAL001"},
                        "display": {"S": "Data Migration"},
                    }
                },
                "name": {"S": "New Practice Name"},
                "active": {"BOOL": True},
                "identifier_ODS_ODSCode": {"S": "A12345"},
                "type": {"S": "GP Practice"},
            },
            "SequenceNumber": "123456791",
        },
    }
