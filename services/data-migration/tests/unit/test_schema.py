import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import create_mock_engine

from pipeline.schema import _drop_schema, _load_schema_file, load_schema, main


def test_load_schema_file() -> None:
    """
    Test that _load_schema_file returns text contents of the file path
    """
    test_content = "I am a test schema file"

    with NamedTemporaryFile(mode="w") as f:
        f.write(test_content)
        f.seek(0)
        assert _load_schema_file(f.name) == test_content


def test_load_schema_file_is_directory() -> None:
    """
    Test that _load_schema_file raises a ValueError when the path is a directory
    """
    with TemporaryDirectory() as test_dir:
        # Ensure the path is a directory
        assert pathlib.Path(test_dir).is_dir()

        with pytest.raises(ValueError) as exc:
            _load_schema_file(test_dir)

        expected_err_msg = f"Schema file not found: {pathlib.Path(test_dir).resolve()}"
        assert str(exc.value) == expected_err_msg


def test_load_schema_file_not_found() -> None:
    """
    Test that _load_schema_file raises a ValueError when the path does not exist
    """
    with TemporaryDirectory() as test_dir:
        # Ensure the path is a directory
        assert pathlib.Path(test_dir).is_dir()

        test_file = pathlib.Path(test_dir) / "test_file.txt"

        with pytest.raises(ValueError) as exc:
            _load_schema_file(test_file)

        expected_err_msg = f"Schema file not found: {test_file.resolve()}"
        assert str(exc.value) == expected_err_msg


def test_drop_schema(mocker: MockerFixture) -> None:
    """
    Test that _drop_schema drops the schema from the database
    """
    mock_input = mocker.patch("pipeline.schema.input", return_value="yes")

    mock_conn = mocker.MagicMock()
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None

    _drop_schema(mock_conn, "test_schema")

    mock_input.assert_called_once_with("Type 'yes' to continue: ")

    assert mock_conn.execute.called is True
    assert mock_conn.execute.call_args[0][0].text == 'DROP SCHEMA "test_schema" CASCADE'
    assert mock_conn.commit.called is True


def test_drop_schema_bypass_input(mocker: MockerFixture) -> None:
    """
    Test that _drop_schema drops the schema from the database without asking for user input
    """
    mock_input = mocker.patch("pipeline.schema.input")

    mock_conn = mocker.MagicMock()
    mock_conn.execute.return_value = None
    mock_conn.commit.return_value = None

    _drop_schema(mock_conn, "test_schema", bypass_input=True)

    mock_input.assert_not_called()

    assert mock_conn.execute.called is True
    assert mock_conn.execute.call_args[0][0].text == 'DROP SCHEMA "test_schema" CASCADE'
    assert mock_conn.commit.called is True


def test_drop_schema_not_yes(mocker: MockerFixture) -> None:
    """
    Test that _drop_schema raises a SystemExit when user input is not 'yes'
    """
    mock_input = mocker.patch("pipeline.schema.input", return_value="no")
    mock_conn = mocker.MagicMock()

    with pytest.raises(SystemExit) as exc:
        _drop_schema(mock_conn, "test_schema")

    assert exc.value.code == 1
    mock_input.assert_called_once_with("Type 'yes' to continue: ")


def test_load_schema(mocker: MockerFixture) -> None:
    """
    Test that load_schema loads the schema from a file and executes it in the database
    """
    mock_conn = mocker.MagicMock()

    mock_engine = create_mock_engine(
        "postgresql://test_user:test_password@test_host/test_db",
        lambda *args, **kwargs: None,
    )
    mock_engine.connect = mocker.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    mock_get_db_engine = mocker.patch("pipeline.schema.get_db_engine")
    mock_get_db_engine.return_value = mock_engine

    with NamedTemporaryFile(mode="w") as f:
        f.write("I am a test schema file")
        f.seek(0)

        load_schema(f.name, "postgresql://test_user:test_password@test_host/test_db")

    mock_get_db_engine.assert_called_once_with(
        "postgresql://test_user:test_password@test_host/test_db"
    )
    mock_engine.connect.assert_called_once()

    assert mock_conn.execute.called is True
    assert mock_conn.execute.call_count == 1
    assert mock_conn.execute.call_args[0][0].text == "I am a test schema file"
    assert mock_conn.commit.called is True
    assert mock_conn.commit.call_count == 1


def test_load_schema_drop(mocker: MockerFixture) -> None:
    """
    Test that load_schema drops the schema before loading the new schema
    """
    mock_conn = mocker.MagicMock()

    mock_engine = create_mock_engine(
        "postgresql://test_user:test_password@test_host/test_db",
        lambda *args, **kwargs: None,
    )
    mock_engine.connect = mocker.MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    mock_get_db_engine = mocker.patch("pipeline.schema.get_db_engine")
    mock_get_db_engine.return_value = mock_engine

    mock_input = mocker.patch("pipeline.schema.input", return_value="yes")

    with NamedTemporaryFile(mode="w") as f:
        f.write("I am a test schema file")
        f.seek(0)

        load_schema(
            f.name, "postgresql://test_user:test_password@test_host/test_db", drop=True
        )

    mock_get_db_engine.assert_called_once_with(
        "postgresql://test_user:test_password@test_host/test_db"
    )
    mock_engine.connect.assert_called_once()

    expected_call_count = 2

    assert mock_conn.execute.called is True
    assert mock_conn.execute.call_count == expected_call_count
    assert mock_input.called is True

    # First execute call is for dropping the schema
    assert (
        mock_conn.execute.call_args_list[0][0][0].text == 'DROP SCHEMA "Core" CASCADE'
    )

    # Second execute call is for loading the new schema
    assert mock_conn.execute.call_args_list[1][0][0].text == "I am a test schema file"

    assert mock_conn.commit.called is True
    assert mock_conn.commit.call_count == expected_call_count


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls load_schema with the correct arguments
    """
    load_schema_mock = mocker.patch("pipeline.schema.load_schema")
    args = [
        "--schema-path",
        "test_schema.sql",
        "--db-uri",
        "postgresql://test_user:test_password@test_host/test_db",
        "--drop",
        "--drop-schema-name",
        "test_schema",
    ]

    main(args)

    assert load_schema_mock.called is True
    assert load_schema_mock.call_args[0][0] == "test_schema.sql"
    assert (
        load_schema_mock.call_args[0][1]
        == "postgresql://test_user:test_password@test_host/test_db"
    )
    assert load_schema_mock.call_args[0][2] is True
    assert load_schema_mock.call_args[0][3] == "test_schema"


def test_main_throws_error_on_no_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when no arguments are provided
    """
    expected_exit_code = 2

    load_schema_mock = mocker.patch("pipeline.schema.load_schema")
    args = [""]

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_schema_mock.called is False


def test_main_throws_error_on_missing_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when required arguments are missing
    """
    expected_exit_code = 2

    load_schema_mock = mocker.patch("pipeline.schema.load_schema")
    args = ["--db-uri", "postgresql://test_user:test_password@test_host/test_db"]

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_schema_mock.called is False


def test_main_throws_error_on_invalid_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when invalid arguments are provided
    """
    expected_exit_code = 2

    load_schema_mock = mocker.patch("pipeline.schema.load_schema")
    args = [
        "--schema-path",
        "test_schema.sql",
        "--db-uri",
        "postgresql://test_user:test_password@test_host/test_db",
        "--invalid-arg",
    ]

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_schema_mock.called is False
