from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from functions.ftrs_service.repository.dynamo import (
    DynamoModel,
    DynamoRepository,
    EndpointValue,
    OrganizationRecord,
    OrganizationValue,
)


# First, improve the mock_dynamodb_table fixture
@pytest.fixture
def mock_dynamodb_table():
    """Create a properly mocked DynamoDB table."""
    mock_table = MagicMock()
    mock_table.query.return_value = {"Items": [], "Count": 0}
    return mock_table


@pytest.fixture
def dynamo_repository(mock_dynamodb_table):
    """Create a DynamoDB repository fixture with properly mocked boto3 resource."""
    with patch("boto3.resource") as mock_boto3_resource:
        mock_boto3_resource.return_value.Table.return_value = mock_dynamodb_table
        repo = DynamoRepository(table_name="test-table")
        # Ensure the boto3 resource is mocked, not real
        assert repo.table == mock_dynamodb_table
        yield repo


@pytest.fixture
def create_sample_dynamo_item():
    """Factory function to create sample DynamoDB items for testing."""

    def _create_sample_dynamo_item(
        org_id: str = "org-123",
        ods_code: str = "O123",
        org_name: str = "Test Organization",
        endpoints: list[dict] = None,
    ) -> dict:
        if endpoints is None:
            endpoints = [
                {
                    "id": "endpoint-123",
                    "identifier_oldDoS_id": 9876,
                    "connectionType": "fhir",
                    "managedByOrganisation": org_id,
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
            ]

        return {
            "id": org_id,
            "ods-code": ods_code,
            "field": "organization",
            "value": {
                "id": org_id,
                "name": org_name,
                "type": "prov",
                "active": True,
                "identifier_ODS_ODSCode": ods_code,
                "telecom": "01234567890",
                "createdBy": "test-user",
                "modifiedBy": "test-user",
                "createdDateTime": "2023-01-01T00:00:00",
                "modifiedDateTime": "2023-01-02T00:00:00",
                "endpoints": endpoints,
            },
        }

    return _create_sample_dynamo_item


class TestDynamoRepository:
    def test_dynamo_repository_init(self):
        # Arrange
        with patch("boto3.resource") as mock_boto3_resource:
            mock_table = mock_boto3_resource.return_value.Table.return_value

            # Act
            repo = DynamoRepository("test-table")

            # Assert
            mock_boto3_resource.assert_called_once_with("dynamodb")
            mock_boto3_resource.return_value.Table.assert_called_once_with("test-table")
            assert repo.table == mock_table

    def test_get_first_record_by_ods_code_found(
        self, dynamo_repository, mock_dynamodb_table, create_sample_dynamo_item
    ):
        # Arrange
        ods_code = "O123"
        test_item = create_sample_dynamo_item()
        mock_dynamodb_table.query.return_value = {
            "Items": [test_item],
            "Count": 1,
        }

        # Mock the record creation to avoid real object validation
        with patch(
            "functions.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item"
        ) as mock_from_dynamo:
            mock_record = MagicMock()
            mock_record.id = "org-123"
            mock_record.ods_code = "O123"
            mock_from_dynamo.return_value = mock_record

            # Act
            result = dynamo_repository.get_first_record_by_ods_code(ods_code)

        # Assert
        mock_dynamodb_table.query.assert_called_once()
        assert result.id == "org-123"
        assert result.ods_code == "O123"

    def test_get_first_record_by_ods_code_multiple_records(
        self, dynamo_repository, mock_dynamodb_table, create_sample_dynamo_item
    ):
        # Arrange
        ods_code = "O123"
        item1 = create_sample_dynamo_item()
        item2 = create_sample_dynamo_item(org_id="org-456")
        mock_dynamodb_table.query.return_value = {
            "Items": [item1, item2],
            "Count": 2,
        }

        # Act
        with patch("functions.ftrs_service.repository.dynamo.logger") as mock_logger:
            with patch(
                "functions.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item"
            ) as mock_from_dynamo:
                mock_record = MagicMock()
                mock_record.id = "org-123"
                mock_from_dynamo.return_value = mock_record

                result = dynamo_repository.get_first_record_by_ods_code(ods_code)

        # Assert
        mock_dynamodb_table.query.assert_called_once()
        mock_logger.warning.assert_called_once()
        assert "Multiple records found" in mock_logger.warning.call_args[0][0]
        assert result.id == "org-123"

    def test_get_first_record_by_ods_code_not_found(
        self, dynamo_repository, mock_dynamodb_table
    ):
        # Arrange
        ods_code = "UNKNOWN"
        mock_dynamodb_table.query.return_value = {"Items": [], "Count": 0}

        # Act
        result = dynamo_repository.get_first_record_by_ods_code(ods_code)

        # Assert
        mock_dynamodb_table.query.assert_called_once()
        assert result is None

    def test_organization_record_from_dynamo_item(self, create_sample_dynamo_item):
        # Act
        result = OrganizationRecord.from_dynamo_item(create_sample_dynamo_item())

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

    def test_organization_record_from_dynamo_item_invalid(self):
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

    def test_dynamo_model_none_to_default(self):
        # Test that None values in the DynamoDB response are converted to default values
        class TestModel(DynamoModel):
            field_with_default: str = "default_value"
            required_field: str

        # When a field with a default is None, it should use the default
        test_data = {"required_field": "value", "field_with_default": None}
        model = TestModel.model_validate(test_data)
        assert model.field_with_default == "default_value"
        assert model.required_field == "value"

    def test_endpoint_value_defaults(self, create_endpoint_value):
        # Ensure EndpointValue correctly sets default values
        endpoint = create_endpoint_value()
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
        self,
        dynamo_repository,
        mock_dynamodb_table,
        ods_code,
        db_response,
        expected_result,
    ):
        # Arrange
        mock_dynamodb_table.query.return_value = db_response

        # Mock the from_dynamo_item method to return a simple object with just the ID
        with patch(
            "functions.ftrs_service.repository.dynamo.OrganizationRecord.from_dynamo_item"
        ) as mock_from_dynamo:
            if expected_result:
                mock_record = OrganizationRecord(
                    id=expected_result,
                    ods_code=ods_code,
                    field="organization",
                    value=OrganizationValue(
                        id=expected_result,
                        name="Test Organization",
                        type="prov",
                        active=True,
                        identifier_ODS_ODSCode=ods_code,
                        createdBy="test-user",
                        modifiedBy="test-user",
                        createdDateTime="2023-01-01T00:00:00",
                        modifiedDateTime="2023-01-02T00:00:00",
                        telecom="dummy-telecom",
                    ),
                )
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
