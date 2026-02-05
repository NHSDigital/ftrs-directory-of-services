"""
API Gateway Error Scenario Tests

Tests error handling for API Gateway-specific scenarios including:
- Malformed requests
- Missing HTTP method
- Unsupported HTTP methods
- Missing required headers
- Edge cases in request structure
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from functions.dos_search_ods_code_function import lambda_handler


@pytest.fixture
def mock_ftrs_service():
    """Mock FtrsService for error scenario tests"""
    with patch("functions.dos_search_ods_code_function.FtrsService") as mock:
        yield mock


class TestAPIGatewayMalformedRequests:
    """Test handling of malformed API Gateway requests"""

    def test_missing_http_method(self, mock_ftrs_service):
        """API Gateway event missing httpMethod should be handled gracefully"""
        # Arrange
        event = {
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act & Assert - Should handle KeyError gracefully
        with pytest.raises(KeyError):
            lambda_handler(event, {})

    def test_missing_query_string_parameters(self, mock_ftrs_service):
        """API Gateway event with None queryStringParameters"""
        # Arrange
        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": None,  # API Gateway returns None when no params
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["resourceType"] == "OperationOutcome"
        assert body["issue"][0]["severity"] == "error"

    def test_empty_query_string_parameters(self, mock_ftrs_service):
        """API Gateway event with empty queryStringParameters dict"""
        # Arrange
        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {},
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["resourceType"] == "OperationOutcome"

    def test_missing_headers(self, mock_ftrs_service):
        """API Gateway event with None headers"""
        # Arrange
        event = {
            "httpMethod": "GET",
            "headers": None,  # API Gateway might return None
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert - Should handle gracefully
        assert response["statusCode"] in [200, 400, 500]

    def test_empty_headers(self, mock_ftrs_service):
        """API Gateway event with empty headers dict"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {},  # No headers at all
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 200  # Should succeed with no optional headers


class TestAPIGatewayUnsupportedMethods:
    """Test handling of unsupported HTTP methods"""

    @pytest.mark.parametrize(
        "method",
        ["POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    )
    def test_unsupported_http_methods(self, method, mock_ftrs_service):
        """API should reject unsupported HTTP methods"""
        # Arrange
        event = {
            "httpMethod": method,
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["resourceType"] == "OperationOutcome"

    def test_case_sensitive_http_method(self, mock_ftrs_service):
        """Test that httpMethod is case-sensitive (lowercase should fail)"""
        # Arrange
        event = {
            "httpMethod": "get",  # lowercase
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert - API Gateway sends uppercase, but test edge case
        assert response["statusCode"] == 400


class TestAPIGatewayRequestEdgeCases:
    """Test edge cases in API Gateway request handling"""

    def test_extra_unexpected_fields_in_event(self, mock_ftrs_service):
        """API Gateway event with extra unexpected fields"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
            "body": None,
            "isBase64Encoded": False,
            "requestContext": {"accountId": "123456789012"},  # gitleaks:allow - Test fixture
            "stageVariables": None,
            "pathParameters": None,
            "resource": "/Organization",
            "path": "/Organization",
        }

        # Act
        response = lambda_handler(event, {})

        # Assert - Should ignore extra fields
        assert response["statusCode"] == 200

    def test_case_insensitive_header_names(self, mock_ftrs_service):
        """Test that header names are case-insensitive"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {
                "content-type": "application/fhir+json",  # lowercase
                "NHSD-CORRELATION-ID": "test-123",  # uppercase
                "nhsd-request-id": "req-456",  # lowercase
            },
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert - Should accept case-insensitive headers
        assert response["statusCode"] == 200

    def test_multivalue_query_parameters(self, mock_ftrs_service):
        """Test handling of multiValueQueryStringParameters"""
        # Arrange
        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
            "multiValueQueryStringParameters": {
                "identifier": ["odsOrganisationCode|ABC123"],
                "_revinclude": ["Endpoint:organization"],
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert - Should handle both formats
        assert response["statusCode"] in [200, 400]

    def test_duplicate_query_parameters(self, mock_ftrs_service):
        """Test handling of duplicate query parameters"""
        # Arrange
        # Note: Python dicts don't allow duplicate keys, so this simulates
        # API Gateway's behavior where the last value wins
        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                # In real API Gateway, duplicate params result in last value being kept
                "identifier": "odsOrganisationCode|XYZ789",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] in [200, 400]


class TestAPIGatewayResponseFormat:
    """Test that responses match API Gateway expected format"""

    def test_response_has_required_fields(self, mock_ftrs_service):
        """API Gateway response must have statusCode and body"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert "statusCode" in response
        assert "body" in response
        assert isinstance(response["statusCode"], int)
        assert isinstance(response["body"], str)

    def test_response_body_is_valid_json(self, mock_ftrs_service):
        """API Gateway response body must be valid JSON string"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        body = json.loads(response["body"])  # Should not raise JSONDecodeError
        assert isinstance(body, dict)

    def test_response_includes_cors_headers(self, mock_ftrs_service):
        """API Gateway response should include CORS headers"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert "multiValueHeaders" in response
        headers = response["multiValueHeaders"]
        assert "Access-Control-Allow-Methods" in headers
        assert "Access-Control-Allow-Headers" in headers

    def test_response_content_type_is_fhir_json(self, mock_ftrs_service):
        """API Gateway response should set Content-Type to application/fhir+json"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        headers = response["multiValueHeaders"]
        assert "Content-Type" in headers
        assert "application/fhir+json" in headers["Content-Type"]


class TestAPIGatewayPayloadSizeHandling:
    """Test handling of various payload sizes"""

    def test_large_ods_code_value(self, mock_ftrs_service):
        """Test handling of maximum length ODS code"""
        # Arrange
        large_ods_code = "A" * 12  # Maximum valid length

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": f"odsOrganisationCode|{large_ods_code}",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] in [200, 404]  # Valid format

    def test_oversized_ods_code_rejected(self, mock_ftrs_service):
        """Test that oversized ODS codes are rejected"""
        # Arrange
        oversized_ods_code = "A" * 13  # Exceeds maximum

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": f"odsOrganisationCode|{oversized_ods_code}",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["resourceType"] == "OperationOutcome"

    def test_large_number_of_headers(self, mock_ftrs_service):
        """Test request with many headers"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        headers = {
            "Content-Type": "application/fhir+json",
            "Authorization": "Bearer token123",
            "NHSD-Correlation-ID": "corr-123",
            "NHSD-Request-ID": "req-123",
            "NHSD-Message-Id": "msg-123",
            "NHSD-Api-Version": "1.0.0",
            "NHSD-End-User-Role": "clinician",
            "NHSD-Client-Id": "client-123",
            "Accept": "application/fhir+json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-GB",
            "User-Agent": "TestAgent/1.0",
        }

        event = {
            "httpMethod": "GET",
            "headers": headers,
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, {})

        # Assert
        assert response["statusCode"] == 200  # Should handle many headers


class TestAPIGatewayContextHandling:
    """Test handling of Lambda context from API Gateway"""

    def test_lambda_context_with_request_id(self, mock_ftrs_service):
        """Test that lambda context request ID is available"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Mock context
        context = MagicMock()
        context.request_id = "test-request-id-123"
        context.function_name = "dos-search-ods-code"
        context.memory_limit_in_mb = 512

        # Act
        response = lambda_handler(event, context)

        # Assert
        assert response["statusCode"] == 200
        # Context should be available for logging/tracing

    def test_lambda_context_none(self, mock_ftrs_service):
        """Test handling when context is None"""
        # Arrange
        mock_ftrs_service.return_value.get_organisation.return_value = None

        event = {
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/fhir+json"},
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
                "_revinclude": "Endpoint:organization",
            },
        }

        # Act
        response = lambda_handler(event, None)

        # Assert - Should handle None context gracefully
        assert response["statusCode"] == 200
