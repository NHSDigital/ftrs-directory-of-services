import pytest
import subprocess
from pytest_bdd import scenarios, given, when, then, parsers
from config import config
from loguru import logger
from utilities.infra.s3_util import S3Utils

# Load feature file
scenarios("../features/test_s3_bucket.feature")

@pytest.fixture(scope="module")
def aws_s3_client():
    """Fixture to initialize AWS S3 utility"""
    return S3Utils()

@pytest.fixture
def fetch_s3_buckets(aws_s3_client):
    """Retrieve list of S3 buckets (Fixture)"""
    logger.info("Fetching list of S3 buckets...")
    return aws_s3_client.list_buckets()

@given("I am authenticated with AWS CLI")
def check_aws_access():
    """Ensure AWS CLI authentication works"""
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    logger.info("AWS CLI Authenticate", result.returncode)
    assert result.returncode == 0, f"Failed to authenticate with AWS CLI: {result.stderr}"


@then(parsers.parse('The S3 bucket "{bucket}" exists'))
def confirm_s3_bucket_exists(bucket, aws_s3_client, workspace, env):
    project = config.get("project")
    logger.info(f"project: {project}, bucket: {bucket}, env: {env}, workspace: {workspace}")
    if workspace=="":
        bucket_name = project + "-" + bucket + "-" + env
    else:
        bucket_name = project + "-" + bucket + "-" + env + "-" + workspace
    response = aws_s3_client.check_bucket_exists(bucket_name)
    logger.info("Bucket Exists: {}", response)
    assert response == True

@when("I fetch the list of S3 buckets")
def fetch_buckets(aws_s3_client):
    """Retrieve list of S3 buckets"""
    return aws_s3_client.list_buckets()

@then("the bucket names should be valid")
def validate_bucket_names(fetch_s3_buckets):
    """Validate AWS S3 bucket naming rules"""
    bucket_names = fetch_s3_buckets
    logger.info("Available Buckets: {}", bucket_names)
    assert bucket_names, "No buckets found!"
    for bucket in bucket_names:
        logger.info("Valid Bucket Names: {}", bucket)
        assert 3 <= len(bucket) <= 63, f"Invalid length for bucket {bucket}"
        assert bucket.islower(), f"Bucket {bucket} must be lowercase"
        assert bucket[0].isalnum() and bucket[-1].isalnum(), f"Bucket {bucket} must start & end with letter/number"
        assert ".." not in bucket, f"Bucket {bucket} contains consecutive dots"
        assert not bucket.startswith("xn--"), f"Bucket {bucket} cannot start with 'xn--'"
        assert not bucket.endswith("-s3alias"), f"Bucket {bucket} cannot end with '-s3alias'"
