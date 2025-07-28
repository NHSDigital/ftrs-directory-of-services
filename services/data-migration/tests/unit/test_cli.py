import json
from pathlib import Path
from uuid import uuid4

from freezegun import freeze_time
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from pytest_mock import MockerFixture
from typer import Typer
from typer.testing import CliRunner

from pipeline.cli import patch_local_save_method, typer_app
from pipeline.processor import ServiceTransformOutput
from pipeline.utils.config import DatabaseConfig, DataMigrationConfig

runner = CliRunner()


def test_typer_app_init() -> None:
    """
    Test the initialization of the Typer app.
    """
    expected_command_count = 1

    assert isinstance(typer_app, Typer)
    assert typer_app.info.name == "dos-etl"
    assert typer_app.info.help == "DoS Data Migration Pipeline CLI"
    assert len(typer_app.registered_commands) == expected_command_count


def test_local_handler_full_sync(mocker: MockerFixture) -> None:
    """
    Test the local_handler function for full sync.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_event = mocker.Mock()

    result = runner.invoke(
        typer_app,
        [
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

    mock_app.return_value.handle_event.assert_called_once_with({"type": "full_sync"})


def test_local_handler_single_sync(mocker: MockerFixture) -> None:
    """
    Test the local_handler function for single sync.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_event = mocker.Mock()

    result = runner.invoke(
        typer_app,
        [
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

    mock_app.return_value.handle_event.assert_called_once_with(
        {
            "type": "dms_event",
            "record_id": "12345",
            "method": "insert",
            "table_name": "services",
        }
    )


def test_local_handler_output_dir(mocker: MockerFixture) -> None:
    """
    Test the local_handler function with output directory for dry run.
    """
    mock_app = mocker.patch("pipeline.cli.DataMigrationApplication")
    mock_app.return_value.handle_event = mocker.Mock()

    mock_open = mocker.patch("pipeline.cli.open", mocker.mock_open())

    result = runner.invoke(
        typer_app,
        [
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
    mock_app.return_value.handle_event.assert_called_once_with({"type": "full_sync"})

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
        organisation=Organisation.model_construct(id=uuid4()),
        location=Location.model_construct(id=uuid4()),
        healthcare_service=HealthcareService.model_construct(id=uuid4()),
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
        "id": str(mock_output.organisation.id),
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-07-15T12:00:00Z",
        "endpoints": [],
    }
    assert loc_content == {
        "id": str(mock_output.location.id),
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-07-15T12:00:00Z",
    }
    assert hc_content == {
        "id": str(mock_output.healthcare_service.id),
        "createdBy": "SYSTEM",
        "createdDateTime": "2025-07-15T12:00:00Z",
        "modifiedBy": "SYSTEM",
        "modifiedDateTime": "2025-07-15T12:00:00Z",
    }

    # Clean up created files
    org_path.unlink()
    loc_path.unlink()
    hc_path.unlink()
