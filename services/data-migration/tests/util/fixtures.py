from typing import Generator
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from pipeline.db_utils import (
    QUERY_GP_ENDPOINTS,
    QUERY_GP_PRACTICE,
    QUERY_SERVICEENDPOINTS_COLUMNS,
    QUERY_SERVICES_COLUMNS,
    QUERY_SERVICES_SIZE,
)
from tests.util.stub_data import (
    mock_gp_endpoints_df,
    mock_gp_practices_df,
    mock_service_endpoint_columns_df,
    mock_services_columns_df,
    mock_services_size_df,
)


class StubData:
    def __init__(self) -> None:
        super().__init__()
        self._store = {}
        self.reset()

    def reset(self) -> None:
        self._store = {
            QUERY_GP_PRACTICE: mock_gp_practices_df.copy(),
            QUERY_GP_ENDPOINTS: mock_gp_endpoints_df.copy(),
            QUERY_SERVICES_SIZE: mock_services_size_df.copy(),
            QUERY_SERVICES_COLUMNS: mock_services_columns_df.copy(),
            QUERY_SERVICEENDPOINTS_COLUMNS: mock_service_endpoint_columns_df.copy(),
        }

    def set_query_result(self, query: str, result: pd.DataFrame) -> None:
        """
        Set the result for a specific query.
        """
        if query not in self._store:
            error_msg = f"Query '{query}' not found in stub data."
            raise ValueError(error_msg)

        self._store[query] = result.copy()

    def __getitem__(self, query: str) -> pd.DataFrame:
        """
        Get the result for a specific query.
        """
        if query in self._store:
            return self._store[query].copy()

        err_msg = f"Query '{query}' not found in stub data."
        raise KeyError(err_msg)


@pytest.fixture()
def mock_sql_data() -> Generator[Mock, None, None]:
    """
    Simulate the DoS database connection.
    """
    data_stub = StubData()

    with patch("pipeline.db_utils.pd.read_sql") as mock_read_sql:
        mock_read_sql.side_effect = lambda query, conn: data_stub[query]
        yield mock_read_sql


@pytest.fixture()
def mock_pd_to_parquet(mocker: MockerFixture) -> Generator[Mock, None, None]:
    """
    Mock the pd.to_parquet function to avoid writing to disk.
    """
    yield mocker.patch("pandas.DataFrame.to_parquet")


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
