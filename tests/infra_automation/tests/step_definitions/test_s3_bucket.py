import pytest
import subprocess
from pytest_bdd import scenarios, given, when, then, parsers
from config import config
import allure
from loguru import logger
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
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
    with allure.step(f"authenticate with AWS CLI: {aws_s3_client.list_buckets()}"):
        logger.info("Fetching list of S3 buckets...")
        return aws_s3_client.list_buckets()

@given("I am authenticated with AWS CLI")
def check_aws_access():
    """Ensure AWS CLI authentication works"""
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    with allure.step(f"authenticate with AWS CLI: {result.returncode}"):
        logger.info("AWS CLI Authenticate", result.returncode)
        assert result.returncode == 0, f"Failed to authenticate with AWS CLI: {result.stderr}"


@then(parsers.parse('The S3 bucket exists'), target_fixture='fbucket_name')
def confirm_s3_bucket_exists(aws_s3_client, workspace, env):
    project = config.get("project")
    bucket = config.get("bucket_type")
    if workspace=="":
        bucket_name = project + "-" + bucket + "-" + env
    else:
        bucket_name = project + "-" + bucket + "-" + env + "-" + workspace
    response = aws_s3_client.check_bucket_exists(bucket_name)
    with allure.step(f"Response: {response}"):
        logger.info("Bucket Exits: {}", response)
        assert response == True

@when("I fetch the list of S3 buckets")
def fetch_buckets(aws_s3_client):
    """Retrieve list of S3 buckets"""
    return aws_s3_client.list_buckets()

@then("the bucket names should be valid")
def validate_bucket_names(fetch_s3_buckets):
    """Validate AWS S3 bucket naming rules"""
    bucket_names = fetch_s3_buckets
    with allure.step(f"Available Buckets: {bucket_names}"):
        logger.info("Available Buckets: {}", bucket_names)
        assert bucket_names, "No buckets found!"
    for bucket in bucket_names:
        with allure.step(f"Valid Bucket Names: {bucket_names}"):
            logger.info("Valid Bucket Names: {}", bucket_names)
            assert 3 <= len(bucket) <= 63, f"Invalid length for bucket {bucket}"
            assert bucket.islower(), f"Bucket {bucket} must be lowercase"
            assert bucket[0].isalnum() and bucket[-1].isalnum(), f"Bucket {bucket} must start & end with letter/number"
            assert ".." not in bucket, f"Bucket {bucket} contains consecutive dots"
            assert not bucket.startswith("xn--"), f"Bucket {bucket} cannot start with 'xn--'"
            assert not bucket.endswith("-s3alias"), f"Bucket {bucket} cannot end with '-s3alias'"
