"""
Utility functions for DoS DB data migration tests
"""

import os

import boto3
import pytest
from utilities.common.constants import ENV_ENVIRONMENT


def get_test_data_script(filename: str) -> str:
    """
    Get a test data script from test-data/integration-tests/
    """
    s3_client = boto3.client("s3")
    if not (env := os.getenv(ENV_ENVIRONMENT)):
        pytest.fail(f"{ENV_ENVIRONMENT} environment variable is not set")

    bucket = f"ftrs-dos-{env}-data-migration-pipeline-store"
    response = s3_client.get_object(
        Bucket=bucket,
        Key=f"test-data/integration-tests/{filename}",
    )
    if not response.get("Body"):
        raise FileNotFoundError(f"Test data script {filename} not found in S3")

    return response["Body"].read().decode("utf-8")
