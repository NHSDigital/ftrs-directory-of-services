from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest.mock import patch

import pytest
from ftrs_common.logger import Logger
from ftrs_common.mocks.mock_logger import MockLogger


@pytest.fixture()
def mock_logger() -> Generator[MockLogger, None, None]:
    """
    Mock the logger to avoid actual logging.
    """
    mock_logger = MockLogger()

    with patch.object(Logger, "get", return_value=mock_logger):
        yield mock_logger
