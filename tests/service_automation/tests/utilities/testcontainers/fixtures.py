"""LocalStack fixtures for integration testing.

This module provides pytest fixtures for running integration tests against
LocalStack instead of real AWS services. All fixtures automatically configure
AWS clients to use the LocalStack endpoint.

The fixtures support two modes:
1. Local mode (USE_LOCALSTACK=true): Uses testcontainers LocalStack
2. Real AWS mode (default): Uses real AWS services with configured credentials

Usage:
    # In your test file or conftest.py
    from utilities.testcontainers import localstack_container, aws_test_environment

    def test_s3_operations(aws_test_environment, local_s3_utils):
        # local_s3_utils is pre-configured to use LocalStack
        buckets = local_s3_utils.list_buckets()
        assert "test-bucket" in buckets
"""

import os
from typing import Any, Generator

import boto3
import pytest
from loguru import logger

try:
    from testcontainers.localstack import LocalStackContainer
except ImportError:  # pragma: no cover
    LocalStackContainer = None

from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.infra.s3_util import S3Utils
from utilities.infra.secrets_util import GetSecretWrapper
from utilities.infra.sqs_util import get_sqs_client
from utilities.testcontainers.setup import setup_all_test_resources

try:
    from utilities.local_servers import crud_api_mock_server
except ImportError:  # pragma: no cover
    crud_api_mock_server = None

try:
    from utilities.local_servers import dos_search_server
except ImportError:  # pragma: no cover
    dos_search_server = None


def is_local_test_mode() -> bool:
    """Check if tests should run against LocalStack instead of real AWS.

    Checks the USE_LOCALSTACK environment variable dynamically each time
    to support late-binding of the variable during test setup.
    """
    return os.environ.get("USE_LOCALSTACK", "false").lower() == "true"


@pytest.fixture(scope="session")
def localstack_container() -> Generator[Any, None, None]:
    """LocalStack container for testing AWS services locally.

    This fixture starts a LocalStack container once per test session.
    It only starts if USE_LOCALSTACK=true environment variable is set.

    To use LocalStack for tests:
        USE_LOCALSTACK=true pytest tests/

    Yields:
        LocalStack container instance, or None if not in local mode
    """
    if not is_local_test_mode():
        logger.info(
            "Running tests against real AWS (set USE_LOCALSTACK=true for local)"
        )
        yield None
        return

    if LocalStackContainer is None:
        pytest.skip("testcontainers is required for USE_LOCALSTACK=true")

    logger.info("Starting LocalStack container for local testing...")
    container = LocalStackContainer(image="localstack/localstack:3.0")
    container.start(timeout=120)  # Increased timeout for CI runners
    try:
        logger.info(f"LocalStack started at {container.get_url()}")
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
def aws_test_environment(
    localstack_container: Any,
) -> Generator[dict[str, str], None, None]:
    """Configure AWS environment for testing.

    Sets up environment variables so all AWS clients automatically use
    LocalStack when in local mode. Also pre-creates required test resources.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Dict with endpoint_url and mode information
    """
    if localstack_container is None:
        # Real AWS mode
        yield {
            "mode": "aws",
            "endpoint_url": None,
        }
        return

    endpoint_url = localstack_container.get_url()

    # Set environment variables for all AWS clients
    # Note: Both AWS_ENDPOINT_URL and ENDPOINT_URL are set because different
    # libraries use different env var names (boto3 vs ftrs_common.utils.config)
    original_env = {
        "AWS_ENDPOINT_URL": os.environ.get("AWS_ENDPOINT_URL"),
        "ENDPOINT_URL": os.environ.get("ENDPOINT_URL"),
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "WORKSPACE": os.environ.get("WORKSPACE"),
        "AWS_REGION": os.environ.get("AWS_REGION"),
        "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
    }

    os.environ["AWS_ENDPOINT_URL"] = endpoint_url
    os.environ["ENDPOINT_URL"] = endpoint_url  # For ftrs_common.utils.config.Settings
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    # Ensure table naming is consistent across helpers:
    # - ftrs_common.utils.config.Settings defaults WORKSPACE to None (no suffix)
    # - ftrs_common.testing.table_config defaults WORKSPACE to "test" if missing
    # Setting WORKSPACE to an empty string ensures both produce no suffix.
    os.environ.setdefault("WORKSPACE", "")
    os.environ["AWS_REGION"] = "eu-west-2"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

    # Boto3 caches a default session; if it was created before the region
    # env vars were set, later `boto3.resource(...)` calls can still raise
    # NoRegionError. Reset the default session explicitly for LocalStack mode.
    boto3.setup_default_session(region_name=os.environ["AWS_DEFAULT_REGION"])

    logger.info(f"Configured AWS environment for LocalStack: {endpoint_url}")

    resources = setup_all_test_resources(endpoint_url)

    yield {
        "mode": "localstack",
        "endpoint_url": endpoint_url,
        "resources": resources,
    }

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture(scope="session")
def test_resources(aws_test_environment: dict) -> dict:
    """Get test resources created in LocalStack.

    Provides access to the S3 buckets, SQS queues, DynamoDB tables,
    and Secrets Manager secrets created during setup.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        Dict with buckets, queues, tables, and secrets
    """
    if not is_local_test_mode():
        return {}

    return aws_test_environment.get("resources", {})


@pytest.fixture(scope="session")
def local_s3_utils(aws_test_environment: dict) -> Any:
    """S3 utility configured for the test environment.

    Returns an S3Utils instance that automatically uses LocalStack
    when in local test mode.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        S3Utils instance
    """
    return S3Utils(endpoint_url=aws_test_environment.get("endpoint_url"))


@pytest.fixture(scope="session")
def local_sqs_client(aws_test_environment: dict) -> Any:
    """SQS client configured for the test environment.

    Returns an SQS client that automatically uses LocalStack
    when in local test mode.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        Boto3 SQS client
    """
    return get_sqs_client(endpoint_url=aws_test_environment.get("endpoint_url"))


@pytest.fixture(scope="session")
def local_secrets_client(aws_test_environment: dict) -> Any:
    """Secrets Manager wrapper configured for the test environment.

    Returns a GetSecretWrapper instance that automatically uses LocalStack
    when in local test mode.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        GetSecretWrapper instance
    """
    return GetSecretWrapper(endpoint_url=aws_test_environment.get("endpoint_url"))


@pytest.fixture(scope="session")
def local_lambda_wrapper(aws_test_environment: dict) -> Any:
    """Lambda wrapper configured for the test environment.

    Returns a LambdaWrapper instance that automatically uses LocalStack
    when in local test mode.

    Note: Lambda execution in LocalStack requires LocalStack Pro.
    For local testing without Pro, consider invoking Lambda handlers directly.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        LambdaWrapper instance
    """
    return LambdaWrapper(endpoint_url=aws_test_environment.get("endpoint_url"))


@pytest.fixture(scope="session")
def local_cloudwatch_logs(aws_test_environment: dict) -> Any:
    """CloudWatch Logs wrapper configured for the test environment.

    Returns a CloudWatchLogsWrapper instance that automatically uses LocalStack
    when in local test mode.

    Args:
        aws_test_environment: Test environment fixture

    Returns:
        CloudWatchLogsWrapper instance
    """
    return CloudWatchLogsWrapper(endpoint_url=aws_test_environment.get("endpoint_url"))


@pytest.fixture(scope="session")
def local_dos_search_server(
    aws_test_environment: dict,
) -> Generator[dict[str, Any], None, None]:
    """DOS Search API server running locally.

    Starts the DOS Search Lambda as a local HTTP server using FastAPI.
    Only starts if in local test mode (USE_LOCALSTACK=true).

    Args:
        aws_test_environment: Test environment fixture

    Yields:
        Dict with base_url and process information
    """
    if not is_local_test_mode():
        yield {"mode": "aws", "base_url": None, "process": None}
        return

    if dos_search_server is None:
        pytest.skip("utilities.local_servers.dos_search_server import failed")

    port = 8002
    host = "127.0.0.1"
    endpoint_url = aws_test_environment.get("endpoint_url")

    try:
        process = dos_search_server.run_dos_search_server(
            port=port,
            host=host,
            endpoint_url=endpoint_url,
        )
        base_url = f"http://{host}:{port}"
        logger.info(f"DOS Search server started at {base_url}")

        yield {
            "mode": "local",
            "base_url": base_url,
            "process": process,
        }
    except Exception as e:
        logger.error(f"Failed to start DOS Search server: {e}")
        yield {"mode": "error", "base_url": None, "process": None, "error": str(e)}
        return
    finally:
        if "process" in locals() and process:
            dos_search_server.stop_server(process)
            logger.info("DOS Search server stopped")


@pytest.fixture(scope="session")
def local_crud_apis_server(
    aws_test_environment: dict,
) -> Generator[dict[str, Any], None, None]:
    """CRUD APIs mock server running locally.

    Starts a mock CRUD APIs server locally for testing the ETL ODS pipeline.
    Only starts if in local test mode (USE_LOCALSTACK=true).

    Args:
        aws_test_environment: Test environment fixture

    Yields:
        Dict with base_url and process information
    """
    if not is_local_test_mode():
        yield {"mode": "aws", "base_url": None, "process": None}
        return

    if crud_api_mock_server is None:
        pytest.skip("utilities.local_servers.crud_api_mock_server import failed")

    port = 8001
    host = "127.0.0.1"

    try:
        server_info = crud_api_mock_server.run_crud_api_mock_server(
            port=port, host=host
        )
        base_url = server_info.get("url")
        logger.info(f"CRUD APIs mock server started at {base_url}")

        yield {
            "mode": "local",
            "base_url": base_url,
            "process": server_info.get("process"),
            "server_info": server_info,
        }
    except Exception as e:
        logger.error(f"Failed to start CRUD APIs mock server: {e}")
        yield {"mode": "error", "base_url": None, "process": None, "error": str(e)}
        return
    finally:
        if "server_info" in locals() and server_info:
            crud_api_mock_server.stop_server(server_info)
            logger.info("CRUD APIs mock server stopped")
