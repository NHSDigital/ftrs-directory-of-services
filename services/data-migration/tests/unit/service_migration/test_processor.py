from decimal import Decimal

import pytest
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    Endpoint,
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
    PositionGCS,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.legacy.service import (
    Service,
)
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
        createdBy={"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        createdTime="2025-07-25T12:00:00+00:00",
        lastUpdatedBy={
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        },
        lastUpdated="2025-07-25T12:00:00+00:00",
        identifier_ODS_ODSCode="A12345",
        identifier_oldDoS_uid="test-uid",
        active=True,
        name="Public Test Service",
        telecom=[],
        type="GP Practice",
        endpoints=[
            Endpoint(
                id="a226aaa5-392c-59c8-8d79-563bb921cb0d",
                createdBy={
                    "type": "app",
                    "value": "INTERNAL001",
                    "display": "Data Migration",
                },
                createdTime="2025-07-25T12:00:00+00:00",
                lastUpdatedBy={
                    "type": "app",
                    "value": "INTERNAL001",
                    "display": "Data Migration",
                },
                lastUpdated="2025-07-25T12:00:00+00:00",
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
                comment="Test Endpoint",
            ),
            Endpoint(
                id="4d678d9c-61db-584f-a64c-bd8eb829d8db",
                createdBy={
                    "type": "app",
                    "value": "INTERNAL001",
                    "display": "Data Migration",
                },
                createdTime="2025-07-25T12:00:00+00:00",
                lastUpdatedBy={
                    "type": "app",
                    "value": "INTERNAL001",
                    "display": "Data Migration",
                },
                lastUpdated="2025-07-25T12:00:00+00:00",
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
                comment="Test Email Endpoint",
            ),
        ],
    )

    assert len(output.healthcare_service) == 1
    assert output.healthcare_service[0] == HealthcareService(
        id="903cd48b-5d0f-532f-94f4-937a4517b14d",
        createdBy={"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        createdTime="2025-07-25T12:00:00+00:00",
        lastUpdatedBy={
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        },
        lastUpdated="2025-07-25T12:00:00+00:00",
        identifier_oldDoS_uid="test-uid",
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        providedBy="4539600c-e04e-5b35-a582-9fb36858d0e0",
        location="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        migrationNotes=[],
        name="Test Service",
        telecom=HealthcareServiceTelecom(
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
        createdBy={"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        createdTime="2025-07-25T12:00:00+00:00",
        lastUpdatedBy={
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        },
        lastUpdated="2025-07-25T12:00:00+00:00",
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


def test_save_handles_transaction_cancelled_with_conditional_check_failed(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save handles TransactionCanceledException with ConditionalCheckFailed gracefully."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Create a real exception (not a MagicMock) with proper attributes
    class MockTransactionCanceledException(Exception):
        def __init__(self) -> None:
            super().__init__("Transaction cancelled")
            self.response = {
                "Error": {"Code": "TransactionCanceledException"},
                "CancellationReasons": [
                    {"Code": "ConditionalCheckFailed"},
                    {"Code": "ConditionalCheckFailed"},
                    {"Code": "ConditionalCheckFailed"},
                    {"Code": "ConditionalCheckFailed"},
                ],
            }

    # Create an instance of the exception
    mock_exception = MockTransactionCanceledException()
    # Set the class name to match what the code checks
    mock_exception.__class__.__name__ = "TransactionCanceledException"

    # Mock DynamoDB client to raise the exception
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items.side_effect = mock_exception

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    # Should not raise exception, should return gracefully
    processor._save(result, mock_legacy_service.id)

    # Verify DM_ETL_022 was logged
    logs = mock_logger.get_log("DM_ETL_022")
    assert len(logs) > 0, "DM_ETL_022 was not logged"
    assert logs[0]["reference"] == "DM_ETL_022"


def test_save_handles_transaction_cancelled_without_conditional_check_failed(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save re-raises TransactionCanceledException if not due to ConditionalCheckFailed."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Create a real exception with different cancellation reasons
    class MockTransactionCanceledException(Exception):
        def __init__(self) -> None:
            super().__init__("Transaction cancelled")
            self.response = {
                "Error": {"Code": "TransactionCanceledException"},
                "CancellationReasons": [
                    {"Code": "ValidationError"},
                    {"Code": "ThrottlingError"},
                ],
            }

    mock_exception = MockTransactionCanceledException()
    mock_exception.__class__.__name__ = "TransactionCanceledException"

    # Mock DynamoDB client to raise the exception
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items.side_effect = mock_exception

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    # Should raise the exception since it's not ConditionalCheckFailed
    with pytest.raises(Exception):
        processor._save(result, mock_legacy_service.id)


def test_save_handles_other_exceptions(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save re-raises non-TransactionCanceledException exceptions."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Mock DynamoDB client to raise a different exception
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items.side_effect = Exception(
        "Some other DynamoDB error"
    )

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    # Should raise the exception
    with pytest.raises(Exception, match="Some other DynamoDB error"):
        processor._save(result, mock_legacy_service.id)


def test_save_checks_exception_via_response_code(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save checks exception code via response attribute."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Create mock exception with response but different class name
    mock_exception = Exception("Transaction cancelled")
    mock_exception.response = {
        "Error": {"Code": "TransactionCanceledException"},
        "CancellationReasons": [
            {"Code": "ConditionalCheckFailed"},
        ],
    }

    # Mock DynamoDB client to raise the exception
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items.side_effect = mock_exception

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    # Should not raise exception, should return gracefully
    processor._save(result, mock_legacy_service.id)

    # Verify DM_ETL_022 was logged
    logs = mock_logger.get_log("DM_ETL_022")
    assert len(logs) > 0, "DM_ETL_022 was not logged"
    assert logs[0]["reference"] == "DM_ETL_022"


def test_save_skips_when_state_exists(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save returns early when state record already exists."""
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

    # Mock verify_state_record_exist to return True (exists)
    processor.verify_state_record_exist = mocker.MagicMock(return_value=True)

    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    transformer.transform(mock_legacy_service, validation_issues)

    # Call _save - but first need to call through _process_service
    processor._process_service(mock_legacy_service)

    # Verify transact_write_items was NOT called since state exists
    assert mock_dynamodb_client.transact_write_items.call_count == 0

    # Verify DM_ETL_019 was logged (state exists)
    assert mock_logger.was_logged("DM_ETL_019") is True


def test_save_logs_success_on_successful_write(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _save logs DM_ETL_021 on successful transactional write."""
    processor = DataMigrationProcessor(
        config=mock_config,
        logger=mock_logger,
    )
    processor.metadata = mock_metadata_cache

    # Mock DynamoDB client
    mock_dynamodb_client = mocker.MagicMock()
    mock_dynamodb_client.transact_write_items.return_value = {}

    mocker.patch(
        "service_migration.processor.get_dynamodb_client",
        return_value=mock_dynamodb_client,
    )

    # Mock verify_state_record_exist to return False
    processor.verify_state_record_exist = mocker.MagicMock(return_value=False)

    validation_issues = []
    item_count = 4
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    processor._save(result, mock_legacy_service.id)

    # Verify DM_ETL_021 was logged with correct parameters
    assert mock_logger.was_logged("DM_ETL_021") is True
    log_entry = mock_logger.get_log("DM_ETL_021")[0]
    assert "item_count" in log_entry["detail"]
    assert (
        log_entry["detail"]["item_count"] == item_count
    )  # org, location, service, state
