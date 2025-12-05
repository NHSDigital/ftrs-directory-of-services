from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from dms_provisioner.dms_service import (
    create_dms_user,
    create_rds_triggers,
    create_service_related_table_trigger,
    create_services_trigger,
)


@pytest.fixture
def mock_engine() -> MagicMock:
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    return mock_engine


@pytest.fixture
def mock_services_template() -> str:
    return """
    DROP TRIGGER IF EXISTS services_lambda_notify ON pathwaysdos.services;
    DROP FUNCTION IF EXISTS pathwaysdos.services_change_notify() CASCADE;

    CREATE OR REPLACE FUNCTION pathwaysdos.services_change_notify()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        PERFORM aws_lambda.invoke(
            '{{ lambda_arn }}',
            json_build_object('table_name', TG_TABLE_NAME, 'method', TG_OP),
            '{{ aws_region }}',
            'Event'
        );
        RETURN NULL;
    END;
    $function$;

    CREATE TRIGGER services_lambda_notify_insert
    AFTER INSERT ON pathwaysdos.services
    REFERENCING NEW TABLE AS new_rows
    FOR EACH STATEMENT
    EXECUTE FUNCTION pathwaysdos.services_change_notify();
    """


@pytest.fixture
def mock_related_template() -> str:
    return """
    DROP TRIGGER IF EXISTS {{ table_name }}_lambda_notify ON pathwaysdos.{{ table_name }};
    DROP FUNCTION IF EXISTS pathwaysdos.related_service_change_notify() CASCADE;

    CREATE OR REPLACE FUNCTION pathwaysdos.related_service_change_notify()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
        PERFORM aws_lambda.invoke(
            '{{ lambda_arn }}',
            json_build_object('table_name', TG_TABLE_NAME, 'method', TG_OP),
            '{{ aws_region }}',
            'Event'
        );
        RETURN NULL;
    END;
    $function$;
    """


def test_dms_user_creation_succeeds_when_all_parameters_are_correct(
    mock_engine: MagicMock,
) -> None:
    username = "dms_user"
    password = "secure_password"

    create_dms_user(mock_engine, username, password)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


def test_dms_user_creation_propagates_exception_when_database_error_occurs(
    mock_engine: MagicMock,
) -> None:
    username = "dms_user"
    password = "secure_password"

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.side_effect = SQLAlchemyError("Database connection failed")

    with pytest.raises(SQLAlchemyError):
        create_dms_user(mock_engine, username, password)


def test_dms_user_creation_handles_special_characters_in_password(
    mock_engine: MagicMock,
) -> None:
    username = "dms_user"
    password = "p@$$w0rd'with\"quotes"

    create_dms_user(mock_engine, username, password)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.assert_called_once()


def test_services_trigger_creation_succeeds_when_template_exists(
    mock_engine: MagicMock, mock_services_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    with patch(
        "dms_provisioner.dms_service.Path.read_text",
        return_value=mock_services_template,
    ):
        create_services_trigger(mock_engine, lambda_arn, aws_region)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


def test_services_trigger_creation_propagates_exception_when_database_error_occurs(
    mock_engine: MagicMock, mock_services_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.side_effect = SQLAlchemyError("Trigger creation failed")

    with patch(
        "dms_provisioner.dms_service.Path.read_text",
        return_value=mock_services_template,
    ):
        with pytest.raises(SQLAlchemyError):
            create_services_trigger(mock_engine, lambda_arn, aws_region)


def test_services_trigger_creation_propagates_exception_when_template_file_not_found(
    mock_engine: MagicMock,
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    with patch(
        "dms_provisioner.dms_service.Path.read_text",
        side_effect=FileNotFoundError("Template file not found"),
    ):
        with pytest.raises(FileNotFoundError):
            create_services_trigger(mock_engine, lambda_arn, aws_region)


def test_services_trigger_creation_handles_all_parameter_substitutions(
    mock_engine: MagicMock, mock_services_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    with patch(
        "dms_provisioner.dms_service.Path.read_text",
        return_value=mock_services_template,
    ):
        create_services_trigger(mock_engine, lambda_arn, aws_region)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    executed_sql = mock_connection.execute.call_args[0][0].text

    assert "{{" not in executed_sql
    assert "}}" not in executed_sql
    assert lambda_arn in executed_sql
    assert aws_region in executed_sql


def test_service_related_table_trigger_creation_succeeds(
    mock_engine: MagicMock, mock_related_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"
    table_name = "serviceendpoints"

    with patch(
        "dms_provisioner.dms_service.Path.read_text", return_value=mock_related_template
    ):
        create_service_related_table_trigger(
            mock_engine, lambda_arn, aws_region, table_name
        )

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


def test_service_related_table_trigger_handles_parameter_substitutions(
    mock_engine: MagicMock, mock_related_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"
    table_name = "serviceendpoints"

    with patch(
        "dms_provisioner.dms_service.Path.read_text", return_value=mock_related_template
    ):
        create_service_related_table_trigger(
            mock_engine, lambda_arn, aws_region, table_name
        )

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    executed_sql = mock_connection.execute.call_args[0][0].text

    assert "{{" not in executed_sql
    assert "}}" not in executed_sql
    assert lambda_arn in executed_sql
    assert aws_region in executed_sql


def test_create_rds_triggers_creates_all_triggers(
    mock_engine: MagicMock, mock_services_template: str, mock_related_template: str
) -> None:
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    with patch("dms_provisioner.dms_service.Path.read_text") as mock_read:
        mock_read.side_effect = [mock_services_template, mock_related_template]
        create_rds_triggers(mock_engine, lambda_arn, aws_region)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    call_count = 2
    assert mock_connection.execute.call_count == call_count
    assert mock_connection.commit.call_count == call_count
