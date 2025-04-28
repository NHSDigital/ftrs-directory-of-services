from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.engine import Engine

from pipeline.common import get_db_engine, get_parquet_path, get_table_name


def test_get_db_engine_creates_engine() -> None:
    """
    Test that get_db_engine creates an engine with the correct URI
    """
    engine = get_db_engine("sqlite:///:memory:")

    assert engine is not None
    assert engine.url.drivername == "sqlite"
    assert isinstance(engine, Engine)


def test_get_db_engine_returns_same_engine() -> None:
    """
    Test that get_db_engine returns the same engine for the same URI
    """
    engine1 = get_db_engine("sqlite:///:memory:")
    engine2 = get_db_engine("sqlite:///:memory:")

    assert engine1 is engine2


def test_get_db_engine_returns_different_engines() -> None:
    """
    Test that get_db_engine returns different engines for different URIs
    """
    engine1 = get_db_engine("sqlite:///:memory:")
    engine2 = get_db_engine("sqlite:///different.db")

    assert engine1 is not engine2
    assert engine1.url.drivername == "sqlite"
    assert engine2.url.drivername == "sqlite"


def test_get_table_name_without_workspace() -> None:
    """
    Test get_table_name without workspace.
    """
    result = get_table_name(entity_type="organisation", env="dev")
    assert result == "ftrs-dos-db-dev-organisation"


def test_get_table_name_with_workspace() -> None:
    """
    Test get_table_name with workspace.
    """
    result = get_table_name(entity_type="organisation", env="dev", workspace="test")
    assert result == "ftrs-dos-db-dev-organisation-test"


@pytest.mark.parametrize(
    "input_path, s3_uri, file_name, expected_result",
    [
        (
            Path("./abc/def"),
            None,
            "test1.parquet",
            Path("abc/def/test1.parquet").resolve(),
        ),
        (None, "s3://abc/def", "test2.parquet", "s3://abc/def/test2.parquet"),
    ],
)
def test_get_parquet_path_success(
    mocker: MockerFixture,
    input_path: Path,
    s3_uri: str,
    file_name: str,
    expected_result: str,
) -> None:
    """
    test that for the given inputs we get out the expected outputs
    test 1 is for input_path being provided.
    test 2 is for s3 path being provided.
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    path = get_parquet_path(input_path, s3_uri, file_name)

    assert path == expected_result


@pytest.mark.parametrize(
    "input_path, file_name, exists, is_file",
    [
        (Path("./abc/def"), "test1.parquet", True, False),
        (Path("./abc/def"), "test2.parquet", False, True),
    ],
)
def test_get_local_parquet_failures(
    mocker: MockerFixture, input_path: Path, file_name: str, exists: bool, is_file: bool
) -> None:
    """
    Test that each failure condition possible for a local parquet works as expected.
    """
    mock_exists = mocker.patch("pathlib.Path.exists", return_value=exists)
    mock_is_file = mocker.patch("pathlib.Path.is_file", return_value=is_file)

    with pytest.raises(FileNotFoundError) as excinfo:
        get_parquet_path(input_path, None, file_name)

    assert mock_exists.called
    if exists:
        assert mock_is_file.called

    file_path = input_path / file_name
    error_msg = f"File not found: {file_path}"
    assert str(excinfo.value) == error_msg
