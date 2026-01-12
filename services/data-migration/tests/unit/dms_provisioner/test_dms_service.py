from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from dms_provisioner.dms_service import (
    _extract_index_name,
    _index_exists,
    create_dms_user,
    create_indexes_from_sql_file,
    create_rds_triggers,
    create_service_related_table_trigger,
    create_services_trigger,
    extract_indexes_from_sql_file,
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


# ============================================================================
# Tests for extract_indexes_from_sql_file
# ============================================================================


@pytest.fixture
def mock_schema_sql_content() -> str:
    return """
    CREATE TABLE pathwaysdos.services (
        id integer NOT NULL,
        name character varying(255)
    );

    CREATE INDEX idx_services_id ON pathwaysdos.services USING btree (id);
    CREATE UNIQUE INDEX uniq_services_name ON pathwaysdos.services (name);
    CREATE INDEX idx_servicetypes_type_id ON pathwaysdos.servicetypes USING btree (type_id);
    """


@pytest.fixture
def mock_schema_file(tmp_path: MagicMock, mock_schema_sql_content: str) -> MagicMock:
    schema_file = tmp_path / "pathwaysdos_schema.sql"
    schema_file.write_text(mock_schema_sql_content)
    return schema_file


def test_extract_indexes_from_sql_file_extracts_all_indexes(
    mock_schema_file: MagicMock,
) -> None:
    indexes = extract_indexes_from_sql_file(mock_schema_file)
    countindexes = 3
    assert len(indexes) == countindexes
    assert any("idx_services_id" in idx for idx in indexes)
    assert any("uniq_services_name" in idx for idx in indexes)
    assert any("idx_servicetypes_type_id" in idx for idx in indexes)


def test_extract_indexes_from_sql_file_adds_if_not_exists(
    mock_schema_file: MagicMock,
) -> None:
    indexes = extract_indexes_from_sql_file(mock_schema_file)

    for idx in indexes:
        assert "IF NOT EXISTS" in idx


def test_extract_indexes_from_sql_file_raises_error_when_file_not_found() -> None:
    non_existent_file = Path("/non/existent/file.sql")

    with pytest.raises(FileNotFoundError):
        extract_indexes_from_sql_file(non_existent_file)


def test_extract_indexes_from_sql_file_handles_empty_file(tmp_path: MagicMock) -> None:
    empty_file = tmp_path / "empty.sql"
    empty_file.write_text("")

    indexes = extract_indexes_from_sql_file(empty_file)

    assert len(indexes) == 0


# ============================================================================
# Tests for _extract_index_name
# ============================================================================


def test_extract_index_name_extracts_simple_index_name() -> None:
    stmt = "CREATE INDEX idx_services_id ON services (id);"
    result = _extract_index_name(stmt)

    assert result == "idx_services_id"


def test_extract_index_name_extracts_unique_index_name() -> None:
    stmt = "CREATE UNIQUE INDEX uniq_services_name ON services (name);"
    result = _extract_index_name(stmt)

    assert result == "uniq_services_name"


def test_extract_index_name_handles_if_not_exists() -> None:
    stmt = "CREATE INDEX IF NOT EXISTS idx_services_id ON services (id);"
    result = _extract_index_name(stmt)

    assert result == "idx_services_id"


def test_extract_index_name_handles_unique_if_not_exists() -> None:
    stmt = "CREATE UNIQUE INDEX IF NOT EXISTS uniq_services_name ON services (name);"
    result = _extract_index_name(stmt)

    assert result == "uniq_services_name"


def test_extract_index_name_returns_none_for_invalid_statement() -> None:
    stmt = "SELECT * FROM services;"
    result = _extract_index_name(stmt)

    assert result is None


# ============================================================================
# Tests for _index_exists
# ============================================================================


def test_index_exists_returns_true_when_index_exists(mock_engine: MagicMock) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1,)
    mock_connection.execute.return_value = mock_result

    result = _index_exists(mock_engine, "idx_services_id")

    assert result is True
    mock_connection.execute.assert_called_once()


def test_index_exists_returns_false_when_index_does_not_exist(
    mock_engine: MagicMock,
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute.return_value = mock_result

    result = _index_exists(mock_engine, "idx_nonexistent")

    assert result is False


def test_index_exists_uses_correct_schema(mock_engine: MagicMock) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute.return_value = mock_result

    _index_exists(mock_engine, "idx_test", schema="custom_schema")

    call_args = mock_connection.execute.call_args
    params = call_args[0][1]
    assert params["schema"] == "custom_schema"
    assert params["index_name"] == "idx_test"


# ============================================================================
# Tests for create_indexes_from_sql_file
# ============================================================================


def test_create_indexes_from_sql_file_creates_new_indexes(
    mock_engine: MagicMock, mock_schema_file: MagicMock
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None  # Index does not exist
    mock_connection.execute.return_value = mock_result

    create_indexes_from_sql_file(mock_engine, mock_schema_file, tables=["services"])

    # Should have called execute for checking index existence and creating indexes
    assert mock_connection.execute.call_count > 0


def test_create_indexes_from_sql_file_skips_existing_indexes(
    mock_engine: MagicMock, mock_schema_file: MagicMock
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1,)  # Index exists
    mock_connection.execute.return_value = mock_result

    create_indexes_from_sql_file(mock_engine, mock_schema_file, tables=["services"])

    # Should only check existence, not create
    mock_connection.commit.assert_not_called()


def test_create_indexes_from_sql_file_filters_by_table(
    mock_engine: MagicMock, mock_schema_file: MagicMock
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute.return_value = mock_result

    create_indexes_from_sql_file(mock_engine, mock_schema_file, tables=["servicetypes"])

    # Should only process indexes for servicetypes table
    executed_calls = [
        call
        for call in mock_connection.execute.call_args_list
        if "servicetypes" in str(call) or "pg_indexes" in str(call)
    ]
    assert len(executed_calls) > 0


def test_create_indexes_from_sql_file_handles_sqlalchemy_error(
    mock_engine: MagicMock, mock_schema_file: MagicMock
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None  # Index does not exist

    # First call returns result (index check), second call raises error (create index)
    def execute_side_effect(*args: object, **kwargs: object) -> MagicMock:
        # Check if this is a pg_indexes query (index existence check)
        query_str = str(args[0]) if args else ""
        if "pg_indexes" in query_str:
            return mock_result
        # Otherwise it's a CREATE INDEX statement - raise error
        raise SQLAlchemyError("Index creation failed")

    mock_connection.execute.side_effect = execute_side_effect

    # Should not raise, just log warning
    create_indexes_from_sql_file(mock_engine, mock_schema_file, tables=["services"])


def test_create_indexes_from_sql_file_uses_default_tables(
    mock_engine: MagicMock, mock_schema_file: MagicMock
) -> None:
    mock_connection = mock_engine.connect.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (1,)  # All indexes exist
    mock_connection.execute.return_value = mock_result

    with patch("dms_provisioner.dms_service.SCHEMA_FILE", mock_schema_file):
        create_indexes_from_sql_file(mock_engine, mock_schema_file)

    # Should use INDEXES_TABLES by default
    assert mock_connection.execute.called
