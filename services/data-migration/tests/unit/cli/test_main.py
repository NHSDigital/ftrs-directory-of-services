<<<<<<< HEAD
=======
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
from pydantic import SecretStr
from pytest_mock import MockerFixture
from typer import Typer
from typer.testing import CliRunner

from cli.main import typer_app
from common.config import DatabaseConfig
from queue_populator.config import QueuePopulatorConfig
<<<<<<< HEAD
from service_migration.config import ServiceMigrationConfig
=======
from service_migration.config import DataMigrationConfig
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))

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


def test_local_handler_single_sync(mocker: MockerFixture) -> None:
    """
    Test the local_handler function for single sync.
    """
    mock_app = mocker.patch("cli.main.ServiceMigrationApplication")
    mock_app.return_value.handle_sqs_event = mocker.Mock()

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
        config=ServiceMigrationConfig(
            db_config=DatabaseConfig.from_uri(
                "postgresql://username:password@localhost:5432/dbname"
            ),
            ENVIRONMENT="test",
            WORKSPACE=None,
            ENDPOINT_URL=None,
        )
    )

    mock_app.return_value.handle_sqs_event.assert_called_once()

    call_args = mock_app.return_value.handle_sqs_event.call_args[0][0]

<<<<<<< HEAD
    assert call_args == {
        "Records": [
            {
                "body": '{"record_id":12345,"service_id":12345,"table_name":"services","method":"insert"}',
                "messageId": "service-12345",
            },
        ],
=======
    assert call_args.message_id == "service-12345"
    assert call_args.json_body == {
        "method": "insert",
        "record_id": 12345,
        "service_id": 12345,
        "table_name": "services",
        "type": "dms_event",
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
    }


def test_populate_queue_handler(
    mocker: MockerFixture,
) -> None:
    """
    Test the populate_queue_handler function.
    """
    mock_populate = mocker.patch("cli.main.populate_sqs_queue")

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
            service_id=None,
            record_id=None,
            full_sync=True,
            table_name="services",
        )
    )


def test_populate_queue_handler_no_ids(
    mocker: MockerFixture,
) -> None:
    """
    Test the populate_queue_handler function without type ids or status ids.
    """
    mock_populate = mocker.patch("cli.main.populate_sqs_queue")

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
            service_id=None,
            record_id=None,
            full_sync=True,
            table_name="services",
        )
    )


def test_export_to_s3_handler(mocker: MockerFixture) -> None:
    """
    Test that the export_to_s3_handler calls run_s3_export
    """
    mock_s3_export = mocker.patch("cli.main.run_s3_export")

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
    mock_s3_restore = mocker.patch("cli.main.run_s3_restore")

    result = runner.invoke(
        typer_app,
        ["restore-from-s3", "--env", "dev", "--workspace", "fdos-000"],
    )

    assert result.exit_code == 0
    mock_s3_restore.assert_called_once_with("dev", "fdos-000")
