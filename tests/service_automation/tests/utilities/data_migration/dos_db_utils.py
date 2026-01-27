"""
Utility functions for DoS DB data migration tests
"""

import boto3
import os
from utilities.common.constants import ENV_ENVIRONMENT
import pytest


def get_test_data_script(filename: str) -> str:
    """
    Get a test data script from test-data/integration-tests/

    Uses AWS_PROFILE environment variable if set, otherwise uses default AWS credentials.
    """
    # Use session to support AWS profiles from environment
    profile_name = os.getenv("AWS_PROFILE")
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
    else:
        session = boto3.Session()

    s3_client = session.client("s3", region_name="eu-west-2")

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
