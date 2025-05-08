from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from boto3.dynamodb.conditions import Key
from pydantic import ValidationError

from functions.ftrs_service.repository.dynamo import (
    DynamoModel,
    DynamoRepository,
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


@pytest.fixture
def mock_dynamodb_table():
    """Mock the DynamoDB table."""
    with patch("boto3.resource") as mock_boto3_resource:
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        yield mock_table


@pytest.fixture
def endpoint_value():
    """Create a standard test endpoint value."""
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
    """Create a standard test organization value with the default endpoint."""
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
    """Create a standard test organization record with the default organization value."""
    return OrganizationRecord(
        id="org-123",
        ods_code="O123",
        field="organization",
        value=organization_value,
    )


@pytest.fixture
def sample_dynamo_item():
    """Create a sample DynamoDB item for testing."""
    return {
        "id": "org-123",
        "ods-code": "O123",
        "field": "organization",
        "value": {
            "id": "org-123",
            "name": "Test Organization",
            "type": "prov",
            "active": True,
            "identifier_ODS_ODSCode": "O123",
            "telecom": "01234567890",
            "createdBy": "test-user",
            "modifiedBy": "test-user",
            "createdDateTime": "2023-01-01T00:00:00",
            "modifiedDateTime": "2023-01-02T00:00:00",
            "endpoints": [
                {
                    "id": "endpoint-123",
                    "identifier_oldDoS_id": 9876,
                    "connectionType": "fhir",
                    "managedByOrganisation": "org-123",
                    "payloadType": "document",
                    "format": "PDF",
                    "address": "https://example.org/fhir",
                    "order": 1,
                    "isCompressionEnabled": True,
                    "description": "Test scenario",
                    "status": "active",
                    "createdBy": "test-user",
                    "modifiedBy": "test-user",
                    "createdDateTime": "2023-01-01T00:00:00",
                    "modifiedDateTime": "2023-01-02T00:00:00",
                    "service": "dummy-service",
                    "name": "dummy-name",
                }
            ],
        },
    }


@pytest.fixture
def dynamo_repository(mock_dynamodb_table):
    """Create a DynamoDB repository fixture with mocked table."""
    return DynamoRepository(table_name="test-table")


def test_dynamo_repository_init():
    # Arrange
    with patch("boto3.resource") as mock_boto3_resource:
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        # Act
        repo = DynamoRepository("test-table")

        # Assert
        mock_boto3_resource.assert_called_once_with("dynamodb")
        mock_dynamodb.Table.assert_called_once_with("test-table")
        assert repo.table == mock_table


def test_get_first_record_by_ods_code_found(
    dynamo_repository, mock_dynamodb_table, sample_dynamo_item
):
    # Arrange
    ods_code = "O123"
    mock_dynamodb_table.query.return_value = {"Items": [sample_dynamo_item], "Count": 1}

    # Act
    result = dynamo_repository.get_first_record_by_ods_code(ods_code)

    # Assert
    mock_dynamodb_table.query.assert_called_once_with(
        IndexName="ods-code-index",
        KeyConditionExpression=Key("ods-code").eq(ods_code),
    )
    assert isinstance(result, OrganizationRecord)
    assert result.id == "org-123"
    assert result.ods_code == "O123"
    assert result.value.name == "Test Organization"
    assert len(result.value.endpoints) == 1
    assert result.value.endpoints[0].id == "endpoint-123"


def test_get_first_record_by_ods_code_multiple_records(
    dynamo_repository, mock_dynamodb_table, sample_dynamo_item
):
    # Arrange
    ods_code = "O123"
    second_item = {**sample_dynamo_item, "id": "org-456"}
    mock_dynamodb_table.query.return_value = {
        "Items": [sample_dynamo_item, second_item],
        "Count": 2,
    }

    # Act
    with patch("functions.ftrs_service.repository.dynamo.logger") as mock_logger:
        result = dynamo_repository.get_first_record_by_ods_code(ods_code)

    # Assert
    mock_dynamodb_table.query.assert_called_once()
    mock_logger.warning.assert_called_once()
    assert "Multiple records found" in mock_logger.warning.call_args[0][0]
    assert isinstance(result, OrganizationRecord)
    assert result.id == "org-123"  # Should return the first item


def test_get_first_record_by_ods_code_not_found(dynamo_repository, mock_dynamodb_table):
    # Arrange
    ods_code = "UNKNOWN"
    mock_dynamodb_table.query.return_value = {"Items": [], "Count": 0}

    # Act
    result = dynamo_repository.get_first_record_by_ods_code(ods_code)

    # Assert
    mock_dynamodb_table.query.assert_called_once()
    assert result is None


def test_organization_record_from_dynamo_item(sample_dynamo_item):
    # Act
    result = OrganizationRecord.from_dynamo_item(sample_dynamo_item)

    # Assert
    assert isinstance(result, OrganizationRecord)
    assert result.id == "org-123"
    assert result.ods_code == "O123"
    assert result.field == "organization"
    assert isinstance(result.value, OrganizationValue)
    assert result.value.name == "Test Organization"
    assert result.value.active is True
    assert len(result.value.endpoints) == 1
    assert isinstance(result.value.endpoints[0], EndpointValue)
    assert result.value.endpoints[0].id == "endpoint-123"


def test_organization_record_from_dynamo_item_invalid():
    # Arrange
    invalid_item = {
        "id": "org-123",
        # Missing required fields
    }

    # Act & Assert
    with patch("functions.ftrs_service.repository.dynamo.logger") as mock_logger:
        with pytest.raises(ValidationError, match=r"\d+ validation errors"):
            OrganizationRecord.from_dynamo_item(invalid_item)

    # Should log the error with the item details
    mock_logger.exception.assert_called_once()
    assert "Error validating DynamoDB item" in mock_logger.exception.call_args[0][0]


def test_dynamo_model_none_to_default():
    # Test that None values in the DynamoDB response are converted to default values
    class TestModel(DynamoModel):
        field_with_default: str = "default_value"
        required_field: str

    # When a field with a default is None, it should use the default
    test_data = {"required_field": "value", "field_with_default": None}
    model = TestModel.model_validate(test_data)
    assert model.field_with_default == "default_value"
    assert model.required_field == "value"


def test_endpoint_value_defaults():
    # Test that EndpointValue sets default values for optional fields
    minimal_data = {
        "id": "endpoint-123",
        "identifier_oldDoS_id": 9876,
        "address": "https://example.org/fhir",
        "format": "PDF",
        "description": "Test scenario",
        "isCompressionEnabled": True,
        "connectionType": "fhir",
        "payloadType": "document",
        "managedByOrganisation": "org-123",
        "status": "active",
        "order": 1,
        "createdBy": "test-user",
        "modifiedBy": "test-user",
        "createdDateTime": datetime(2023, 1, 1),
        "modifiedDateTime": datetime(2023, 1, 2),
    }

    endpoint = EndpointValue(**minimal_data)
    assert endpoint.service == "dummy-service"  # Default value
    assert endpoint.name == "dummy-name"  # Default value


@pytest.mark.parametrize(
    ("ods_code", "db_response", "expected_result"),
    [
        # Case 1: Normal response with a single item
        (
            "O123",
            {"Items": [{"id": "org-123", "ods-code": "O123"}], "Count": 1},
            "org-123",
        ),
        # Case 2: Multiple items returned
        (
            "O456",
            {
                "Items": [
                    {"id": "org-456", "ods-code": "O456"},
                    {"id": "org-789", "ods-code": "O456"},
                ],
                "Count": 2,
            },
            "org-456",
        ),
        # Case 3: No items found
        ("UNKNOWN", {"Items": [], "Count": 0}, None),
    ],
)
def test_get_first_record_by_ods_code_parameterized(
    dynamo_repository, mock_dynamodb_table, ods_code, db_response, expected_result
):
    # Arrange
    mock_dynamodb_table.query.return_value = db_response

    # Mock the from_dynamo_item method to return a simple object with just the ID
    with patch(
        "functions.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item"
    ) as mock_from_dynamo:
        if expected_result:
            mock_record = MagicMock()
            mock_record.id = expected_result
            mock_from_dynamo.return_value = mock_record

        # Act
        result = dynamo_repository.get_first_record_by_ods_code(ods_code)

    # Assert
    mock_dynamodb_table.query.assert_called_once()

    if expected_result:
        assert result is not None
        assert result.id == expected_result
        mock_from_dynamo.assert_called_once()
    else:
        assert result is None
        mock_from_dynamo.assert_not_called()
