import json
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from common.exceptions import (
    PermanentProcessingError,
    RetryableProcessingError,
)
from transformer.transformer import (
    _process_record,
    _transform_organisation,
    transformer_lambda_handler,
)


@pytest.fixture(scope="module")
def sample_organisation() -> dict:
    """File-scoped fixture for sample organisation data."""
    return {
        "id": "org1",
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organization",
    }


@pytest.fixture(scope="module")
def sample_transformer_record() -> dict:
    """File-scoped fixture for sample transformer SQS record."""
    return {
        "messageId": "msg-123",
        "attributes": {"ApproximateReceiveCount": "1"},
        "body": json.dumps(
            {
                "organisation": {
                    "id": "org1",
                    "identifier": [{"value": "ABC123"}],
                    "name": "Test Org",
                },
                "correlation_id": "corr-456",
                "request_id": "req-789",
            }
        ),
    }


@pytest.fixture(scope="module")
def sample_event_single_record() -> dict:
    """File-scoped fixture for Lambda event with single record."""
    return {
        "Records": [
            {
                "messageId": "msg-1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": "org1", "name": "Org 1"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        ]
    }


@pytest.fixture(scope="module")
def sample_event_multiple_records() -> dict:
    """File-scoped fixture for Lambda event with multiple records."""
    records = []
    for i in range(15):  # 15 records to test batching (BATCH_SIZE = 10)
        records.append(
            {
                "messageId": f"msg-{i}",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {
                        "organisation": {"id": f"org{i}", "name": f"Org {i}"},
                        "correlation_id": "corr-123",
                        "request_id": "req-456",
                    }
                ),
            }
        )
    return {"Records": records}


class TestTransformOrganisation:
    """Test _transform_organisation function."""

    def test_successful_processing(
        self, mocker: MockerFixture, sample_organisation: dict
    ) -> None:
        """Test successful organisation processing and payload creation."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [MagicMock(value="ABC123")]
        mock_fhir_org.model_dump.return_value = {
            "id": "uuid-123",
            "resourceType": "Organization",
            "name": "Test Organization",
        }

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid", return_value="uuid-123"
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        mock_corr_id = mocker.patch("transformer.transformer.current_correlation_id")
        mock_req_id = mocker.patch("transformer.transformer.current_request_id")
        mock_corr_id.get.return_value = "corr-123"
        mock_req_id.get.return_value = "req-456"

        result = _transform_organisation(sample_organisation, "test-msg-123")

        assert result is not None
        parsed_result = json.loads(result)
        assert parsed_result["path"] == "uuid-123"
        assert parsed_result["correlation_id"] == "corr-123"
        assert parsed_result["request_id"] == "req-456"
        assert parsed_result["body"]["resourceType"] == "Organization"

    def test_missing_identifier_raises_permanent_error(
        self, mocker: MockerFixture
    ) -> None:
        """Test that organisation with no identifier raises PermanentProcessingError."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = []

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mock_logger = mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        with pytest.raises(PermanentProcessingError) as exc_info:
            _transform_organisation(organisation, "test-msg-123")

        assert exc_info.value.message_id == "test-msg-123"
        mock_logger.log.assert_called()
        call_kwargs = mock_logger.log.call_args[1]
        assert call_kwargs["ods_code"] == "<no identifier>"

    def test_uuid_not_found_raises_permanent_error(self, mocker: MockerFixture) -> None:
        """Test that missing UUID raises PermanentProcessingError."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [MagicMock(value="NOTFOUND123")]

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid",
            side_effect=PermanentProcessingError(
                message_id="test-msg-123",
                status_code=404,
                response_text="Organisation not found",
            ),
        )
        organisation = {"id": "org1", "name": "Test Org"}

        # PermanentProcessingError should be re-raised by _transform_organisation
        with pytest.raises(PermanentProcessingError) as exc_info:
            _transform_organisation(organisation, "test-msg-123")

        assert exc_info.value.message_id == "test-msg-123"
        assert str(exc_info.value.status_code) == "404"

    def test_rate_limit_exception_is_reraised(self, mocker: MockerFixture) -> None:
        """Test that RetryableProcessingError is re-raised for retry."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [MagicMock(value="ABC123")]

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid",
            side_effect=RetryableProcessingError(
                "Rate limit exceeded",
                status_code=429,
                response_text="Too many requests",
            ),
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        with pytest.raises(RetryableProcessingError, match="Rate limit exceeded"):
            _transform_organisation(organisation, "test-msg-123")

    def test_message_integrity_error_is_reraised(self, mocker: MockerFixture) -> None:
        """Test that PermanentProcessingError wraps transformation failures."""
        mocker.patch(
            "transformer.transformer.transform_to_payload",
            side_effect=ValueError("Invalid FHIR structure"),
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        with pytest.raises(ValueError, match="Invalid FHIR structure"):
            _transform_organisation(organisation, "test-msg-123")

    def test_http_error_404_raises_permanent_error(self, mocker: MockerFixture) -> None:
        """Test that 404 error (PermanentProcessingError) is re-raised by _transform_organisation."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [MagicMock(value="ABC123")]

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )

        # fetch_organisation_uuid raises PermanentProcessingError for 404
        perm_error = PermanentProcessingError(
            message_id="test-msg-123",
            status_code=404,
            response_text="UUID not found for ODS code: ABC123",
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid", side_effect=perm_error
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        # PermanentProcessingError should be re-raised (not caught and returned as None)
        with pytest.raises(PermanentProcessingError) as exc_info:
            _transform_organisation(organisation, "test-msg-123")

        assert exc_info.value.message_id == "test-msg-123"
        assert str(exc_info.value.status_code) == "404"

    def test_general_exception_propagates(self, mocker: MockerFixture) -> None:
        """Test that general exceptions are wrapped in PermanentProcessingError."""
        mocker.patch(
            "transformer.transformer.transform_to_payload",
            side_effect=ValueError("Transform failed"),
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        # Transform failures are now propagated as-is
        with pytest.raises(ValueError, match="Transform failed"):
            _transform_organisation(organisation, "test-msg-123")

    def test_context_variables_none(self, mocker: MockerFixture) -> None:
        """Test processing when context variables are None."""
        # Create mock with proper identifier
        mock_identifier = MagicMock()
        mock_identifier.value = "ABC123"

        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [mock_identifier]
        mock_fhir_org.model_dump.return_value = {
            "id": "uuid-123",
            "resourceType": "Organization",
        }

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid", return_value="uuid-123"
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        # Mock create_message_payload to return a JSON string
        mocker.patch(
            "transformer.transformer.create_message_payload",
            return_value=json.dumps(
                {
                    "path": "uuid-123",
                    "correlation_id": None,
                    "request_id": None,
                }
            ),
        )

        mock_corr_id = mocker.patch("transformer.transformer.current_correlation_id")
        mock_req_id = mocker.patch("transformer.transformer.current_request_id")
        mock_corr_id.get.return_value = None
        mock_req_id.get.return_value = None

        organisation = {"id": "org1", "name": "Test Org"}

        result = _transform_organisation(organisation, "test-msg-123")

        assert result is not None
        parsed_result = json.loads(result)
        assert parsed_result["correlation_id"] is None
        assert parsed_result["request_id"] is None

    def test_exception_propagates_on_early_error(self, mocker: MockerFixture) -> None:
        """Test that ods_code is 'unknown' when error occurs before extraction."""
        mocker.patch(
            "transformer.transformer.transform_to_payload",
            side_effect=ValueError("Early failure"),
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        # Early failures are now propagated as-is
        with pytest.raises(ValueError, match="Early failure"):
            _transform_organisation(organisation, "test-msg-123")

    def test_exception_propagates_after_ods_extraction(
        self, mocker: MockerFixture
    ) -> None:
        """Test that exceptions propagate after ODS code extraction."""
        mock_fhir_org = MagicMock()
        mock_fhir_org.identifier = [MagicMock(value="TRACKED123")]

        mocker.patch(
            "transformer.transformer.transform_to_payload", return_value=mock_fhir_org
        )
        mocker.patch(
            "transformer.transformer.fetch_organisation_uuid",
            side_effect=ValueError("Fetch failed"),
        )
        mocker.patch("transformer.transformer.ods_transformer_logger")

        organisation = {"id": "org1", "name": "Test Org"}

        # Exception should propagate
        with pytest.raises(ValueError, match="Fetch failed"):
            _transform_organisation(organisation, "test-msg-123")


class TestProcessTransformerRecord:
    """Test _process_record function."""

    def test_successful_record_processing(
        self, mocker: MockerFixture, sample_transformer_record: dict
    ) -> None:
        """Test successful processing of transformer record."""
        mock_logger = mocker.patch("transformer.transformer.ods_transformer_logger")

        mocker.patch(
            "transformer.transformer.extract_record_metadata",
            return_value={
                "message_id": "msg-123",
                "body": {
                    "organisation": {"id": "org1", "name": "Test Org"},
                    "correlation_id": "corr-456",
                    "request_id": "req-789",
                },
            },
        )
        mocker.patch("transformer.transformer.validate_required_fields")
        mocker.patch(
            "transformer.transformer._transform_organisation",
            return_value="processed_payload",
        )

        result = _process_record(sample_transformer_record)

        assert result == "processed_payload"
        mock_logger.log.assert_called()

    def test_missing_organisation_field_raises_error(
        self, mocker: MockerFixture
    ) -> None:
        """Test that missing organisation field raises error."""
        mocker.patch(
            "transformer.transformer.extract_record_metadata",
            return_value={
                "message_id": "msg-123",
                "body": {"incomplete": "data"},
            },
        )
        mocker.patch(
            "transformer.transformer.validate_required_fields",
            side_effect=PermanentProcessingError(
                message_id="msg-123",
                status_code=400,
                response_text="organisation field missing",
            ),
        )

        record = {
            "messageId": "msg-123",
            "body": json.dumps({"incomplete": "data"}),
        }

        with pytest.raises(PermanentProcessingError) as exc_info:
            _process_record(record)

        assert exc_info.value.message_id == "msg-123"

    def test_failed_organisation_processing_returns_none(
        self, mocker: MockerFixture
    ) -> None:
        """Test that failed organisation processing returns None."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer.extract_record_metadata",
            return_value={
                "message_id": "msg-123",
                "body": {"organisation": {"id": "org1"}},
            },
        )
        mocker.patch("transformer.transformer.validate_required_fields")
        mocker.patch(
            "transformer.transformer._transform_organisation",
            side_effect=PermanentProcessingError(
                message_id="msg-123",
                status_code=404,
                response_text="Organisation not found",
            ),
        )

        record = {
            "messageId": "msg-123",
            "body": json.dumps({"organisation": {"id": "org1"}}),
        }

        # PermanentProcessingError should be raised by _process_record
        with pytest.raises(PermanentProcessingError) as exc_info:
            _process_record(record)

        assert exc_info.value.message_id == "msg-123"

    def test_extracts_and_validates_correctly(self, mocker: MockerFixture) -> None:
        """Test that record metadata extraction and validation occur correctly."""
        mock_extract = mocker.patch("transformer.transformer.extract_record_metadata")
        mock_validate = mocker.patch("transformer.transformer.validate_required_fields")
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._transform_organisation", return_value="payload"
        )

        mock_extract.return_value = {
            "message_id": "msg-456",
            "body": {"organisation": {"id": "org2"}},
        }

        record = {
            "messageId": "msg-456",
            "body": json.dumps({"organisation": {"id": "org2"}}),
        }

        _process_record(record)

        mock_extract.assert_called_once_with(record)
        mock_validate.assert_called_once()
        call_args = mock_validate.call_args[0]
        assert call_args[1] == ["organisation"]


class TestTransformerLambdaHandler:
    """Test transformer_lambda_handler function."""

    def test_empty_event_returns_empty_failures(self) -> None:
        """Test handler returns empty failures for empty event."""
        response = transformer_lambda_handler({"Records": []}, {})
        assert response["batchItemFailures"] == []

    def test_successful_single_record_processing(
        self, mocker: MockerFixture, sample_event_single_record: dict
    ) -> None:
        """Test successful processing of single record."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._process_record",
            return_value="processed_data",
        )
        mock_send = mocker.patch("transformer.transformer.send_messages_to_queue")

        response = transformer_lambda_handler(sample_event_single_record, {})

        assert response["batchItemFailures"] == []
        mock_send.assert_called_once_with(["processed_data"], queue_suffix="load-queue")

    def test_batch_processing_multiple_records(
        self, mocker: MockerFixture, sample_event_multiple_records: dict
    ) -> None:
        """Test batch processing with 15 records (BATCH_SIZE = 10)."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._process_record",
            return_value="processed_data",
        )
        mock_send = mocker.patch("transformer.transformer.send_messages_to_queue")

        response = transformer_lambda_handler(sample_event_multiple_records, {})

        assert response["batchItemFailures"] == []
        # Should be called twice: once for batch of 10, once for remaining 5
        assert str(mock_send.call_count) == "2"

    def test_permanent_error_consumed_without_retry(
        self, mocker: MockerFixture
    ) -> None:
        """Test that permanent errors are consumed without adding to batch failures."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        # Raise PermanentProcessingError to indicate permanent failure (will be consumed)
        mocker.patch(
            "transformer.transformer._process_record",
            side_effect=PermanentProcessingError(
                message_id="msg-1",
                status_code=404,
                response_text="Organisation not found",
            ),
        )
        mock_send = mocker.patch("transformer.transformer.send_messages_to_queue")

        event = {
            "Records": [
                {
                    "messageId": "msg-1",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": "org1"}}),
                }
            ]
        }

        response = transformer_lambda_handler(event, {})

        # No batch failures since error was permanent and consumed by process_sqs_records
        assert response["batchItemFailures"] == []
        # Nothing sent since permanent error prevented transformation
        mock_send.assert_not_called()

    def test_retryable_error_added_to_batch_failures(
        self, mocker: MockerFixture
    ) -> None:
        """Test that retryable errors are added to batch failures."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._process_record",
            side_effect=ValueError("Retryable error"),
        )

        event = {
            "Records": [
                {
                    "messageId": "msg-retry",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": "org1"}}),
                }
            ]
        }

        response = transformer_lambda_handler(event, {})

        assert len(response["batchItemFailures"]) == 1
        assert response["batchItemFailures"][0]["itemIdentifier"] == "msg-retry"

    def test_mixed_success_and_failure(self, mocker: MockerFixture) -> None:
        """Test processing with mixed success and failures."""
        mocker.patch("transformer.transformer.ods_transformer_logger")

        def mock_process_side_effect(record: dict) -> str:
            body_str = record.get("body", "{}")
            body = json.loads(body_str) if isinstance(body_str, str) else body_str
            org = body.get("organisation", {})
            org_id = org.get("id", "")
            if org_id == "org-fail":
                err_msg = "Processing failed"
                raise ValueError(err_msg)
            return f"processed_{org_id}"

        mocker.patch(
            "transformer.transformer._process_record",
            side_effect=mock_process_side_effect,
        )
        mock_send = mocker.patch("transformer.transformer.send_messages_to_queue")

        event = {
            "Records": [
                {
                    "messageId": "msg-success",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": "org-success"}}),
                },
                {
                    "messageId": "msg-fail",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": "org-fail"}}),
                },
            ]
        }

        response = transformer_lambda_handler(event, {})

        # Only failed message in batch failures
        assert len(response["batchItemFailures"]) == 1
        assert response["batchItemFailures"][0]["itemIdentifier"] == "msg-fail"
        # Successful message sent to queue
        mock_send.assert_called_once_with(
            ["processed_org-success"], queue_suffix="load-queue"
        )

    def test_context_setup(
        self, mocker: MockerFixture, sample_event_single_record: dict
    ) -> None:
        """Test that request context is properly set up."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch("transformer.transformer._process_record", return_value="data")
        mocker.patch("transformer.transformer.send_messages_to_queue")

        transformer_lambda_handler(sample_event_single_record, {})

    def test_remaining_batch_sent_at_end(self, mocker: MockerFixture) -> None:
        """Test that remaining items in batch are sent at the end."""
        mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._transform_organisation",
            return_value="processed_data",
        )
        mock_send = mocker.patch("transformer.transformer.send_messages_to_queue")

        # Create 3 records (less than BATCH_SIZE)
        event = {
            "Records": [
                {
                    "messageId": f"msg-{i}",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": f"org{i}"}}),
                }
                for i in range(3)
            ]
        }

        transformer_lambda_handler(event, {})

        # Should send remaining batch at the end
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert str(len(call_args[0])) == "3"

    def test_poison_message_consumed(self, mocker: MockerFixture) -> None:
        """Test that poison messages (PermanentProcessingError) are consumed and not retried."""
        mocker.patch("transformer.transformer.ods_transformer_logger")

        # Mock _process_record to raise PermanentProcessingError directly
        mocker.patch(
            "transformer.transformer._process_record",
            side_effect=PermanentProcessingError(
                message_id="msg-poison",
                status_code=400,
                response_text="Malformed data",
            ),
        )

        event = {
            "Records": [
                {
                    "messageId": "msg-poison",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": "org1"}}),
                }
            ]
        }

        response = transformer_lambda_handler(event, {})

        assert len(response["batchItemFailures"]) == 0

    def test_logging_failure_summary(self, mocker: MockerFixture) -> None:
        """Test that failure summary is logged when there are batch failures."""
        mock_logger = mocker.patch("transformer.transformer.ods_transformer_logger")
        mocker.patch(
            "transformer.transformer._transform_organisation",
            side_effect=ValueError("Error"),
        )

        event = {
            "Records": [
                {
                    "messageId": f"msg-{i}",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"organisation": {"id": f"org{i}"}}),
                }
                for i in range(3)
            ]
        }

        transformer_lambda_handler(event, {})

        # Verify failure logging occurred
        log_calls = [str(call) for call in mock_logger.log.call_args_list]
        failure_log_found = any("ETL_TRANSFORMER_027" in call for call in log_calls)
        assert failure_log_found
