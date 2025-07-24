from unittest.mock import patch
from uuid import UUID

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.legacy_model import Service, ServiceStatusEnum, ServiceType
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pytest_mock import MockerFixture
from sqlmodel import Session

from pipeline.processor import DataMigrationProcessor
from pipeline.transformer.gp_practice import GPPracticeTransformer


@patch("pipeline.processor.uuid4", return_value="test-uuid")
def test_processor_init(mock_logger: MockLogger) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    assert processor.env == "test"
    assert processor.workspace == "test_workspace"
    assert processor.dry_run is True

    log_keys = processor.logger.get_current_keys()

    assert log_keys["run_id"] == "test-uuid"
    assert log_keys["service"] == "data-migration"
    assert log_keys["env"] == "test"
    assert log_keys["workspace"] == "test_workspace"
    assert log_keys["dry_run"] is True


def test_processor_get_repository() -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    repository = processor.get_repository(
        entity_type="organisation",
        model_cls=Organisation,
    )

    assert repository is not None
    assert isinstance(repository, AttributeLevelRepository)
    assert repository.table.name == "ftrs-dos-test-database-organisation-test_workspace"

    assert processor._repository_cache[repository.table.name] is repository
    assert (
        processor.get_repository(
            entity_type="organisation",
            model_cls=Organisation,
        )
        is repository
    )


def test_processor_get_repository_no_workspace() -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace=None,
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    repository = processor.get_repository(
        entity_type="organisation",
        model_cls=Organisation,
    )

    assert repository is not None
    assert isinstance(repository, AttributeLevelRepository)
    assert repository.table.name == "ftrs-dos-test-database-organisation"

    assert processor._repository_cache[repository.table.name] is repository
    assert (
        processor.get_repository(
            entity_type="organisation",
            model_cls=Organisation,
        )
        is repository
    )


def test_processor_is_full_sync() -> None:
    assert DataMigrationProcessor.is_full_sync({}) is True


def test_full_service_sync(
    mock_logger: MockLogger, mocker: MockerFixture, mock_service: Service
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    processor._iter_records = mocker.MagicMock(return_value=iter([mock_service]))
    processor.run_full_service_sync({}, {})

    assert processor._iter_records.call_count == 1
    assert mock_logger.get_log("DM_ETL_000") == [
        {
            "detail": {"mode": "full_sync"},
            "msg": "Starting Data Migration ETL Pipeline in mode: full_sync",
            "reference": "DM_ETL_000",
        }
    ]

    assert mock_logger.get_log("DM_ETL_999") == [
        {
            "detail": {
                "metrics": {
                    "errors": 0,
                    "migrated_records": 0,
                    "skipped_records": 0,
                    "supported_records": 1,
                    "total_records": 1,
                    "transformed_records": 1,
                    "unsupported_records": 0,
                },
                "mode": "full_sync",
            },
            "msg": "Data Migration ETL Pipeline completed successfully.",
            "reference": "DM_ETL_999",
        }
    ]


def test_run_single_service_sync(
    mock_service: Service,
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    with patch.object(Session, "get") as mock_get:
        mock_get.return_value = mock_service
        processor.run_single_service_sync({"record_id": "test-id"})

    mock_get.assert_called_once_with(Service, "test-id")

    assert mock_logger.get_log("DM_ETL_000") == [
        {
            "detail": {"mode": "single_service_sync"},
            "msg": "Starting Data Migration ETL Pipeline in mode: single_service_sync",
            "reference": "DM_ETL_000",
        }
    ]
    assert mock_logger.get_log("DM_ETL_999") == [
        {
            "detail": {
                "metrics": {
                    "errors": 0,
                    "migrated_records": 0,
                    "skipped_records": 0,
                    "supported_records": 1,
                    "total_records": 1,
                    "transformed_records": 1,
                    "unsupported_records": 0,
                },
                "mode": "single_service_sync",
            },
            "msg": "Data Migration ETL Pipeline completed successfully.",
            "reference": "DM_ETL_999",
        }
    ]


def test_run_single_service_sync_no_record_id(
    mock_logger: MockLogger,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    with pytest.raises(ValueError, match="No record_id provided in the event"):
        processor.run_single_service_sync({})


def test_run_single_service_sync_record_not_found(
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    with patch.object(Session, "get") as mock_get:
        mock_get.return_value = None
        with pytest.raises(ValueError, match="Service with ID test-id not found"):
            processor.run_single_service_sync({"record_id": "test-id"})


def test_process_service(
    mock_service: Service,
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    mock_logger.append_keys = mocker.MagicMock()
    mock_logger.remove_keys = mocker.MagicMock()

    processor._process_service(mock_service)

    mock_logger.append_keys.assert_called_once_with(record_id=mock_service.id)
    mock_logger.remove_keys.assert_called_once_with(["record_id"])

    assert mock_logger.was_logged("DM_ETL_001") is True
    assert mock_logger.was_logged("DM_ETL_004") is False

    assert mock_logger.get_log("DM_ETL_006") == [
        {
            "reference": "DM_ETL_006",
            "msg": "Record 123456 successfully migrated",
            "detail": {
                "record_id": 123456,
                "transformer_name": "GPPracticeTransformer",
                "healthcare_service_id": UUID("39ff9286-3313-5970-ba22-0ab84c58c5ad"),
                "organisation_id": UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e"),
                "location_id": UUID("65f34381-acc8-5315-9b81-ff4e4dbef8d2"),
            },
        }
    ]


def test_process_record_no_transformer(
    mock_service: Service,
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    mock_service.typeid = 1000  # Simulate no transformer available
    mock_service.type = ServiceType(id=1000, name="Unknown Service Type")

    processor._process_service(mock_service)

    assert mock_logger.was_logged("DM_ETL_001") is True
    assert mock_logger.was_logged("DM_ETL_004") is True

    assert mock_logger.get_log("DM_ETL_004") == [
        {
            "reference": "DM_ETL_004",
            "msg": "Record 123456 was not migrated due to reason: No suitable transformer found",
            "detail": {
                "record_id": mock_service.id,
                "reason": "No suitable transformer found",
            },
        }
    ]

    assert processor.metrics.model_dump() == {
        "errors": 0,
        "migrated_records": 0,
        "skipped_records": 0,
        "supported_records": 0,
        "total_records": 1,
        "transformed_records": 0,
        "unsupported_records": 1,
    }


def test_process_record_skipped_record(
    mock_service: Service,
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    mock_service.id = 123456
    mock_service.statusid = ServiceStatusEnum.CLOSED

    processor._process_service(mock_service)

    assert mock_logger.was_logged("DM_ETL_001") is True
    assert mock_logger.was_logged("DM_ETL_004") is True

    assert mock_logger.get_log("DM_ETL_004") == [
        {
            "reference": "DM_ETL_004",
            "msg": "Record 123456 was not migrated due to reason: Transformer indicated to skip this record - Service is not active",
            "detail": {
                "record_id": mock_service.id,
                "reason": "Transformer indicated to skip this record - Service is not active",
            },
        }
    ]


def test_process_service_unexpected_error(
    mock_service: Service,
    mock_logger: MockLogger,
) -> None:
    processor = DataMigrationProcessor(
        db_uri="sqlite:///:memory:",
        env="test",
        workspace="test_workspace",
        dynamodb_endpoint="http://localhost:8000",
        dry_run=True,
    )

    with patch.object(GPPracticeTransformer, "transform") as mock_transform:
        mock_transform.side_effect = Exception("Unexpected error")
        processor._process_service(mock_service)

    assert mock_logger.was_logged("DM_ETL_001") is True
    assert mock_logger.was_logged("DM_ETL_007") is True

    assert mock_logger.get_log("DM_ETL_007") == [
        {
            "reference": "DM_ETL_007",
            "msg": "Error processing record 123456: Unexpected error",
            "detail": {"record_id": mock_service.id, "error": "Unexpected error"},
        }
    ]
