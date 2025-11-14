from decimal import Decimal

import pytest
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    Disposition,
    Endpoint,
    HealthcareService,
    Location,
    Organisation,
    PositionGCS,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
    Telecom,
)
from ftrs_data_layer.domain.legacy.service import (
    Service,
)
from pytest_mock import MockerFixture
from sqlalchemy import Engine

from pipeline.processor import (
    DataMigrationMetrics,
    DataMigrationProcessor,
    ServiceTransformOutput,
)
from pipeline.utils import dbutil
from pipeline.utils.cache import DoSMetadataCache
from pipeline.utils.config import DataMigrationConfig
from pipeline.validation.types import ValidationIssue, ValidationResult


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

    mocker.patch("pipeline.processor.Session", return_value=mock_session)

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

    mocker.patch("pipeline.processor.Session", return_value=mock_session)

    record_id = 1
    method = "test_method"

    assert processor.sync_service(record_id, method) is None

    assert processor._process_service.call_count == 1
    # processor._process_service.assert_called_once_with(mock_legacy_service)

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

    mocker.patch("pipeline.processor.Session", return_value=mock_session)

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
                sg=SymptomGroup(
                    id="2b52f7e2-c0ab-5e00-8d7d-75ede400fe7c",
                    source="pathways",
                    codeType="Symptom Group (SG)",
                    codeID=1035,
                    codeValue="Breathing Problems, Breathlessness or Wheeze, Pregnant",
                ),
                sd=SymptomDiscriminator(
                    id="300af504-ba5d-5973-a877-a0789c6863ab",
                    source="pathways",
                    codeType="Symptom Discriminator (SD)",
                    codeID=4003,
                    codeValue="PC full Primary Care assessment and prescribing capability",
                    synonyms=[],
                ),
            ),
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id="39ce1220-2586-5b2e-a35d-3021b2e0337c",
                    source="servicefinder",
                    codeType="Symptom Group (SG)",
                    codeID=360,
                    codeValue="z2.0 - Service Types",
                ),
                sd=SymptomDiscriminator(
                    id="6ce70d41-9337-578d-a662-d9fe25016d40",
                    source="servicefinder",
                    codeType="Symptom Discriminator (SD)",
                    codeID=14023,
                    codeValue="GP Practice",
                    synonyms=["General Practice"],
                ),
            ),
        ],
        dispositions=[
            Disposition(
                id="4443b15a-26a3-517f-8a93-eb7c2539d4fc",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=126,
                codeValue="Contact Own GP Practice next working day for appointment",
                time=7200,
            ),
            Disposition(
                id="ae7a129f-cda2-51f6-aff6-88a94f7f36de",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=10,
                codeValue="Speak to a Primary Care Service within 2 hours",
                time=120,
            ),
        ],
    )

    assert len(output.location) == 1
    assert output.location[0] == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        active=True,
        address=Address(
            line1="123 Main St",
            line2=None,
            county=None,
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
    mocker.patch("pipeline.processor.SUPPORTED_TRANSFORMERS", [mock_transformer])

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

    with pytest.raises(Exception, match="Test error"):
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

    mocker.patch("pipeline.processor.SUPPORTED_TRANSFORMERS", [mock_transformer])

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

    mocker.patch("pipeline.processor.SUPPORTED_TRANSFORMERS", [mock_transformer])

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

    mock_org_repo = mocker.MagicMock()
    mock_location_repo = mocker.MagicMock()
    mock_service_repo = mocker.MagicMock()

    dbutil.REPOSITORY_CACHE = {
        "ftrs-dos-test-database-organisation-test_workspace": mock_org_repo,
        "ftrs-dos-test-database-healthcare-service-test_workspace": mock_service_repo,
        "ftrs-dos-test-database-location-test_workspace": mock_location_repo,
    }
    validation_issues = []
    transformer = processor.get_transformer(mock_legacy_service)
    result = transformer.transform(mock_legacy_service, validation_issues)

    processor._save(result)

    assert mock_org_repo.upsert.call_count == 1
    mock_org_repo.upsert.assert_called_once_with(result.organisation[0])

    assert mock_location_repo.upsert.call_count == 1
    mock_location_repo.upsert.assert_called_once_with(result.location[0])

    assert mock_service_repo.upsert.call_count == 1
    mock_service_repo.upsert.assert_called_once_with(result.healthcare_service[0])
