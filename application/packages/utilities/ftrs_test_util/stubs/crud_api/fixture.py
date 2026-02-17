import pytest
from ftrs_test_util.stubs.crud_api.mock_app import app
from typing import Generator
from ftrs_test_util.server_utils import run_server


@pytest.fixture(scope="session")
def crud_api_stub() -> Generator[str, None, None]:
    """Fixture for CRUD API stub server."""
    with run_server(app) as base_url:
        yield base_url
