from decimal import Decimal
from uuid import UUID

import pytest
from boto3.dynamodb.types import TypeSerializer
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    Endpoint,
    HealthcareService,
    Location,
    Organisation,
    PositionGCS,
    SymptomGroupSymptomDiscriminatorPair,
    Telecom,
)
from ftrs_data_layer.domain.legacy.service import (
    Service,
)
from pydantic import BaseModel
from pytest_mock import MockerFixture
from sqlalchemy import Engine

from common.cache import DoSMetadataCache
from service_migration.config import DataMigrationConfig
from service_migration.processor import (
    DataMigrationMetrics,
    DataMigrationProcessor,
    ServiceTransformOutput,
)
from service_migration.validation.types import ValidationIssue, ValidationResult


def test_processor_init(
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    assert processor.logger == mock_logger
    assert processor.config == mock_config
    assert isinstance(processor.engine, Engine)
    assert processor.metrics.model_dump() == {
        "errors": 0,
        "migrated_records": 0,
        "skipped_records": 0,
        "supported_records": 0,
        "total_records": 0,
        "transformed_records": 0,
        "unsupported_records": 0,
        "invalid_records": 0,
    }


def test_sync_all_services(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    processor._process_service = mocker.MagicMock()

    mock_session = mocker.MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.scalars = mocker.MagicMock(return_value=[mock_legacy_service])

    mocker.patch("service_migration.processor.Session", return_value=mock_session)

    assert processor.sync_all_services() is None

    assert processor._process_service.call_count == 1
    processor._process_service.assert_called_once_with(mock_legacy_service)


def test_sync_service(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    processor._process_service = mocker.MagicMock()

    mock_session = mocker.MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.get.return_value = mock_legacy_service

    mocker.patch("service_migration.processor.Session", return_value=mock_session)

    record_id = 1
    method = "test_method"

    assert processor.sync_service(record_id, method) is None

    assert processor._process_service.call_count == 1
    processor._process_service.assert_called_once_with(mock_legacy_service)

    assert mock_session.get.call_count == 1
    mock_session.get.assert_called_once_with(Service, record_id)


def test_sync_service_record_not_found(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_session = mocker.MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    mocker.patch("service_migration.processor.Session", return_value=mock_session)

    record_id = 1
    method = "test_method"

    with pytest.raises(ValueError, match=f"Service with ID {record_id} not found"):
        processor.sync_service(record_id, method)


@freeze_time("2025-07-25 12:00:00")
def test_process_service(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._save = mocker.MagicMock()
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    assert processor.metrics == DataMigrationMetrics(
        total_records=0,
        supported_records=0,
        unsupported_records=0,
        transformed_records=0,
        migrated_records=0,
        skipped_records=0,
        invalid_records=0,
        errors=0,
    )

    processor._process_service(service=mock_legacy_service)

    assert processor.metrics == DataMigrationMetrics(
        total_records=1,
        supported_records=1,
        unsupported_records=0,
        transformed_records=1,
        migrated_records=1,
        skipped_records=0,
        invalid_records=0,
        errors=0,
    )

    assert mock_logger.was_logged("DM_ETL_004") is False
    assert mock_logger.was_logged("DM_ETL_005") is False
    assert mock_logger.was_logged("DM_ETL_006") is True

    assert processor._save.call_count == 1

    output = processor._save.call_args[0][0]
    assert isinstance(output, ServiceTransformOutput)
    assert len(output.organisation) == 1
    assert output.organisation[0] == Organisation(
        id="4539600c-e04e-5b35-a582-9fb36858d0e0",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        identifier_ODS_ODSCode="A12345",
        identifier_oldDoS_uid="test-uid",
        active=True,
        name="Public Test Service",
        telecom=None,
        type="GP Practice",
        endpoints=[
            Endpoint(
                id="a226aaa5-392c-59c8-8d79-563bb921cb0d",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-25T12:00:00+00:00",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-25T12:00:00+00:00",
                identifier_oldDoS_id=1,
                status="active",
                connectionType="http",
                name=None,
                payloadMimeType=None,
                description="Primary",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="http://example.com/endpoint",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=1,
                isCompressionEnabled=True,
            ),
            Endpoint(
                id="4d678d9c-61db-584f-a64c-bd8eb829d8db",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-25T12:00:00+00:00",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-25T12:00:00+00:00",
                identifier_oldDoS_id=2,
                status="active",
                connectionType="email",
                name=None,
                payloadMimeType=None,
                description="Copy",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="mailto:test@example.com",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=2,
                isCompressionEnabled=False,
            ),
        ],
    )

    assert len(output.healthcare_service) == 1
    assert output.healthcare_service[0] == HealthcareService(
        id="903cd48b-5d0f-532f-94f4-937a4517b14d",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        identifier_oldDoS_uid="test-uid",
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        providedBy="4539600c-e04e-5b35-a582-9fb36858d0e0",
        location="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        migrationNotes=[],
        name="Test Service",
        telecom=Telecom(
            phone_public="01234567890",
            phone_private="09876543210",
            email="firstname.lastname@nhs.net",
            web="http://example.com",
        ),
        openingTime=[
            AvailableTime(
                category="availableTime",
                dayOfWeek="mon",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="tue",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="09:00:00",
                endTime="12:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="13:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="thu",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="fri",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="sat",
                startTime="10:00:00",
                endTime="14:00:00",
                allDay=False,
            ),
            AvailableTimePublicHolidays(
                category="availableTimePublicHolidays",
                startTime="10:00:00",
                endTime="14:00:00",
            ),
        ],
        symptomGroupSymptomDiscriminators=[
            SymptomGroupSymptomDiscriminatorPair(
                sg=1035,
                sd=4003,
            ),
            SymptomGroupSymptomDiscriminatorPair(
                sg=360,
                sd=14023,
            ),
        ],
        dispositions=["DX115", "DX12"],
    )

    assert len(output.location) == 1
    assert output.location[0] == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        identifier_oldDoS_uid="test-uid",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        active=True,
        address=Address(
            line1="123 Main St",
            line2=None,
            county="West Yorkshire",
            town="Leeds",
            postcode="AB12 3CD",
        ),
        managingOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
        name=None,
        positionGCS=PositionGCS(
            latitude=Decimal("51.5074"), longitude=Decimal("-0.1278")
        ),
        positionReferenceNumber_UPRN=None,
        positionReferenceNumber_UBRN=None,
        primaryAddress=True,
        partOf=None,
    )


def test_process_service_unsupported_service(
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache
    mock_legacy_service.typeid = 1000

    processor._process_service(mock_legacy_service)

    assert processor.metrics == DataMigrationMetrics(
        total_records=1,
        supported_records=0,
        unsupported_records=1,
        transformed_records=0,
        migrated_records=0,
        skipped_records=0,
        errors=0,
    )

    assert mock_logger.get_log("DM_ETL_004") == [
        {
            "msg": "Record was not migrated due to reason: No suitable transformer found",
            "detail": {"reason": "No suitable transformer found"},
            "reference": "DM_ETL_004",
        }
    ]


def test_process_service_skipped_service(
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    mock_legacy_service.statusid = 2  # Closed status

    processor._process_service(mock_legacy_service)

    assert processor.metrics == DataMigrationMetrics(
        total_records=1,
        supported_records=1,
        unsupported_records=0,
        transformed_records=0,
        migrated_records=0,
        skipped_records=1,
        errors=0,
    )

    assert mock_logger.get_log("DM_ETL_005") == [
        {
            "msg": "Record skipped due to condition: Service is not active",
            "detail": {"reason": "Service is not active"},
            "reference": "DM_ETL_005",
        }
    ]


def test_handles_invalid_service(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    # Arrange transformer and patch lookup to return it
    mock_transformer = mocker.MagicMock()
    mock_transformer.__name__ = "MockTransformer"
    mock_transformer.is_service_supported.return_value = (True, None)
    mock_transformer.should_include_service.return_value = (True, None)
    mock_transformer.return_value = mock_transformer
    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS", [mock_transformer]
    )

    # A fatal issue => is_valid == False and should_continue == False
    fatal_issue = ValidationIssue(
        severity="fatal",
        code="TEST_FATAL",
        diagnostics="Invalid data encountered",
        value=None,
        expression=["some.field"],
    )
    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[fatal_issue],
        sanitised=mock_legacy_service,  # pass the (sanitised) service, not metadata
    )
    mock_transformer.validator.validate.return_value = validation_result

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._save = mocker.MagicMock()

    assert processor.metrics == DataMigrationMetrics(
        total_records=0,
        supported_records=0,
        unsupported_records=0,
        transformed_records=0,
        migrated_records=0,
        skipped_records=0,
        invalid_records=0,
        errors=0,
    )

    processor._process_service(mock_legacy_service)

    assert processor.metrics == DataMigrationMetrics(
        total_records=1,
        supported_records=1,
        unsupported_records=0,
        transformed_records=0,
        migrated_records=0,
        skipped_records=0,
        invalid_records=1,
        errors=0,
    )
    mock_transformer.transform.assert_not_called()
    processor._save.assert_not_called()


def test_process_service_error(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    processor._save = mocker.MagicMock(side_effect=Exception("Test error"))
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    processor._process_service(mock_legacy_service)

    assert processor.metrics == DataMigrationMetrics(
        total_records=1,
        supported_records=1,
        unsupported_records=0,
        transformed_records=1,
        migrated_records=0,
        skipped_records=0,
        errors=1,
    )

    assert mock_logger.get_log("DM_ETL_008") == [
        {
            "msg": "Error processing record: Test error",
            "detail": {"error": "Test error"},
            "reference": "DM_ETL_008",
        }
    ]


def test_get_transformer(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
) -> None:
    mock_transformer = mocker.MagicMock()
    mock_transformer.__name__ = "MockTransformer"
    mock_transformer.is_service_supported.return_value = (True, None)
    mock_transformer.return_value = mock_transformer

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS", [mock_transformer]
    )

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    transformer = processor.get_transformer(mock_legacy_service)

    assert transformer == mock_transformer

    mock_transformer.assert_called_once_with(
        logger=processor.logger,
        metadata=processor.metadata,
    )
    assert mock_transformer.is_service_supported.call_count == 1
    mock_transformer.is_service_supported.assert_called_once_with(mock_legacy_service)

    assert mock_logger.was_logged("DM_ETL_002") is False
    assert mock_logger.get_log("DM_ETL_003") == [
        {
            "msg": "Transformer MockTransformer selected for record",
            "detail": {"transformer_name": "MockTransformer"},
            "reference": "DM_ETL_003",
        }
    ]


def test_get_transformer_not_supported(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
) -> None:
    mock_transformer = mocker.MagicMock()
    mock_transformer.__name__ = "MockTransformer"
    mock_transformer.is_service_supported.return_value = (False, "Unsupported type")

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS", [mock_transformer]
    )

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    transformer = processor.get_transformer(mock_legacy_service)

    assert transformer is None

    assert mock_transformer.is_service_supported.call_count == 1
    mock_transformer.is_service_supported.assert_called_once_with(mock_legacy_service)

    assert mock_logger.was_logged("DM_ETL_003") is False
    assert mock_logger.get_log("DM_ETL_002") == [
        {
            "msg": "Transformer MockTransformer is not valid for record: Unsupported type",
            "detail": {
                "transformer_name": "MockTransformer",
                "reason": "Unsupported type",
            },
            "reference": "DM_ETL_002",
        }
    ]


def test_save(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Mock DynamoDB client
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items = mocker.MagicMock()

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False (not exists)
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    processor._save(result, mock_legacy_service.id)

    # Verify transact_write_items was called once
    assert mock_dynamodb_client.transact_write_items.call_count == 1

    # Verify the transaction contains items for:
    # - 1 organisation
    # - 1 location
    # - 1 healthcare service
    # - 1 data migration state
    transact_items = mock_dynamodb_client.transact_write_items.call_args[1][
        "TransactItems"
    ]
    noItems = 4
    assert len(transact_items) == noItems

    # Verify all items are Put operations
    for item in transact_items:
        assert "Put" in item
        assert "TableName" in item["Put"]
        assert "Item" in item["Put"]


def test_verify_state_record_exist_returns_true_when_state_exists(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that verify_state_record_exist returns True when state record exists."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Mock logger debug method
    processor.logger.debug = mocker.MagicMock()

    # Mock DynamoDB client
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.get_item.return_value = {
        "Item": {
            "source_record_id": {"S": "services#123"},
            "version": {"N": "1"},
        }
    }

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    result = processor.verify_state_record_exist(123)

    assert result is True
    mock_dynamodb_client.get_item.assert_called_once_with(
        TableName="ftrs-dos-test-database-data-migration-state-test_workspace",
        Key={
            "source_record_id": {"S": "services#123"},
        },
    )


def test_verify_state_record_exist_returns_false_when_state_not_exists(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that verify_state_record_exist returns False when state record doesn't exist."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Mock logger debug method
    processor.logger.debug = mocker.MagicMock()

    # Mock DynamoDB client - no Item in response
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.get_item.return_value = {}

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    result = processor.verify_state_record_exist(456)

    assert result is False
    mock_dynamodb_client.get_item.assert_called_once_with(
        TableName="ftrs-dos-test-database-data-migration-state-test_workspace",
        Key={
            "source_record_id": {"S": "services#456"},
        },
    )


def test_verify_state_record_exist_handles_exception(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that verify_state_record_exist raises exceptions when DynamoDB errors occur."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Mock DynamoDB client to raise exception
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.get_item.side_effect = Exception("DynamoDB error")

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Should raise the exception
    with pytest.raises(Exception, match="DynamoDB error"):
        processor.verify_state_record_exist(789)


def test_verify_state_record_exist_constructs_correct_source_record_id(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that verify_state_record_exist constructs the correct source_record_id."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Mock logger debug method
    processor.logger.debug = mocker.MagicMock()

    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.get_item.return_value = {}

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    processor.verify_state_record_exist(12345)

    # Verify the source_record_id format
    call_args = mock_dynamodb_client.get_item.call_args
    assert call_args[1]["Key"]["source_record_id"]["S"] == "services#12345"


def test_verify_state_record_exist_uses_correct_table_name(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that verify_state_record_exist uses the correct table name."""
    # Modify config for this test
    mock_config.env = "dev"
    mock_config.workspace = "my_workspace"

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Mock logger debug method
    processor.logger.debug = mocker.MagicMock()

    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.get_item.return_value = {}

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    processor.verify_state_record_exist(999)

    # Verify the table name format
    call_args = mock_dynamodb_client.get_item.call_args
    assert (
        call_args[1]["TableName"]
        == "ftrs-dos-dev-database-data-migration-state-my_workspace"
    )


def test_create_put_item_basic_functionality(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item creates correct DynamoDB Put item structure."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Create a mock model
    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "test-uuid-123"
    mock_model.model_dump.return_value = {
        "name": "Test Name",
        "status": "active",
        "count": 42,
    }

    serializer = TypeSerializer()
    table_name = "test-table"

    result = processor._create_put_item(mock_model, table_name, serializer)

    # Verify structure
    assert "Put" in result
    assert "TableName" in result["Put"]
    assert result["Put"]["TableName"] == table_name
    assert "Item" in result["Put"]

    # Verify required fields are added
    item = result["Put"]["Item"]
    assert "id" in item
    assert "field" in item
    assert item["id"]["S"] == "test-uuid-123"
    assert item["field"]["S"] == "document"

    # Verify model data is included
    assert "name" in item
    assert "status" in item
    assert "count" in item


def test_create_put_item_with_condition_expression(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item includes condition expression by default."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "test-uuid"
    mock_model.model_dump.return_value = {"name": "Test"}

    serializer = TypeSerializer()

    result = processor._create_put_item(
        mock_model, "test-table", serializer, with_condition=True
    )

    # Verify condition expression is present
    assert "ConditionExpression" in result["Put"]
    assert (
        result["Put"]["ConditionExpression"]
        == "attribute_not_exists(id) AND attribute_not_exists(#field)"
    )

    # Verify expression attribute names
    assert "ExpressionAttributeNames" in result["Put"]
    assert result["Put"]["ExpressionAttributeNames"] == {"#field": "field"}


def test_create_put_item_without_condition_expression(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item can skip condition expression when requested."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "test-uuid"
    mock_model.model_dump.return_value = {"name": "Test"}

    serializer = TypeSerializer()

    result = processor._create_put_item(
        mock_model, "test-table", serializer, with_condition=False
    )

    # Verify condition expression is NOT present
    assert "ConditionExpression" not in result["Put"]
    assert "ExpressionAttributeNames" not in result["Put"]


def test_create_put_item_serializes_data_correctly(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item properly serializes different data types."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "uuid-123"
    mock_model.model_dump.return_value = {
        "string_field": "test",
        "number_field": 42,
        "boolean_field": True,
        "list_field": ["a", "b", "c"],
        "dict_field": {"key": "value"},
        "null_field": None,
    }

    serializer = TypeSerializer()

    result = processor._create_put_item(mock_model, "test-table", serializer)

    item = result["Put"]["Item"]

    # Verify string serialization
    assert item["string_field"]["S"] == "test"

    # Verify number serialization
    assert item["number_field"]["N"] == "42"

    # Verify boolean serialization
    assert item["boolean_field"]["BOOL"] is True

    # Verify list serialization
    assert "L" in item["list_field"]

    # Verify dict serialization
    assert "M" in item["dict_field"]

    # Verify null serialization
    assert item["null_field"]["NULL"] is True


def test_create_put_item_converts_id_to_string(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item converts model.id to string."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Test with UUID
    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = UUID("12345678-1234-5678-1234-567812345678")
    mock_model.model_dump.return_value = {"name": "Test"}

    serializer = TypeSerializer()

    result = processor._create_put_item(mock_model, "test-table", serializer)

    # Verify ID is converted to string
    assert result["Put"]["Item"]["id"]["S"] == "12345678-1234-5678-1234-567812345678"
    assert isinstance(result["Put"]["Item"]["id"]["S"], str)


def test_create_put_item_adds_field_attribute(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item always adds 'field' attribute set to 'document'."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "test-id"
    mock_model.model_dump.return_value = {"name": "Test"}

    serializer = TypeSerializer()

    result = processor._create_put_item(mock_model, "test-table", serializer)

    # Verify field attribute
    assert "field" in result["Put"]["Item"]
    assert result["Put"]["Item"]["field"]["S"] == "document"


def test_create_put_item_with_organisation_model(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test _create_put_item with a real Organisation model structure."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    # Create a mock organisation
    mock_org = mocker.MagicMock(spec=Organisation)
    mock_org.id = "org-uuid-123"
    mock_org.model_dump.return_value = {
        "identifier_ODS_ODSCode": "ABC123",
        "name": "Test Organisation",
        "active": True,
        "type": "GP Practice",
    }

    serializer = TypeSerializer()
    table_name = "ftrs-dos-test-organisation"

    result = processor._create_put_item(mock_org, table_name, serializer)

    # Verify organisation-specific fields are serialized
    item = result["Put"]["Item"]
    assert item["identifier_ODS_ODSCode"]["S"] == "ABC123"
    assert item["name"]["S"] == "Test Organisation"
    assert item["active"]["BOOL"] is True
    assert item["type"]["S"] == "GP Practice"


def test_create_put_item_calls_model_dump_with_json_mode(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    """Test that _create_put_item calls model_dump with mode='json'."""

    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )

    mock_model = mocker.MagicMock(spec=BaseModel)
    mock_model.id = "test-id"
    mock_model.model_dump.return_value = {"name": "Test"}

    serializer = TypeSerializer()

    processor._create_put_item(mock_model, "test-table", serializer)

    # Verify model_dump was called with mode="json"
    mock_model.model_dump.assert_called_once_with(mode="json")
