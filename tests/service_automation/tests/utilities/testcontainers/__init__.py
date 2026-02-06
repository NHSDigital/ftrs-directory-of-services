"""Testcontainers utilities for local AWS service testing.

This module provides fixtures and utilities for running integration tests
against LocalStack instead of real AWS services.

Usage in conftest.py:
    from utilities.testcontainers import (
        localstack_container,
        aws_test_environment,
        local_s3_utils,
        local_sqs_client,
        local_secrets_client,
        local_lambda_wrapper,
    )

    # Re-export fixtures for pytest discovery
    localstack_container = localstack_container
    aws_test_environment = aws_test_environment
"""

from utilities.testcontainers.etl_ods_fixtures import (
    etl_ods_pipeline_invoker,
    etl_ods_test_environment,
    local_ods_mock_server,
    ods_empty_payload_scenario,
    ods_happy_path_scenario,
    ods_server_error_scenario,
)
from utilities.testcontainers.fixtures import (
    aws_test_environment,
    is_local_test_mode,
    local_cloudwatch_logs,
    local_lambda_wrapper,
    local_s3_utils,
    local_secrets_client,
    local_sqs_client,
    localstack_container,
)
from utilities.testcontainers.setup import (
    setup_test_s3_buckets,
    setup_test_secrets,
    setup_test_sqs_queues,
)

__all__ = [
    # Fixtures
    "localstack_container",
    "aws_test_environment",
    "is_local_test_mode",
    "local_s3_utils",
    "local_sqs_client",
    "local_secrets_client",
    "local_lambda_wrapper",
    "local_cloudwatch_logs",
    # ETL ODS fixtures
    "local_ods_mock_server",
    "etl_ods_pipeline_invoker",
    "etl_ods_test_environment",
    "ods_happy_path_scenario",
    "ods_empty_payload_scenario",
    "ods_server_error_scenario",
    # Setup functions
    "setup_test_s3_buckets",
    "setup_test_sqs_queues",
    "setup_test_secrets",
]
