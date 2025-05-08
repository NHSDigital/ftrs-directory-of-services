from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper
from functions.ftrs_service.ftrs_service import FtrsService
from functions.ftrs_service.repository.dynamo import (
    DynamoRepository,
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


@pytest.fixture
def endpoint_value():
    return EndpointValue(
        id="endpoint-123",
        identifier_oldDoS_id=9876,
        connectionType="fhir",
        managedByOrganisation="org-123",
        payloadType="document",
        format="PDF",
        address="https://example.org/fhir",
        order=1,
        isCompressionEnabled=True,
        description="Test scenario",
        status="active",
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )


@pytest.fixture
def organization_value(endpoint_value):
    return OrganizationValue(
        id="org-123",
        name="Test Organization",
        type="prov",
        active=True,
        identifier_ODS_ODSCode="O123",
        telecom="01234567890",
        endpoints=[endpoint_value],
        createdBy="test-user",
        modifiedBy="test-user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedDateTime=datetime(2023, 1, 2),
    )


@pytest.fixture
def organization_record(organization_value):
    return OrganizationRecord(
        id="org-123",
        ods_code="O123",
        field="organization",
        value=organization_value,
    )


@pytest.fixture
def mock_config():
    with patch("functions.ftrs_service.ftrs_service.get_config") as mock:
        mock.return_value = {
            "DYNAMODB_TABLE_NAME": "test-table",
            "FHIR_BASE_URL": "https://test-base-url.org",
        }
        yield mock


@pytest.fixture
def mock_repository(organization_record):
    with patch("functions.ftrs_service.ftrs_service.DynamoRepository") as mock_class:
        mock_repo = MagicMock(spec=DynamoRepository)
        mock_repo.get_first_record_by_ods_code.return_value = organization_record
        mock_class.return_value = mock_repo
        yield mock_repo


@pytest.fixture
def mock_bundle_mapper():
    with patch("functions.ftrs_service.ftrs_service.BundleMapper") as mock_class:
        mock_mapper = MagicMock(spec=BundleMapper)
        mock_bundle = MagicMock(spec=Bundle)
        mock_mapper.map_to_fhir.return_value = mock_bundle
        mock_class.return_value = mock_mapper
        yield mock_mapper


@pytest.fixture
def ftrs_service(mock_config, mock_repository, mock_bundle_mapper):
    return FtrsService()


def test_init(mock_config, mock_repository, mock_bundle_mapper):
    # Act
    service = FtrsService()

    # Assert
    assert service.repository == mock_repository
    assert service.mapper == mock_bundle_mapper


def test_endpoints_by_ods_success(
    ftrs_service, mock_repository, mock_bundle_mapper, organization_record
):
    # Arrange
    ods_code = "O123"
    expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

    # Act
    result = ftrs_service.endpoints_by_ods(ods_code)

    # Assert
    mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
    mock_bundle_mapper.map_to_fhir.assert_called_once_with(organization_record)
    assert result == expected_bundle


def test_endpoints_by_ods_not_found(ftrs_service, mock_repository, mock_bundle_mapper):
    # Arrange
    ods_code = "UNKNOWN"
    mock_repository.get_first_record_by_ods_code.return_value = None

    # Create a mock OperationOutcome that matches the structure in the actual implementation
    error_outcome = OperationOutcome.model_construct(
        id="not-found",
        resourceType="OperationOutcome",
        issue=[
            {
                "severity": "error",
                "code": "not-found",
                "details": {"text": f"No organization found for ODS code: {ods_code}"},
            }
        ],
    )

    # Patch the _create_error_resource method to return our mock
    with patch.object(
        ftrs_service, "_create_error_resource", return_value=error_outcome
    ):
        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_not_called()
        assert isinstance(result, OperationOutcome)
        assert result.id == "not-found"
        # Access the issue dictionary properly
        assert result.issue[0]["severity"] == "error"
        assert result.issue[0]["code"] == "not-found"
        assert (
            f"No organization found for ODS code: {ods_code}"
            in result.issue[0]["details"]["text"]
        )


def test_endpoints_by_ods_exception(ftrs_service, mock_repository, mock_bundle_mapper):
    # Arrange
    ods_code = "O123"
    mock_repository.get_first_record_by_ods_code.side_effect = Exception(
        "Test exception"
    )

    # Create a mock OperationOutcome that matches the structure in the actual implementation
    error_outcome = OperationOutcome.model_construct(
        id="not-found",
        resourceType="OperationOutcome",
        issue=[
            {
                "severity": "error",
                "code": "not-found",
                "details": {"text": f"No organization found for ODS code: {ods_code}"},
            }
        ],
    )

    # Patch the _create_error_resource method to return our mock
    with patch.object(
        ftrs_service, "_create_error_resource", return_value=error_outcome
    ):
        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_not_called()
        assert isinstance(result, OperationOutcome)
        assert result.id == "not-found"
        # Access the issue dictionary properly
        assert result.issue[0]["severity"] == "error"
        assert result.issue[0]["code"] == "not-found"


def test_endpoints_by_ods_mapping_exception(
    ftrs_service, mock_repository, mock_bundle_mapper, organization_record
):
    # Arrange
    ods_code = "O123"
    mock_bundle_mapper.map_to_fhir.side_effect = Exception("Mapping error")

    # Create a mock OperationOutcome that matches the structure in the actual implementation
    error_outcome = OperationOutcome.model_construct(
        id="not-found",
        resourceType="OperationOutcome",
        issue=[
            {
                "severity": "error",
                "code": "not-found",
                "details": {"text": f"No organization found for ODS code: {ods_code}"},
            }
        ],
    )

    # Patch the _create_error_resource method to return our mock
    with patch.object(
        ftrs_service, "_create_error_resource", return_value=error_outcome
    ):
        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organization_record)
        assert isinstance(result, OperationOutcome)
