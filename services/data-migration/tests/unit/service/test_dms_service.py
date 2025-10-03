from unittest.mock import MagicMock, mock_open, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from pipeline.service.dms_service import create_dms_user, create_rds_trigger_replica_db


@pytest.fixture
def mock_engine() -> MagicMock:
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection
    return mock_engine


@pytest.fixture
def mock_file_open() -> MagicMock:
    sql_template = """
    CREATE OR REPLACE FUNCTION public.notify_lambda_function()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    BEGIN
    PERFORM aws_lambda.invoke(
        '${lambda_arn}',
        json_build_object('source', 'postgres', 'table', TG_TABLE_NAME, 'type', TG_OP)::text,
            '${aws_region}' );
    RETURN NEW;
    END;
    $function$;

    DROP TRIGGER IF EXISTS ${table_name}_changes_trigger ON ${table_name};

    CREATE TRIGGER ${table_name}_changes_trigger
        AFTER INSERT OR UPDATE OR DELETE ON ${table_name}
        FOR EACH ROW
        EXECUTE FUNCTION public.notify_lambda_function();

    GRANT EXECUTE ON FUNCTION public.notify_lambda_function() TO ${user};
    """

    m = mock_open(read_data=sql_template)
    with patch("builtins.open", m):
        yield m


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


def test_rds_trigger_creation_succeeds_when_template_exists(
    mock_engine: MagicMock, mock_file_open: MagicMock
) -> None:
    username = "dms_user"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    create_rds_trigger_replica_db(mock_engine, username, lambda_arn, aws_region)

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


def test_rds_trigger_creation_propagates_exception_when_database_error_occurs(
    mock_engine: MagicMock, mock_file_open: MagicMock
) -> None:
    username = "dms_user"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_connection.execute.side_effect = SQLAlchemyError("Trigger creation failed")

    with pytest.raises(SQLAlchemyError):
        create_rds_trigger_replica_db(mock_engine, username, lambda_arn, aws_region)


def test_rds_trigger_creation_propagates_exception_when_template_file_not_found(
    mock_engine: MagicMock,
) -> None:
    with patch(
        "pathlib.Path.open", side_effect=FileNotFoundError("Template file not found")
    ):
        username = "dms_user"
        lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
        aws_region = "eu-west-2"

        with pytest.raises(FileNotFoundError):
            create_rds_trigger_replica_db(mock_engine, username, lambda_arn, aws_region)


def test_rds_trigger_creation_handles_all_parameter_substitutions(
    mock_engine: MagicMock, mock_file_open: MagicMock
) -> None:
    username = "dms_user"
    lambda_arn = "arn:aws:lambda:eu-west-2:123456789012:function:my-function"
    aws_region = "eu-west-2"

    with patch("ftrs_data_layer.domain.legacy.Service.__tablename__", "services"):
        create_rds_trigger_replica_db(mock_engine, username, lambda_arn, aws_region)

        mock_connection = mock_engine.connect.return_value.__enter__.return_value
        executed_sql = mock_connection.execute.call_args[0][0].text

        assert "${user}" not in executed_sql
        assert "${lambda_arn}" not in executed_sql
        assert "${aws_region}" not in executed_sql
        assert "${table_name}" not in executed_sql
        assert username in executed_sql
        assert lambda_arn in executed_sql
        assert aws_region in executed_sql
        assert "services" in executed_sql
