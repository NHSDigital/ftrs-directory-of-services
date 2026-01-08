import boto3

DEV_MIGRATION_STORE_BUCKET = "ftrs-dos-dev-data-migration-pipeline-store"


def get_test_data_script(filename: str):
    """
    Get a test data script from test-data/integration-tests/
    """
    s3_client = boto3.client("s3")

    response = s3_client.get_object(
        Bucket=DEV_MIGRATION_STORE_BUCKET,
        Key=f"test-data/integration-tests/{filename}",
    )
    if not response.get("Body"):
        raise FileNotFoundError(f"Test data script {filename} not found in S3")

    return response["Body"].read().decode("utf-8")
