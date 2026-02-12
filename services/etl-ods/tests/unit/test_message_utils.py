import json
from typing import Optional

import pytest
from pytest_mock import MockerFixture

from common.message_utils import create_message_payload


@pytest.fixture
def mock_context_ids(mocker: MockerFixture) -> tuple:
    """Mock correlation_id and request_id context variables for testing."""
    mock_correlation_id = mocker.patch("common.message_utils.current_correlation_id")
    mock_request_id = mocker.patch("common.message_utils.current_request_id")
    mock_correlation_id.get.return_value = "default-corr-id"
    mock_request_id.get.return_value = "default-req-id"
    return mock_correlation_id, mock_request_id


class TestCreateMessagePayload:
    def test_create_message_payload_with_all_parameters(self) -> None:
        """Test that create_message_payload correctly formats payload with explicit IDs."""
        path = "/test/path"
        body = {"key": "value", "number": 42}
        correlation_id = "corr-123"
        request_id = "req-456"

        result = create_message_payload(path, body, correlation_id, request_id)

        parsed_result = json.loads(result)
        assert parsed_result == {
            "path": "/test/path",
            "body": {"key": "value", "number": 42},
            "correlation_id": "corr-123",
            "request_id": "req-456",
        }

    def test_create_message_payload_with_default_correlation_id(
        self, mock_context_ids: tuple
    ) -> None:
        """Test that correlation_id defaults to current context value when not provided."""
        mock_correlation_id, _ = mock_context_ids
        mock_correlation_id.get.return_value = "auto-corr-789"

        path = "/test/path"
        body = {"data": "test"}
        request_id = "req-456"

        result = create_message_payload(path, body, request_id=request_id)

        parsed_result = json.loads(result)
        assert parsed_result == {
            "path": "/test/path",
            "body": {"data": "test"},
            "correlation_id": "auto-corr-789",
            "request_id": "req-456",
        }
        mock_correlation_id.get.assert_called_once()

    def test_create_message_payload_with_default_request_id(
        self, mock_context_ids: tuple
    ) -> None:
        """Test that request_id defaults to current context value when not provided."""
        _, mock_request_id = mock_context_ids
        mock_request_id.get.return_value = "auto-req-987"

        path = "/test/path"
        body = {"data": "test"}
        correlation_id = "corr-123"

        result = create_message_payload(path, body, correlation_id=correlation_id)

        parsed_result = json.loads(result)
        assert parsed_result == {
            "path": "/test/path",
            "body": {"data": "test"},
            "correlation_id": "corr-123",
            "request_id": "auto-req-987",
        }
        mock_request_id.get.assert_called_once()

    def test_create_message_payload_with_both_defaults(
        self, mock_context_ids: tuple
    ) -> None:
        """Test that both IDs default to current context values when not provided."""
        mock_correlation_id, mock_request_id = mock_context_ids
        mock_correlation_id.get.return_value = "auto-corr-111"
        mock_request_id.get.return_value = "auto-req-222"

        path = "/test/path"
        body = {"message": "hello"}

        result = create_message_payload(path, body)

        parsed_result = json.loads(result)
        assert parsed_result == {
            "path": "/test/path",
            "body": {"message": "hello"},
            "correlation_id": "auto-corr-111",
            "request_id": "auto-req-222",
        }
        mock_correlation_id.get.assert_called_once()
        mock_request_id.get.assert_called_once()

    def test_create_message_payload_with_complex_body(self) -> None:
        """Test that complex nested body structures are correctly serialized."""
        path = "/complex/data"
        body = {
            "nested": {
                "array": [1, 2, {"inner": "value"}],
                "boolean": True,
                "null_value": None,
            },
            "simple": "string",
        }
        correlation_id = "corr-complex"
        request_id = "req-complex"

        result = create_message_payload(path, body, correlation_id, request_id)

        parsed_result = json.loads(result)
        assert parsed_result["body"] == body
        assert parsed_result["path"] == path
        assert parsed_result["correlation_id"] == correlation_id
        assert parsed_result["request_id"] == request_id

    def test_create_message_payload_with_empty_body(self) -> None:
        """Test that empty body dictionary is correctly handled."""
        path = "/empty"
        body = {}
        correlation_id = "corr-empty"
        request_id = "req-empty"

        result = create_message_payload(path, body, correlation_id, request_id)

        parsed_result = json.loads(result)
        assert parsed_result == {
            "path": "/empty",
            "body": {},
            "correlation_id": "corr-empty",
            "request_id": "req-empty",
        }

    @pytest.mark.parametrize(
        "correlation_id,request_id",
        [
            (None, "explicit-req"),
            ("explicit-corr", None),
            (None, None),
            ("", ""),
        ],
    )
    def test_create_message_payload_id_variations(
        self,
        mock_context_ids: tuple,
        correlation_id: Optional[str],
        request_id: Optional[str],
    ) -> None:
        """Test that function handles various combinations of None and explicit ID values."""
        mock_correlation_id, mock_request_id = mock_context_ids
        mock_correlation_id.get.return_value = "default-corr"
        mock_request_id.get.return_value = "default-req"

        path = "/test"
        body = {"test": "data"}

        result = create_message_payload(path, body, correlation_id, request_id)
        parsed_result = json.loads(result)

        expected_corr = "default-corr" if correlation_id is None else correlation_id
        expected_req = "default-req" if request_id is None else request_id

        assert parsed_result["correlation_id"] == expected_corr
        assert parsed_result["request_id"] == expected_req

    def test_create_message_payload_returns_valid_json_string(self) -> None:
        """Test that function returns a valid JSON string that can be parsed."""
        path = "/test"
        body = {"key": "value"}
        correlation_id = "corr-123"
        request_id = "req-456"

        result = create_message_payload(path, body, correlation_id, request_id)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "path" in parsed
        assert "body" in parsed
        assert "correlation_id" in parsed
        assert "request_id" in parsed

    def test_create_message_payload_with_special_characters(self) -> None:
        """Test that special characters in path and IDs are correctly preserved."""
        path = "/test/with spaces & symbols"
        body = {"special": "!@#$%^&*()"}
        correlation_id = "corr-!@#"
        request_id = "req-!@#"

        result = create_message_payload(path, body, correlation_id, request_id)

        parsed_result = json.loads(result)
        assert parsed_result["path"] == path
        assert parsed_result["body"] == body
        assert parsed_result["correlation_id"] == correlation_id
        assert parsed_result["request_id"] == request_id
