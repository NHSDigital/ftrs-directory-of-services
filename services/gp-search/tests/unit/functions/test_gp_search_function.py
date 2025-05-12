import json
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.operationoutcome import OperationOutcome
from fhir.resources.R4B.organization import Organization

from functions.gp_search_function import lambda_handler


@pytest.fixture
def lambda_context():
    return MagicMock(spec=LambdaContext)


@pytest.fixture
def mock_ftrs_service():
    with patch("functions.gp_search_function.FtrsService") as mock_class:
        mock_service = MagicMock()
        mock_class.return_value = mock_service
        yield mock_service


@pytest.fixture
def create_test_bundle():
    """Factory function to create a test FHIR Bundle with separate counts for endpoints and organizations."""

    def _create_test_bundle(
        bundle_id="test-bundle-id", endpoint_count=0, organization_count=0
    ):
        # Create entries array
        entries = []

        # Add endpoint entries first
        for i in range(endpoint_count):
            endpoint = Endpoint.model_validate(
                {
                    "id": f"endpoint-{i}",
                    "status": "active",
                    "connectionType": {
                        "system": "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                        "code": "hl7-fhir-rest",
                    },
                    "payloadType": [
                        {
                            "coding": [
                                {
                                    "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                    "code": "document",
                                }
                            ]
                        }
                    ],
                    "address": f"https://example.org/endpoint-{i}",
                }
            )
            entries.append(
                {
                    "fullUrl": f"https://example.org/Endpoint/endpoint-{i}",
                    "resource": endpoint,
                    "search": {"mode": "match"},
                }
            )

        # Then add organization entries
        for i in range(organization_count):
            org = Organization.model_validate(
                {"id": f"org-{i}", "name": f"Test Organization {i}", "active": True}
            )
            entries.append(
                {
                    "fullUrl": f"https://example.org/Organization/org-{i}",
                    "resource": org,
                    "search": {"mode": "include"},
                }
            )

        # Create the bundle
        return Bundle.model_validate(
            {
                "resourceType": "Bundle",
                "type": "searchset",
                "id": bundle_id,
                "entry": entries,
            }
        )

    return _create_test_bundle


@pytest.fixture
def create_error_outcome():
    """Factory function to create a test OperationOutcome for errors."""

    def _create_error_outcome(
        ods_code="UNKNOWN", issue_code="internal-server-error", severity="error"
    ):
        return OperationOutcome.model_validate(
            {
                "resourceType": "OperationOutcome",
                "id": issue_code,
                "issue": [
                    {
                        "severity": severity,
                        "code": issue_code,
                        "details": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                                    "code": "INTERNAL_SERVER_ERROR",
                                    "display": f"Internal server error while processing ODS code '{ods_code}'",
                                },
                            ]
                        },
                    }
                ],
            }
        )

    return _create_error_outcome


class TestLambdaHandler:
    def test_lambda_handler_success_empty_bundle(
        self, lambda_context, mock_ftrs_service, create_test_bundle
    ):
        # Arrange
        ods_code = "O123"
        event = {"odsCode": ods_code}

        # Create an empty test bundle
        bundle = create_test_bundle(bundle_id="empty-bundle")
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        assert response["statusCode"] == 200
        assert response["headers"] == {"Content-Type": "application/fhir+json"}

        # Verify the response body is valid JSON and matches the bundle
        response_body = json.loads(response["body"])
        assert response_body["resourceType"] == "Bundle"
        assert response_body["type"] == "searchset"
        assert response_body["id"] == "empty-bundle"
        assert "entry" in response_body
        assert len(response_body["entry"]) == 0

    def test_lambda_handler_success_with_entries(
        self, lambda_context, mock_ftrs_service, create_test_bundle
    ):
        # Arrange
        ods_code = "O123"
        event = {"odsCode": ods_code}

        # Create a test bundle with 2 endpoints and 2 organizations
        bundle = create_test_bundle(
            bundle_id="test-bundle-with-entries", endpoint_count=2, organization_count=2
        )
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        assert response["statusCode"] == 200
        assert response["headers"] == {"Content-Type": "application/fhir+json"}

        # Verify the response body is valid JSON and matches the bundle
        response_body = json.loads(response["body"])
        assert response_body["resourceType"] == "Bundle"
        assert response_body["id"] == "test-bundle-with-entries"
        assert len(response_body["entry"]) == 4

        # Verify the entries are in the right order - endpoints first, then organizations
        assert response_body["entry"][0]["resource"]["resourceType"] == "Endpoint"
        assert response_body["entry"][0]["resource"]["id"] == "endpoint-0"
        assert response_body["entry"][1]["resource"]["resourceType"] == "Endpoint"
        assert response_body["entry"][1]["resource"]["id"] == "endpoint-1"
        assert response_body["entry"][2]["resource"]["resourceType"] == "Organization"
        assert response_body["entry"][2]["resource"]["id"] == "org-0"
        assert response_body["entry"][3]["resource"]["resourceType"] == "Organization"
        assert response_body["entry"][3]["resource"]["id"] == "org-1"

    def test_lambda_handler_service_error(
        self, lambda_context, mock_ftrs_service, create_error_outcome
    ):
        # Arrange
        ods_code = "O123"
        event = {"odsCode": ods_code}

        # Create an error outcome for a service error
        outcome = create_error_outcome(
            ods_code=ods_code, issue_code="internal-error", severity="error"
        )
        mock_ftrs_service.endpoints_by_ods.return_value = outcome

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        assert response["statusCode"] == 500
        assert response["headers"] == {"Content-Type": "application/fhir+json"}

        # Verify the response body contains the error
        response_body = json.loads(response["body"])
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["severity"] == "error"
