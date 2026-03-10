from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.legacy.service import Service
from pytest_mock import MockerFixture

from common.cache import DoSMetadataCache
from service_migration.config import DataMigrationConfig
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.models import ServiceMigrationState
from service_migration.processor import DataMigrationProcessor
from service_migration.transformer.base import ServiceTransformOutput
from service_migration.transformer.contraception_pharmacy import (
    ContraceptionPharmacyTransformer,
)
from service_migration.transformer.pharmacy_blood_pressure_check import (
    PharmacyBPCheckTransformer,
)
from service_migration.validation.types import ValidationIssue, ValidationResult


@pytest.fixture()
def default_transform_output() -> ServiceTransformOutput:
    return ServiceTransformOutput(
        organisation=[],
        healthcare_service=[],
        location=[],
    )


@pytest.fixture()
def mock_transaction_builder(mocker: MockerFixture) -> MagicMock:
    mock_builder = mocker.MagicMock()
    mock_builder.add_organisation.return_value = mock_builder
    mock_builder.add_location.return_value = mock_builder
    mock_builder.add_healthcare_service.return_value = mock_builder
    mock_builder.build.return_value = [{}]
    mocker.patch(
        "service_migration.processor.ServiceTransactionBuilder",
        return_value=mock_builder,
    )
    return mock_builder


def test_migrate_parent_pharmacy_success(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    default_transform_output: ServiceTransformOutput,
    mock_transaction_builder: MagicMock,
) -> None:
    """Test that _migrate_parent_pharmacy executes a transaction and returns org/loc IDs."""
    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache

    mock_legacy_service.typeid = 13
    mock_legacy_service.odscode = "FXX99"

    org_id = uuid4()
    loc_id = uuid4()

    state_after = ServiceMigrationState.init(service_id=mock_legacy_service.id)
    state_after = state_after.model_copy(
        update={"organisation_id": org_id, "location_id": loc_id}
    )

    mock_parent_transformer = mocker.MagicMock()
    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[],
        sanitised=mock_legacy_service,
    )
    mock_parent_transformer.validator.validate.return_value = validation_result
    mock_parent_transformer.transform.return_value = default_transform_output

    mocker.patch(
        "service_migration.processor.BasePharmacyTransformer",
        return_value=mock_parent_transformer,
    )

    mock_transaction_builder.build.return_value = [{}, {}]

    processor._execute_transaction = mocker.MagicMock()
    processor.get_state_record = mocker.MagicMock(side_effect=[None, state_after])

    result_org_id, result_loc_id = processor._migrate_parent_pharmacy(
        mock_legacy_service
    )

    assert result_org_id == org_id
    assert result_loc_id == loc_id
    processor._execute_transaction.assert_called_once()


def test_migrate_parent_pharmacy_validation_fails(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that _migrate_parent_pharmacy raises ValueError when parent validation fails."""
    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache

    mock_parent_transformer = mocker.MagicMock()
    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[
            ValidationIssue(
                severity="fatal",
                code="invalid",
                diagnostics="Parent pharmacy failed validation",
            )
        ],
        sanitised=mock_legacy_service,
    )
    mock_parent_transformer.validator.validate.return_value = validation_result

    mocker.patch(
        "service_migration.processor.BasePharmacyTransformer",
        return_value=mock_parent_transformer,
    )

    with pytest.raises(ValueError, match="failed validation"):
        processor._migrate_parent_pharmacy(mock_legacy_service)


def test_migrate_parent_pharmacy_state_not_found_after_migration(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    default_transform_output: ServiceTransformOutput,
    mock_transaction_builder: MagicMock,
) -> None:
    """Test that _migrate_parent_pharmacy raises ValueError when state record is absent after writing."""
    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache

    mock_parent_transformer = mocker.MagicMock()
    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[],
        sanitised=mock_legacy_service,
    )
    mock_parent_transformer.validator.validate.return_value = validation_result
    mock_parent_transformer.transform.return_value = default_transform_output

    mocker.patch(
        "service_migration.processor.BasePharmacyTransformer",
        return_value=mock_parent_transformer,
    )

    mock_transaction_builder.build.return_value = [{}]

    processor._execute_transaction = mocker.MagicMock()
    # State is None both before and after migration
    processor.get_state_record = mocker.MagicMock(return_value=None)

    with pytest.raises(
        ValueError, match="Parent pharmacy state record not found after migration"
    ):
        processor._migrate_parent_pharmacy(mock_legacy_service)


@pytest.mark.parametrize(
    "transformer_cls,type_id,ods_code,service_name",
    [
        (PharmacyBPCheckTransformer, 148, "FXX99BPS", "BP Check: Test Service"),
        (
            ContraceptionPharmacyTransformer,
            149,
            "FXX99CON",
            "Contraception: Test Service",
        ),
    ],
)
def test_process_service_linked_pharmacy_parent_already_migrated(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    default_transform_output: ServiceTransformOutput,
    mock_transaction_builder: MagicMock,
    transformer_cls: type,
    type_id: int,
    ods_code: str,
    service_name: str,
) -> None:
    """Test that linked pharmacy services use existing org/loc IDs when parent is already in state."""
    mock_legacy_service.typeid = type_id
    mock_legacy_service.odscode = ods_code
    mock_legacy_service.name = service_name

    parent_org_id = uuid4()
    parent_loc_id = uuid4()

    mocker.patch.object(
        transformer_cls,
        "is_service_supported",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "should_include_service",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "resolve_parent",
        return_value=(None, parent_org_id, parent_loc_id),
    )

    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[],
        sanitised=mock_legacy_service,
    )
    mock_validator_cls = mocker.MagicMock()
    mock_validator_cls.return_value.validate.return_value = validation_result
    mocker.patch.object(transformer_cls, "VALIDATOR_CLS", mock_validator_cls)
    mocker.patch.object(
        transformer_cls,
        "transform",
        return_value=default_transform_output,
    )

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [transformer_cls],
    )

    mock_transaction_builder.build.return_value = [{}]

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._execute_transaction = mocker.MagicMock()
    processor._migrate_parent_pharmacy = mocker.MagicMock()
    processor.get_state_record = mocker.MagicMock(return_value=None)

    processor._process_service(mock_legacy_service)

    processor._migrate_parent_pharmacy.assert_not_called()

    assert processor.metrics.supported == 1
    assert processor.metrics.transformed == 1
    assert processor.metrics.errors == 0


@pytest.mark.parametrize(
    "transformer_cls,type_id,ods_code,service_name",
    [
        (PharmacyBPCheckTransformer, 148, "FXX99BPS", "BP Check: Test Service"),
        (
            ContraceptionPharmacyTransformer,
            149,
            "FXX99CON",
            "Contraception: Test Service",
        ),
    ],
)
def test_process_service_linked_pharmacy_parent_needs_migration(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    default_transform_output: ServiceTransformOutput,
    mock_transaction_builder: MagicMock,
    transformer_cls: type,
    type_id: int,
    ods_code: str,
    service_name: str,
) -> None:
    """Test that linked pharmacy services run parent migration when parent has no state record."""
    mock_legacy_service.typeid = type_id
    mock_legacy_service.odscode = ods_code
    mock_legacy_service.name = service_name

    parent_service = mocker.MagicMock(spec=Service)
    parent_org_id = uuid4()
    parent_loc_id = uuid4()

    mocker.patch.object(
        transformer_cls,
        "is_service_supported",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "should_include_service",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "resolve_parent",
        return_value=(parent_service, None, None),
    )
    mocker.patch.object(
        transformer_cls,
        "transform",
        return_value=default_transform_output,
    )

    validation_result = ValidationResult(
        origin_record_id=mock_legacy_service.id,
        issues=[],
        sanitised=mock_legacy_service,
    )
    mock_validator_cls = mocker.MagicMock()
    mock_validator_cls.return_value.validate.return_value = validation_result
    mocker.patch.object(transformer_cls, "VALIDATOR_CLS", mock_validator_cls)

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [transformer_cls],
    )

    mock_transaction_builder.build.return_value = [{}]

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._execute_transaction = mocker.MagicMock()
    processor._migrate_parent_pharmacy = mocker.MagicMock(
        return_value=(parent_org_id, parent_loc_id)
    )
    processor.get_state_record = mocker.MagicMock(return_value=None)

    processor._process_service(mock_legacy_service)

    processor._migrate_parent_pharmacy.assert_called_once_with(parent_service)

    assert processor.metrics.supported == 1
    assert processor.metrics.transformed == 1
    assert processor.metrics.errors == 0


@pytest.mark.parametrize(
    "transformer_cls,type_id,ods_code,service_name",
    [
        (PharmacyBPCheckTransformer, 148, "FXX99BPS", "BP Check: Test Service"),
        (
            ContraceptionPharmacyTransformer,
            149,
            "FXX99CON",
            "Contraception: Test Service",
        ),
    ],
)
def test_process_service_linked_pharmacy_parent_not_found(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    transformer_cls: type,
    type_id: int,
    ods_code: str,
    service_name: str,
) -> None:
    """Test that linked pharmacy services increment errors and stop when parent pharmacy is not found."""
    mock_legacy_service.typeid = type_id
    mock_legacy_service.odscode = ods_code
    mock_legacy_service.name = service_name

    mocker.patch.object(
        transformer_cls,
        "is_service_supported",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "should_include_service",
        return_value=(True, None),
    )
    mocker.patch.object(
        transformer_cls,
        "resolve_parent",
        side_effect=ParentPharmacyNotFoundError(
            record_id=mock_legacy_service.id, ods_code="FXX99"
        ),
    )

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [transformer_cls],
    )

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()

    processor._process_service(mock_legacy_service)

    assert processor.metrics.supported == 1
    assert processor.metrics.errors == 1
    assert processor.metrics.transformed == 0


def test_setup_linked_transformer_parent_migration_exception(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that DM_ETL_039 is logged and processing stops when parent migration raises."""
    mock_legacy_service.typeid = 149
    mock_legacy_service.odscode = "FXX99CON"
    mock_legacy_service.name = "Contraception: Test Service"

    parent_service = mocker.MagicMock(spec=Service)
    parent_service.id = 2

    mocker.patch.object(
        ContraceptionPharmacyTransformer,
        "is_service_supported",
        return_value=(True, None),
    )
    mocker.patch.object(
        ContraceptionPharmacyTransformer,
        "resolve_parent",
        return_value=(parent_service, None, None),
    )

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [ContraceptionPharmacyTransformer],
    )

    # Make BasePharmacyTransformer validation fail so _migrate_parent_pharmacy raises ValueError
    fatal_issue = ValidationIssue(
        severity="fatal",
        code="INVALID",
        diagnostics="Parent pharmacy failed validation",
    )
    parent_validation_result = ValidationResult(
        origin_record_id=parent_service.id,
        issues=[fatal_issue],
        sanitised=parent_service,
    )
    mock_parent_transformer = mocker.MagicMock()
    mock_parent_transformer.validator.validate.return_value = parent_validation_result
    mocker.patch(
        "service_migration.processor.BasePharmacyTransformer",
        return_value=mock_parent_transformer,
    )

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._execute_transaction = mocker.MagicMock()
    processor.get_state_record = mocker.MagicMock(return_value=None)

    processor._process_service(mock_legacy_service)

    assert processor.metrics.total == 1
    assert processor.metrics.supported == 1
    assert processor.metrics.errors == 1
    assert processor.metrics.transformed == 0

    logs = mock_logger.get_log("DM_ETL_039")
    assert len(logs) == 1
    assert logs[0]["detail"]["parent_record_id"] == parent_service.id
    assert logs[0]["detail"]["record_id"] == mock_legacy_service.id


def test_setup_linked_transformer_org_loc_id_none(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that DM_ETL_040 is logged and processing stops when org/loc IDs are None after resolve."""
    mock_legacy_service.typeid = 149
    mock_legacy_service.odscode = "FXX99CON"
    mock_legacy_service.name = "Contraception: Test Service"

    mocker.patch.object(
        ContraceptionPharmacyTransformer,
        "is_service_supported",
        return_value=(True, None),
    )
    # resolve_parent returns no parent service and no IDs — an unexpected incomplete state
    mocker.patch.object(
        ContraceptionPharmacyTransformer,
        "resolve_parent",
        return_value=(None, None, None),
    )

    mocker.patch(
        "service_migration.processor.SUPPORTED_TRANSFORMERS",
        [ContraceptionPharmacyTransformer],
    )

    processor = DataMigrationProcessor(config=mock_config, logger=mock_logger)
    processor.metadata = mock_metadata_cache
    processor.logger.append_keys = mocker.MagicMock()
    processor.logger.remove_keys = mocker.MagicMock()
    processor._execute_transaction = mocker.MagicMock()
    processor.get_state_record = mocker.MagicMock(return_value=None)

    processor._process_service(mock_legacy_service)

    assert processor.metrics.total == 1
    assert processor.metrics.supported == 1
    assert processor.metrics.errors == 1
    assert processor.metrics.transformed == 0

    logs = mock_logger.get_log("DM_ETL_040")
    assert len(logs) == 1
    assert logs[0]["detail"]["record_id"] == mock_legacy_service.id
