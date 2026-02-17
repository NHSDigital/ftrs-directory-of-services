import os
from typing import Generator

import httpx
import pytest

from ftrs_test_util.server_utils import run_server
from ftrs_test_util.settings import TestSettings


def _get_client_for_existing_crud_api(settings: TestSettings) -> httpx.Client:
    if not settings.crud_api_endpoint:
        pytest.fail(
            "CRUD_API_ENDPOINT must be provided when USE_EXISTING_CRUD_API is True"
        )

    session = httpx.Client(
        base_url=settings.crud_api_endpoint,
        timeout=5,
        headers={
            "NHSE-Product-ID": "crud-integration-tests",
            "Content-Type": "application/fhir+json",
        },
        follow_redirects=True,
    )
    return session


@pytest.fixture(scope="function")
def ingest_api_client(dynamodb_endpoint: str) -> Generator[httpx.Client, None, None]:
    """Fixture for an instance of the Organisation CRUD API"""

    settings = TestSettings()
    if settings.use_existing_crud_api:
        yield _get_client_for_existing_crud_api(settings)
        return

    # Store original env vars to restore later
    original_endpoint = os.environ.get("ENDPOINT_URL")
    original_environment = os.environ.get("ENVIRONMENT")
    original_workspace = os.environ.get("WORKSPACE")

    # Reset cached settings to ensure fresh configuration with new endpoint
    # reset_settings()

    # Set environment variables to match TestSettings so table names are consistent
    os.environ["ENDPOINT_URL"] = dynamodb_endpoint
    os.environ["ENVIRONMENT"] = settings.environment
    if settings.workspace is not None:
        os.environ["WORKSPACE"] = settings.workspace
    elif "WORKSPACE" in os.environ:
        del os.environ["WORKSPACE"]

    from dos_ingest.app import app  # noqa: F401 PLC0415

    with run_server(app) as base_url:
        session = httpx.Client(
            base_url=base_url,
            timeout=5,
            headers={
                "NHSE-Product-ID": "crud-integration-tests",
                # TODO: These shouldn't be required by the API - if not provided they should be assumed
                "Accept": "application/fhir+json",
                "Content-Type": "application/fhir+json",
            },
            follow_redirects=True,
        )

        yield session
        session.close()

    # Restore original environment variables
    if original_endpoint is not None:
        os.environ["ENDPOINT_URL"] = original_endpoint
    elif "ENDPOINT_URL" in os.environ:
        del os.environ["ENDPOINT_URL"]

    if original_environment is not None:
        os.environ["ENVIRONMENT"] = original_environment
    elif "ENVIRONMENT" in os.environ:
        del os.environ["ENVIRONMENT"]

    if original_workspace is not None:
        os.environ["WORKSPACE"] = original_workspace
    elif "WORKSPACE" in os.environ:
        del os.environ["WORKSPACE"]

    # Reset settings again after test to clean up cached state
    # reset_settings()
