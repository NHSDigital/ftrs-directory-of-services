import json
from pathlib import Path
from uuid import uuid4

from freezegun import freeze_time
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from pydantic import SecretStr
from pytest_mock import MockerFixture
from typer import Typer
from typer.testing import CliRunner

from pipeline.application import DMSEvent
from pipeline.cli import patch_local_save_method, typer_app
from pipeline.processor import ServiceTransformOutput
from pipeline.utils.config import (
    DatabaseConfig,
    DataMigrationConfig,
)
from queue_populator.config import QueuePopulatorConfig

runner = CliRunner()


def test_typer_app_init() -> None:
    """
    Test the initialization of the Typer app.
    """
    expected_command_count = 4

    assert isinstance(typer_app, Typer)
    assert typer_app.info.name == "dos-etl"
    assert typer_app.info.help == "DoS Data Migration Pipeline CLI"
    assert len(typer_app.registered_commands) == expected_command_count


def test_local_handler_full_sync(mocker: MockerFixture) -> None:
    """
    Test the local_handler function for full sync.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_full_sync_event = mocker.Mock()

    result = runner.invoke(
        typer_app,
        [
            "migrate",
            "--db-uri",
            "postgresql://username:password@localhost:5432/dbname",
            "--env",
            "test",
            "--workspace",
            "test_workspace",
            "--ddb-endpoint-url",
            "http://localhost:8000",
        ],
    )

    assert result.exit_code == 0

    mock_app.assert_called_once_with(
        config=DataMigrationConfig(
            db_config=DatabaseConfig.from_uri(
                "postgresql://username:password@localhost:5432/dbname"
            ),
            ENVIRONMENT="test",
            WORKSPACE="test_workspace",
            ENDPOINT_URL="http://localhost:8000",
        )
    )

    mock_app.return_value.handle_full_sync_event.assert_called_once_with()


def test_local_handler_single_sync(mocker: MockerFixture) -> None:
    """
    Test the local_handler function for single sync.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_dms_event = mocker.Mock()

    result = runner.invoke(
        typer_app,
        [
            "migrate",
            "--db-uri",
            "postgresql://username:password@localhost:5432/dbname",
            "--env",
            "test",
            "--service-id",
            "12345",
        ],
    )

    assert result.exit_code == 0

    mock_app.assert_called_once_with(
        config=DataMigrationConfig(
            db_config=DatabaseConfig.from_uri(
                "postgresql://username:password@localhost:5432/dbname"
            ),
            ENVIRONMENT="test",
            WORKSPACE=None,
            ENDPOINT_URL=None,
        )
    )

    mock_app.return_value.handle_dms_event.assert_called_once_with(
        DMSEvent(
            type="dms_event",
            record_id=12345,
            method="insert",
            table_name="services",
        )
    )


def test_local_handler_output_dir(mocker: MockerFixture) -> None:
    """
    Test the local_handler function with output directory for dry run.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_full_sync_event = mocker.Mock()

    mock_open = mocker.patch("pipeline.cli.open", mocker.mock_open())

    result = runner.invoke(
        typer_app,
        [
            "migrate",
            "--db-uri",
            "postgresql://username:password@localhost:5432/dbname",
            "--env",
            "test",
            "--output-dir",
            "/tmp/output",
        ],
    )

    assert result.exit_code == 0

    mock_app.assert_called_once_with(
        config=DataMigrationConfig(
            db_config=DatabaseConfig.from_uri(
                "postgresql://username:password@localhost:5432/dbname"
            ),
            ENVIRONMENT="test",
            WORKSPACE=None,
            ENDPOINT_URL=None,
        )
    )
    mock_app.return_value.handle_full_sync_event.assert_called_once_with()

    expected_file_count = 3
    assert mock_open.call_count == expected_file_count

    mock_open.assert_has_calls(
        [
            mocker.call(Path("/tmp/output/organisation.jsonl"), "w"),
            mocker.call(Path("/tmp/output/location.jsonl"), "w"),
            mocker.call(Path("/tmp/output/healthcare-service.jsonl"), "w"),
        ]
    )


@freeze_time("2025-07-15T12:00:00")
def test_patch_local_save_method(mocker: MockerFixture) -> None:
    """
    Test the patch_local_save_method function.
    """
    mock_app = mocker.Mock()
    output_dir = Path("/tmp/output")
    org_path = output_dir / "organisation.jsonl"
    loc_path = output_dir / "location.jsonl"
    hc_path = output_dir / "healthcare-service.jsonl"

    mock_output = ServiceTransformOutput(
        organisation=[Organisation.model_construct(id=uuid4())],
        location=[Location.model_construct(id=uuid4())],
        healthcare_service=[HealthcareService.model_construct(id=uuid4())],
    )

    with patch_local_save_method(mock_app, output_dir):
        assert hasattr(mock_app.processor, "_save")
        assert callable(mock_app.processor._save)

        mock_app.processor._save(mock_output)

    # Check if files were created
    assert org_path.exists()
    assert loc_path.exists()
    assert hc_path.exists()

    # Check if the content was written correctly
    org_content = json.loads(org_path.read_text().strip())
    loc_content = json.loads(loc_path.read_text().strip())
    hc_content = json.loads(hc_path.read_text().strip())

    assert org_content == {
        "id": str(mock_output.organisation[0].id),
        "identifier_ODS_ODSCode": None,
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-07-15T12:00:00Z",
        "endpoints": [],
        "telecom": None,
    }
    assert loc_content == {
        "id": str(mock_output.location[0].id),
        "name": None,
        "partOf": None,
        "positionGCS": None,
        "positionReferenceNumber_UBRN": None,
        "positionReferenceNumber_UPRN": None,
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-07-15T12:00:00Z",
    }
    assert hc_content == {
        "id": str(mock_output.healthcare_service[0].id),
        "identifier_oldDoS_uid": None,
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "migrationNotes": None,
        "modifiedDateTime": "2025-07-15T12:00:00Z",
        "ageEligibilityCriteria": None,
    }

    # Clean up created files
    org_path.unlink()
    loc_path.unlink()
    hc_path.unlink()


def test_populate_queue_handler(
    mocker: MockerFixture,
) -> None:
    """
    Test the populate_queue_handler function.
    """
    mock_populate = mocker.patch("pipeline.cli.populate_sqs_queue")

    result = runner.invoke(
        typer_app,
        [
            "populate-queue",
            "--db-uri",
            "postgresql://username:password@localhost:5432/dbname",
            "--sqs-queue-url",
            "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
            "--type-id",
            "1",
            "--type-id",
            "2",
            "--status-id",
            "3",
            "--status-id",
            "4",
        ],
    )

    assert result.exit_code == 0

    mock_populate.assert_called_once_with(
        QueuePopulatorConfig(
            db_config=DatabaseConfig(
                host="localhost",
                port=5432,
                username="username",
                password=SecretStr("password"),
                dbname="dbname",
            ),
            SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
            type_ids=[1, 2],
            status_ids=[3, 4],
        )
    )


def test_populate_queue_handler_no_ids(
    mocker: MockerFixture,
) -> None:
    """
    Test the populate_queue_handler function without type ids or status ids.
    """
    mock_populate = mocker.patch("pipeline.cli.populate_sqs_queue")

    result = runner.invoke(
        typer_app,
        [
            "populate-queue",
            "--db-uri",
            "postgresql://username:password@localhost:5432/dbname",
            "--sqs-queue-url",
            "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
        ],
    )

    assert result.exit_code == 0

    mock_populate.assert_called_once_with(
        QueuePopulatorConfig(
            db_config=DatabaseConfig(
                host="localhost",
                port=5432,
                username="username",
                password=SecretStr("password"),
                dbname="dbname",
            ),
            SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/123456789012/my-queue",
            type_ids=None,
            status_ids=None,
        )
    )


def test_export_to_s3_handler(mocker: MockerFixture) -> None:
    """
    Test that the export_to_s3_handler calls run_s3_export
    """
    mock_s3_export = mocker.patch("pipeline.cli.run_s3_export")

    result = runner.invoke(
        typer_app,
        ["export-to-s3", "--env", "dev", "--workspace", "fdos-000"],
    )

    assert result.exit_code == 0
    mock_s3_export.assert_called_once_with("dev", "fdos-000")


def test_restore_from_s3_handler(mocker: MockerFixture) -> None:
    """
    Test that the restore_from_s3_handler calls run_s3_restore
    """
    mock_s3_restore = mocker.patch("pipeline.cli.run_s3_restore")

    result = runner.invoke(
        typer_app,
        ["restore-from-s3", "--env", "dev", "--workspace", "fdos-000"],
    )

    assert result.exit_code == 0
    mock_s3_restore.assert_called_once_with("dev", "fdos-000")
