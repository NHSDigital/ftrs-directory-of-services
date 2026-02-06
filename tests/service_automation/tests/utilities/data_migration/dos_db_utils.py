"""
Utility functions for DoS DB data migration tests
"""

import os
from pathlib import Path

import boto3
import pytest
from utilities.common.constants import ENV_ENVIRONMENT

# Path to local SQL files relative to this file
LOCAL_SQL_FILES_DIR = Path(__file__).parent.parent.parent / "sql_files"


def is_local_test_mode() -> bool:
    """Check if tests should use local files instead of S3."""
    return os.environ.get("USE_LOCALSTACK", "false").lower() == "true"


def get_test_data_script(filename: str) -> str:
    """
    Get a test data script from local files or S3.

    In local mode (USE_LOCALSTACK=true), loads from tests/sql_files/data_migration/.
    In AWS mode, downloads from S3 bucket.

    Uses AWS_PROFILE environment variable if set, otherwise uses default AWS credentials.
    """
    if is_local_test_mode():
        return _get_local_script(filename)
    return _get_s3_script(filename)


def _get_local_script(filename: str) -> str:
    """Load a test data script from local files."""
    local_path = LOCAL_SQL_FILES_DIR / filename
    if not local_path.exists():
        raise FileNotFoundError(
            f"Local test data script not found: {local_path}\n"
            f"Please ensure the file exists in tests/sql_files/data_migration/"
        )
    return local_path.read_text(encoding="utf-8")


def _get_s3_script(filename: str) -> str:
    """Download a test data script from S3."""
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
