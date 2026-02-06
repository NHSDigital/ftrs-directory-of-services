"""ETL ODS fixtures for local testing with testcontainers.

This module provides pytest fixtures specifically for testing the ETL ODS
pipeline locally using LocalStack and mock servers.
"""

import os
from typing import Any, Generator

import pytest
from loguru import logger
from utilities.testcontainers.fixtures import is_local_test_mode

try:
    from utilities.local_servers.ods_mock_server import run_ods_mock_server, stop_server
except ImportError:  # pragma: no cover
    run_ods_mock_server = None  # type: ignore[assignment]
    stop_server = None  # type: ignore[assignment]

try:
    from utilities.local.etl_ods_invoker import ETLOdsPipelineInvoker
except ImportError:  # pragma: no cover
    ETLOdsPipelineInvoker = None  # type: ignore[assignment]

try:
    from utilities.test_keys import get_test_private_key
except ImportError:  # pragma: no cover
    get_test_private_key = None  # type: ignore[assignment]


@pytest.fixture(scope="session")
def local_ods_mock_server(
    aws_test_environment: dict,
) -> Generator[dict[str, Any], None, None]:
    """ODS Terminology API mock server.

    Starts a local FastAPI server that mocks the NHS ODS Terminology API.
    Returns different FHIR Bundle responses based on the date parameter.

    Args:
        aws_test_environment: Test environment fixture

    Yields:
        Dict with mock server information
    """
    if not is_local_test_mode():
        yield {"mode": "aws", "base_url": None, "process": None}
        return

    if run_ods_mock_server is None or stop_server is None:
        pytest.skip("ods_mock_server utilities are not available")

    port = 8003
    host = "127.0.0.1"

    try:
        process = run_ods_mock_server(port=port, host=host)
        base_url = f"http://{host}:{port}"
        logger.info(f"ODS mock server started at {base_url}")

        yield {
            "mode": "local",
            "base_url": base_url,
            "ods_api_url": f"{base_url}/fhir/Organization",
            "process": process,
        }
    except Exception as e:
        logger.error(f"Failed to start ODS mock server: {e}")
        yield {"mode": "error", "base_url": None, "process": None, "error": str(e)}
        return
    finally:
        if "process" in locals() and process:
            stop_server(process)
            logger.info("ODS mock server stopped")


@pytest.fixture(scope="session")
def etl_ods_pipeline_invoker(
    aws_test_environment: dict,
    local_ods_mock_server: dict,
    local_crud_apis_server: dict,
) -> Generator[Any, None, None]:
    """ETL ODS pipeline invoker for local testing.

    Provides an invoker that can run the complete ETL ODS pipeline
    locally by invoking Lambda handlers directly.

    Args:
        aws_test_environment: Test environment fixture
        local_ods_mock_server: ODS mock server fixture
        local_crud_apis_server: CRUD APIs server fixture

    Yields:
        ETLOdsPipelineInvoker instance or None
    """
    if not is_local_test_mode():
        yield None
        return

    if ETLOdsPipelineInvoker is None:
        pytest.skip("ETLOdsPipelineInvoker is not available")

    endpoint_url = aws_test_environment.get("endpoint_url")
    ods_mock_url = (
        local_ods_mock_server.get("ods_api_url")
        or "http://127.0.0.1:8003/fhir/Organization"
    )
    apim_url = local_crud_apis_server.get("base_url") or "http://127.0.0.1:8001"

    if not endpoint_url:
        logger.warning("No endpoint_url available for ETL ODS pipeline invoker")
        yield None
        return

    invoker = ETLOdsPipelineInvoker(
        endpoint_url=endpoint_url,
        ods_mock_url=ods_mock_url,
        apim_url=apim_url,
    )

    yield invoker


@pytest.fixture
def etl_ods_test_environment(
    aws_test_environment: dict,
    local_ods_mock_server: dict,
    local_crud_apis_server: dict,
) -> Generator[dict[str, str], None, None]:
    """Set up complete environment for ETL ODS local tests.

    This fixture configures all environment variables needed for
    running ETL ODS handlers locally.

    Args:
        aws_test_environment: Test environment fixture
        local_ods_mock_server: ODS mock server fixture
        local_crud_apis_server: CRUD APIs server fixture

    Yields:
        Dict with environment configuration
    """
    if not is_local_test_mode():
        yield {}
        return

    if get_test_private_key is None:
        pytest.skip("Test key utilities are not available")

    endpoint_url = aws_test_environment.get("endpoint_url") or "http://localhost:4566"
    ods_mock_url = (
        local_ods_mock_server.get("ods_api_url")
        or "http://127.0.0.1:8003/fhir/Organization"
    )
    apim_url = local_crud_apis_server.get("base_url") or "http://127.0.0.1:8001"

    # RSA private key for JWT signing (generated at runtime for testing)
    test_private_key = get_test_private_key()

    env_vars = {
        # AWS configuration
        "AWS_REGION": "eu-west-2",
        "AWS_DEFAULT_REGION": "eu-west-2",
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_ENDPOINT_URL": endpoint_url,
        "ENDPOINT_URL": endpoint_url,
        # Application configuration
        "ENVIRONMENT": "local",
        "WORKSPACE": "test",
        "PROJECT_NAME": "ftrs-dos",
        # URLs for local testing
        "LOCAL_ODS_URL": ods_mock_url,
        "LOCAL_APIM_API_URL": apim_url,
        "LOCAL_API_KEY": "test-api-key",
        "ODS_API_PAGE_LIMIT": "100",
        "MAX_RECEIVE_COUNT": "3",
        # JWT authentication for local testing (bypassed by mock server)
        "LOCAL_PRIVATE_KEY": test_private_key,
        "LOCAL_KID": "test-kid-local",
        "LOCAL_TOKEN_URL": f"{apim_url}/oauth2/token",
        # Disable X-Ray tracing
        "AWS_XRAY_SDK_ENABLED": "false",
        "POWERTOOLS_TRACE_DISABLED": "true",
    }

    # Store original environment
    original_env = {}
    for key in env_vars:
        original_env[key] = os.environ.get(key)

    # Set environment variables
    os.environ.update(env_vars)

    yield {
        "endpoint_url": endpoint_url,
        "ods_mock_url": ods_mock_url,
        "apim_url": apim_url,
        **env_vars,
    }

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def ods_happy_path_scenario() -> str:
    """Get the date that triggers the happy path scenario."""
    return "2025-12-08"


@pytest.fixture
def ods_empty_payload_scenario() -> str:
    """Get the date that triggers the empty payload scenario."""
    return "2025-12-09"


@pytest.fixture
def ods_server_error_scenario() -> str:
    """Get the date that triggers the server error scenario."""
    return "2025-12-16"
