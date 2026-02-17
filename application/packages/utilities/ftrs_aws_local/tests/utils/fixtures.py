from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture()
def mock_logging(mocker: MockerFixture) -> Generator[Mock, None, None]:
    """
    Mock the logging module to avoid actual logging.
    """
    mock_log = Mock()

    mocker.patch("logging.debug", side_effect=mock_log.debug)
    mocker.patch("logging.info", side_effect=mock_log.info)
    mocker.patch("logging.warning", side_effect=mock_log.warning)
    mocker.patch("logging.error", side_effect=mock_log.error)
    mocker.patch("logging.critical", side_effect=mock_log.critical)
    mocker.patch("logging.exception", side_effect=mock_log.exception)

    yield mock_log


@pytest.fixture()
def mock_tmp_directory() -> Generator[Path, None, None]:
    """
    Mock the temporary directory creation to avoid actual file system changes.
    """
    with TemporaryDirectory() as tmpdir:
        mock_tmpdir = Path(tmpdir)
        mock_tmpdir.mkdir(parents=True, exist_ok=True)
        yield mock_tmpdir
