import json
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

from pipeline.transformer import _process_organisation, transformer_lambda_handler

# Test constants
TEST_RECORD_COUNT = 15
EXPECTED_BATCH_CALLS = 2


def test_transformer_lambda_handler_success(mocker: MockerFixture) -> None:
    """Test successful transformation of organization messages."""
    mock_process = mocker.patch(
        "pipeline.transformer._process_organisation", return_value="processed_data"
    )
    mock_send_messages = mocker.patch("pipeline.transformer.send_messages_to_queue")

    event = {
        "Records": [
            {
                "messageId": "msg1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": "org1", "name": "Test Org"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        ]
    }

    result = transformer_lambda_handler(event, {})

    assert result["batchItemFailures"] == []
    mock_process.assert_called_once()
    mock_send_messages.assert_called_once_with(
        ["processed_data"], queue_suffix="load-queue"
    )


def test_transformer_lambda_handler_missing_fields(mocker: MockerFixture) -> None:
    """Test transformer handles missing required fields."""
    event = {
        "Records": [
            {
                "messageId": "msg1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"incomplete": "data"}),
            }
        ]
    }

    result = transformer_lambda_handler(event, {})

    assert len(result["batchItemFailures"]) == 1
    assert result["batchItemFailures"][0]["itemIdentifier"] == "msg1"


def test_transformer_lambda_handler_processing_failure(mocker: MockerFixture) -> None:
    """Test transformer handles processing failures."""
    mock_process = mocker.patch(
        "pipeline.transformer._process_organisation", return_value=None
    )
    mock_send_messages = mocker.patch("pipeline.transformer.send_messages_to_queue")

    event = {
        "Records": [
            {
                "messageId": "msg1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": "org1", "name": "Test Org"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        ]
    }

    result = transformer_lambda_handler(event, {})

    assert result["batchItemFailures"] == []
    mock_process.assert_called_once()
    mock_send_messages.assert_not_called()


def test_transformer_lambda_handler_batch_processing(mocker: MockerFixture) -> None:
    """Test transformer processes multiple messages and sends in batches."""
    mock_process = mocker.patch(
        "pipeline.transformer._process_organisation", return_value="processed_data"
    )
    mock_send_messages = mocker.patch("pipeline.transformer.send_messages_to_queue")

    # Create 15 messages to test batching (BATCH_SIZE = 10)
    records = []
    for i in range(TEST_RECORD_COUNT):
        records.append(
            {
                "messageId": f"msg{i}",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": f"org{i}", "name": f"Test Org {i}"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        )

    event = {"Records": records}

    result = transformer_lambda_handler(event, {})

    assert result["batchItemFailures"] == []
    assert mock_process.call_count == TEST_RECORD_COUNT
    # Should be called twice: once for batch of 10, once for remaining 5
    assert mock_send_messages.call_count == EXPECTED_BATCH_CALLS


def test_transformer_lambda_handler_exception(mocker: MockerFixture) -> None:
    """Test transformer handles processing exceptions."""
    mocker.patch(
        "pipeline.transformer._process_organisation",
        side_effect=Exception("Processing failed"),
    )

    event = {
        "Records": [
            {
                "messageId": "msg1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": "org1", "name": "Test Org"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        ]
    }

    result = transformer_lambda_handler(event, {})

    assert len(result["batchItemFailures"]) == 1
    assert result["batchItemFailures"][0]["itemIdentifier"] == "msg1"


def test_transformer_lambda_handler_no_event() -> None:
    """Test transformer handles empty event."""
    result = transformer_lambda_handler({}, {})

    assert result["batchItemFailures"] == []


def test_process_organisation_success(mocker: MockerFixture) -> None:
    """Test successful organization processing."""
    mock_organisation = {
        "id": "org1",
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
    }

    mock_fhir_org = MagicMock()
    mock_fhir_org.identifier = [MagicMock()]
    mock_fhir_org.identifier[0].value = "ABC123"
    mock_fhir_org.model_dump.return_value = {
        "id": "uuid-123",
        "resourceType": "Organization",
    }

    mocker.patch(
        "pipeline.transformer.transform_to_payload", return_value=mock_fhir_org
    )
    mocker.patch(
        "pipeline.transformer.fetch_organisation_uuid", return_value="uuid-123"
    )

    # Use patch context manager to mock the context variables
    with patch("pipeline.transformer.current_correlation_id") as mock_corr_id:
        with patch("pipeline.transformer.current_request_id") as mock_req_id:
            mock_corr_id.get.return_value = "corr-123"
            mock_req_id.get.return_value = "req-456"

            result = _process_organisation(mock_organisation)

            assert result is not None
            parsed_result = json.loads(result)
            assert parsed_result["path"] == "uuid-123"
            assert parsed_result["correlation_id"] == "corr-123"
            assert parsed_result["request_id"] == "req-456"


def test_process_organisation_uuid_not_found(mocker: MockerFixture) -> None:
    """Test organization processing when UUID is not found."""
    mock_organisation = {
        "id": "org1",
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
    }

    mock_fhir_org = MagicMock()
    mock_fhir_org.identifier = [MagicMock()]
    mock_fhir_org.identifier[0].value = "ABC123"

    mocker.patch(
        "pipeline.transformer.transform_to_payload", return_value=mock_fhir_org
    )
    mocker.patch("pipeline.transformer.fetch_organisation_uuid", return_value=None)

    result = _process_organisation(mock_organisation)

    assert result is None


def test_process_organisation_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test organization processing handles exceptions."""
    mock_organisation = {"id": "org1", "name": "Test Org"}

    mocker.patch(
        "pipeline.transformer.transform_to_payload",
        side_effect=Exception("Transform failed"),
    )

    result = _process_organisation(mock_organisation)

    assert result is None
