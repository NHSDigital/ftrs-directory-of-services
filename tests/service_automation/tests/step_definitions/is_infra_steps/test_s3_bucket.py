import pytest
import subprocess
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra.s3_util import S3Utils
from utilities.common import directories, csv_reader


# Load feature file
scenarios("./is_infra_features/s3.feature")


@pytest.fixture(scope="module")
def aws_s3_client():
    """Fixture to initialize AWS S3 utility"""
    return S3Utils()

@pytest.fixture
def fetch_s3_buckets(aws_s3_client):
    """Retrieve list of S3 buckets (Fixture)"""
    logger.info("Fetching list of S3 buckets...")
    return aws_s3_client.list_buckets()


@given(parsers.parse('I can see the S3 bucket "{bucket}" for stack "{stack}"'), target_fixture='fbucket_name')
def confirm_s3_bucket_exists(aws_s3_client, project, bucket, stack, workspace, env):
    bucket_name = aws_s3_client.get_bucket(project, workspace, env, stack, bucket)
    response = aws_s3_client.check_bucket_exists(bucket_name)
    assert response == True
    return bucket_name

@given(parsers.parse('I upload the file "{file_name}" to the s3 bucket'), target_fixture='file_name')
def put_s3_file(aws_s3_client, fbucket_name, file_name):
    file_name = file_name + ".csv"
    filepath = "tests/csv_files/"+file_name
    bucket_name = fbucket_name
    aws_s3_client.put_object(bucket_name, filepath, file_name)
    return file_name

@given("I am authenticated with AWS CLI")
def check_aws_access():
    """Ensure AWS CLI authentication works"""
    result = subprocess.run(["aws", "sts", "get-caller-identity"], capture_output=True, text=True)
    logger.debug("AWS CLI Authenticate", result.returncode)
    assert result.returncode == 0, f"Failed to authenticate with AWS CLI: {result.stderr}"

@given(parsers.parse('I can see the S3 bucket "{bucket}" for stack "{stack}"'), target_fixture='fbucket_name')
def confirm_s3_bucket_exists(aws_s3_client, project, bucket, stack, workspace, env):
    bucket_name = aws_s3_client.get_bucket(project, workspace, env, stack, bucket)
    response = aws_s3_client.check_bucket_exists(bucket_name)
    assert response == True
    return bucket_name

@given(parsers.parse('I upload the file "{file_name}" to the s3 bucket'), target_fixture='ffile_name')
def put_s3_file(aws_s3_client, fbucket_name, file_name):
    file_name = file_name + ".csv"
    filepath = "tests/csv_files/"+file_name
    bucket_name = fbucket_name
    aws_s3_client.put_object(bucket_name, filepath, file_name)
    return file_name

@when("I fetch the list of S3 buckets")
def fetch_buckets(aws_s3_client):
    """Retrieve list of S3 buckets"""
    return aws_s3_client.list_buckets()

@then(parsers.parse('I can download the file from the s3 bucket'), target_fixture='fdownload_file')
def download_s3_file(aws_s3_client, fbucket_name, ffile_name):
    downloadfile = ffile_name
    directories.create_folder("downloads")
    file_name = "downloads/" + downloadfile
    bucket_name = fbucket_name
    aws_s3_client.download_object(bucket_name, file_name, downloadfile)
    return file_name


@then(parsers.parse('I can delete the file from the s3 bucket'))
def delete_s3_file(aws_s3_client, fbucket_name, ffile_name):
    file_name = ffile_name
    bucket_name = fbucket_name
    aws_s3_client.delete_object(bucket_name, file_name)

@then(parsers.parse("the file contains {rowcount} rows"))
def count_csv_rows(fdownload_file, rowcount):
    file_name = fdownload_file
    row_count = str(csv_reader.csv_row_count(file_name))
    assert row_count == rowcount

@then("the bucket names should be valid")
def validate_bucket_names(fetch_s3_buckets):
    """Validate AWS S3 bucket naming rules"""
    bucket_names = fetch_s3_buckets
    logger.debug("Available Buckets: {}", bucket_names)
    assert bucket_names, "No buckets found!"
    for bucket in bucket_names:
        logger.debug("Valid Bucket Names: {}", bucket)
        assert 3 <= len(bucket) <= 63, f"Invalid length for bucket {bucket}"
        assert bucket.islower(), f"Bucket {bucket} must be lowercase"
        assert bucket[0].isalnum() and bucket[-1].isalnum(), f"Bucket {bucket} must start & end with letter/number"
        assert ".." not in bucket, f"Bucket {bucket} contains consecutive dots"
        assert not bucket.startswith("xn--"), f"Bucket {bucket} cannot start with 'xn--'"
        assert not bucket.endswith("-s3alias"), f"Bucket {bucket} cannot end with '-s3alias'"
