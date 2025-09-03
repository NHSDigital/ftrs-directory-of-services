from typing import NoReturn
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.domain.triage_code import TriageCode
from ftrs_data_layer.logbase import DataMigrationLogBase

from pipeline.transformer.triage_code import TriageCodeTransformer
from pipeline.triagecode_processor import TriageCodeProcessor
from pipeline.utils.config import DataMigrationConfig


@pytest.fixture(autouse=True)
def processor() -> TriageCodeProcessor:
    config = Mock(spec=DataMigrationConfig)
    # Create a nested mock for db_config
    config.db_config = Mock()
    config.db_config.connection_string = "sqlite://"

    logger = Mock()
    processor = TriageCodeProcessor(config, logger)
    processor.metadata = Mock()
    processor._save_to_dynamoDB = Mock()
    return processor


@patch("pipeline.triagecode_processor.iter_records")
@patch.object(TriageCodeTransformer, "build_triage_code_from_symptom_group")
@patch.object(TriageCodeTransformer, "build_triage_code_from_disposition")
@patch.object(TriageCodeTransformer, "build_triage_code_from_symptom_discriminator")
def test_sync_all_triage_codes_processes_all_record_types(
    mock_transform_discriminator: Mock,
    mock_transform_disposition: Mock,
    mock_transform_group: Mock,
    mock_iter_records: Mock,
    processor: TriageCodeProcessor,
) -> NoReturn:
    mock_symptom_group = Mock(spec=legacy.SymptomGroup, id=1)
    mock_disposition = Mock(spec=legacy.Disposition, id=2)
    mock_symptom_discriminator = Mock(spec=legacy.SymptomDiscriminator, id=3)

    mock_iter_records.side_effect = lambda engine, model: [
        mock_symptom_group
        if model == legacy.SymptomGroup
        else mock_disposition
        if model == legacy.Disposition
        else mock_symptom_discriminator
    ]

    processor.sync_all_triage_codes()

    mock_iter_records.assert_has_calls(
        [
            call(processor.engine, legacy.SymptomGroup),
            call(processor.engine, legacy.Disposition),
            call(processor.engine, legacy.SymptomDiscriminator),
        ]
    )
    mock_transform_group.assert_called_once_with(mock_symptom_group)
    mock_transform_disposition.assert_called_once_with(mock_disposition)
    mock_transform_discriminator.assert_called_once_with(mock_symptom_discriminator)


def test_process_record_logs_input_record(processor: TriageCodeProcessor) -> NoReturn:
    record = Mock()
    record.id = 1
    record.model_dump.return_value = {"id": 1, "name": "test"}
    transformer_method = Mock(return_value=Mock(spec=TriageCode))

    processor._process_record(record, "TestType", transformer_method)

    processor.logger.append_keys.assert_called_with(record_id=1)
    processor.logger.log.assert_any_call(
        DataMigrationLogBase.DM_ETL_001, record={"id": 1, "name": "test"}
    )


def test_process_record_transforms_and_saves_record(
    processor: TriageCodeProcessor,
) -> NoReturn:
    record = Mock()
    record.id = 1
    record.model_dump.return_value = {"id": 1}

    triage_code = Mock(spec=TriageCode)
    triage_code.model_dump.return_value = {"code": "TEST", "type": "TestType"}
    transformer_method = Mock(return_value=triage_code)

    processor._process_record(record, "TestType", transformer_method)

    transformer_method.assert_called_once_with(record)
    processor._save_to_dynamoDB.assert_called_once_with(triage_code)


def test_process_record_logs_transformation_details(
    processor: TriageCodeProcessor,
) -> NoReturn:
    record = Mock()
    record.id = 1
    record.model_dump.return_value = {"id": 1}

    triage_code = Mock(spec=TriageCode)
    triage_code.model_dump.return_value = {"code": "TEST"}
    transformer_method = Mock(return_value=triage_code)

    processor._process_record(record, "TestType", transformer_method)

    processor.logger.log.assert_any_call(
        DataMigrationLogBase.DM_ETL_006,
        transformer_name="TestTypeTransformer",
        original_record={"id": 1},
        transformed_record={"code": "TEST"},
    )


def test_process_record_logs_metrics(processor: TriageCodeProcessor) -> NoReturn:
    record = Mock()
    record.id = 1
    record.model_dump.return_value = {"id": 1}

    triage_code = Mock(spec=TriageCode)
    triage_code.model_dump.return_value = {"code": "TEST"}
    transformer_method = Mock(return_value=triage_code)

    processor._process_record(record, "TestType", transformer_method)

    # Verify that performance metrics were logged
    log_calls = processor.logger.log.call_args_list
    performance_log_call = [
        call for call in log_calls if call[0][0] == DataMigrationLogBase.DM_ETL_007
    ]
    assert len(performance_log_call) > 0

    # Verify the call contains the expected parameters
    call_args = performance_log_call[0][1]
    assert "elapsed_time" in call_args
    assert call_args["transformer_name"] == "TestTypeTransformer"


def test_process_record_handles_exceptions(processor: TriageCodeProcessor) -> NoReturn:
    record = Mock()
    record.id = 1
    record.model_dump.return_value = {"id": 1}

    transformer_method = Mock(side_effect=Exception("Test error"))

    processor._process_record(record, "TestType", transformer_method)

    processor.logger.exception.assert_called_once()
    processor.logger.log.assert_any_call(
        DataMigrationLogBase.DM_ETL_008, error="Test error"
    )
    assert processor.metrics.errors == 1


@patch("pipeline.triagecode_processor.get_repository")
def test_save_to_dynamoDB_calls_upsert(
    mock_get_repository: Mock, processor: TriageCodeProcessor
) -> NoReturn:
    mock_repo = Mock()
    mock_get_repository.return_value = mock_repo
    triage_code = Mock(spec=TriageCode)

    # Don't replace the mock, just call the original method directly
    TriageCodeProcessor._save_to_dynamoDB(processor, triage_code)

    mock_get_repository.assert_called_once_with(
        processor.config, "triage-code", TriageCode, processor.logger
    )
    mock_repo.upsert.assert_called_once_with(triage_code)


def test_process_combinations_success(
    mocker: Mock, processor: TriageCodeProcessor
) -> NoReturn:
    """
    Test successful execution of _process_combinations.
    """
    mock_symptom_group_ids = [1, 2]
    mock_symptom_discriminators = [MagicMock(), MagicMock()]
    mock_triage_code = MagicMock()

    mocker.patch(
        "pipeline.triagecode_processor.get_all_symptom_groups",
        return_value=mock_symptom_group_ids,
    )
    mocker.patch(
        "pipeline.triagecode_processor.get_symptom_discriminators_for_symptom_group",
        return_value=mock_symptom_discriminators,
    )
    mocker.patch(
        "pipeline.triagecode_processor.TriageCodeTransformer.build_triage_code_combinations",
        return_value=mock_triage_code,
    )
    mocker.patch.object(processor, "_save_to_dynamoDB")

    processor._process_combinations()

    assert processor._save_to_dynamoDB.call_count == len(mock_symptom_group_ids)


def test_process_combinations_no_discriminators(
    mocker: Mock, processor: TriageCodeProcessor
) -> NoReturn:
    """
    Test processing when no symptom discriminators are found for a symptom group.
    """
    mock_symptom_group_ids = [1]
    mocker.patch(
        "pipeline.triagecode_processor.get_all_symptom_groups",
        return_value=mock_symptom_group_ids,
    )
    mocker.patch(
        "pipeline.triagecode_processor.get_symptom_discriminators_for_symptom_group",
        return_value=[],
    )

    processor._process_combinations()

    processor.logger.log.assert_called_once_with(
        DataMigrationLogBase.DM_ETL_012, sg_id=1
    )


def test_process_combinations_error_in_discriminator_fetch(
    mocker: Mock, processor: TriageCodeProcessor
) -> NoReturn:
    """
    Test handling of exceptions when fetching discriminators for a symptom group.
    """
    mock_symptom_group_ids = [1]
    mocker.patch(
        "pipeline.triagecode_processor.get_all_symptom_groups",
        return_value=mock_symptom_group_ids,
    )
    mocker.patch(
        "pipeline.triagecode_processor.get_symptom_discriminators_for_symptom_group",
        side_effect=Exception("Error fetching discriminators"),
    )
    processor._process_combinations()
    processor.logger.exception.assert_called_once()
    processor.logger.log.assert_called_once_with(
        DataMigrationLogBase.DM_ETL_008,
        error="Error fetching discriminators",
    )


def test_process_combinations_engine_error(
    mocker: Mock, processor: TriageCodeProcessor
) -> NoReturn:
    """
    Test handling of exceptions when fetching symptom groups.
    """
    mocker.patch(
        "pipeline.triagecode_processor.get_all_symptom_groups",
        side_effect=Exception("Database connection failed"),
    )

    processor._process_combinations()

    processor.logger.exception.assert_called_once()
    processor.logger.log.assert_called_once_with(
        DataMigrationLogBase.DM_ETL_008,
        error="Database connection failed",
    )
