from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest.mock import patch

import pytest
from ftrs_common.logger import Logger
from ftrs_common.mocks.mock_logger import MockLogger

# from pipeline.utils.dos_db import (
#     QUERY_GP_ENDPOINTS,
#     QUERY_GP_PRACTICE,
#     QUERY_GP_SERVICEDAYOPENINGTIMES,
#     QUERY_GP_SERVICESPECIFIEDOPENINGTIMES,
#     QUERY_SERVICEENDPOINTS_COLUMNS,
#     QUERY_SERVICES_COLUMNS,
#     QUERY_SERVICES_SIZE,
# )
# from tests.util.stub_data import (
#     mock_gp_endpoints_df,
#     mock_gp_practices_df,
#     mock_service_endpoint_columns_df,
#     mock_service_opening_times_df,
#     mock_service_specified_opening_times_df,
#     mock_services_columns_df,
#     mock_services_size_df,
# )


# class StubData:
#     def __init__(self) -> None:
#         super().__init__()
#         self._store = {}
#         self.reset()

#     def reset(self) -> None:
#         self._store = {
#             QUERY_GP_PRACTICE: mock_gp_practices_df.copy(),
#             QUERY_GP_ENDPOINTS: mock_gp_endpoints_df.copy(),
#             QUERY_SERVICES_SIZE: mock_services_size_df.copy(),
#             QUERY_SERVICES_COLUMNS: mock_services_columns_df.copy(),
#             QUERY_SERVICEENDPOINTS_COLUMNS: mock_service_endpoint_columns_df.copy(),
#             QUERY_GP_SERVICEDAYOPENINGTIMES: mock_service_opening_times_df.copy(),
#             QUERY_GP_SERVICESPECIFIEDOPENINGTIMES: mock_service_specified_opening_times_df.copy(),
#         }

#     def set_query_result(self, query: str, result: pd.DataFrame) -> None:
#         """
#         Set the result for a specific query.
#         """
#         if query not in self._store:
#             error_msg = f"Query '{query}' not found in stub data."
#             raise ValueError(error_msg)

#         self._store[query] = result.copy()

#     def __getitem__(self, query: str) -> pd.DataFrame:
#         """
#         Get the result for a specific query.
#         """
#         if query in self._store:
#             return self._store[query].copy()

#         err_msg = f"Query '{query}' not found in stub data."
#         raise KeyError(err_msg)


# @pytest.fixture()
# def mock_sql_data() -> Generator[Mock, None, None]:
#     """
#     Simulate the DoS database connection.
#     """
#     data_stub = StubData()

#     with patch("pipeline.utils.dos_db.pd.read_sql") as mock_read_sql:
#         mock_read_sql.side_effect = lambda query, conn: data_stub[query]
#         yield mock_read_sql


@pytest.fixture()
def mock_tmp_directory() -> Generator[Path, None, None]:
    """
    Mock the temporary directory creation to avoid actual file system changes.
    """
    with TemporaryDirectory() as tmpdir:
        mock_tmpdir = Path(tmpdir)
        mock_tmpdir.mkdir(parents=True, exist_ok=True)
        yield mock_tmpdir


@pytest.fixture()
def mock_logger() -> Generator[MockLogger, None, None]:
    """
    Mock the logger to avoid actual logging.
    """
    mock_logger = MockLogger()

    with patch.object(Logger, "get", return_value=mock_logger):
        yield mock_logger
