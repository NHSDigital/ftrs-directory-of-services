"""
Smoke Test Configuration and Fixtures

Provides shared configuration and fixtures for smoke tests across environments.
"""

import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    """
    Base URL for the dos-search API endpoint.

    Override with SMOKE_TEST_BASE_URL environment variable.
    Default is local development endpoint.
    """
    return os.getenv("SMOKE_TEST_BASE_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def api_key():
    """
    API key for authenticated requests (if required in environment).

    Override with SMOKE_TEST_API_KEY environment variable.
    """
    return os.getenv("SMOKE_TEST_API_KEY", None)


@pytest.fixture(scope="session")
def valid_ods_code():
    """
    A known valid ODS code that exists in the target environment.

    Override with SMOKE_TEST_VALID_ODS_CODE environment variable.
    """
    return os.getenv("SMOKE_TEST_VALID_ODS_CODE", "ABC123")


@pytest.fixture(scope="session")
def invalid_ods_code():
    """
    A known invalid ODS code format for testing validation.

    Override with SMOKE_TEST_INVALID_ODS_CODE environment variable.
    """
    return os.getenv("SMOKE_TEST_INVALID_ODS_CODE", "INVALID!")


@pytest.fixture(scope="session")
def nonexistent_ods_code():
    """
    A valid format ODS code that doesn't exist in the database.

    Override with SMOKE_TEST_NONEXISTENT_ODS_CODE environment variable.
    """
    return os.getenv("SMOKE_TEST_NONEXISTENT_ODS_CODE", "NOEXIST99")


@pytest.fixture(scope="session")
def timeout():
    """
    Request timeout in seconds for smoke tests.

    Override with SMOKE_TEST_TIMEOUT environment variable.
    """
    return int(os.getenv("SMOKE_TEST_TIMEOUT", "10"))


@pytest.fixture(scope="session")
def headers(api_key):
    """
    Default headers for API requests.
    """
    headers = {
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    return headers


@pytest.fixture(scope="session")
def environment():
    """
    Target environment for smoke tests.

    Override with SMOKE_TEST_ENVIRONMENT environment variable.
    Options: local, dev, test, int, prod
    """
    return os.getenv("SMOKE_TEST_ENVIRONMENT", "local")


@pytest.fixture(scope="session")
def skip_destructive_tests(environment):
    """
    Flag to skip destructive tests in production environments.
    """
    return environment == "prod"
