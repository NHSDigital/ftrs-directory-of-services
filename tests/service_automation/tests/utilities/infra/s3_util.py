import os
from typing import Optional

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from loguru import logger


class S3Utils:
    """S3 utility class that supports both real AWS and LocalStack.

    Args:
        endpoint_url: Optional endpoint URL for LocalStack or other S3-compatible services.
                     If not provided, checks AWS_ENDPOINT_URL environment variable,
                     then falls back to real AWS.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        try:
            # Use provided endpoint, environment variable, or default to real AWS
            endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")

            session = boto3.Session()
            client_kwargs = {}
            if endpoint:
                client_kwargs["endpoint_url"] = endpoint
                logger.debug(f"Using S3 endpoint: {endpoint}")

            self.s3_client = session.client("s3", **client_kwargs)

        except (NoCredentialsError, PartialCredentialsError):
            logger.error("Error: AWS credentials not found.")
            raise

    def list_buckets(self):
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception:
            logger.error("Error fetching bucket list")
            return []

    def check_bucket_exists(self, bucket_name):
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            exists = True
        except Exception:
            logger.error("Error: bucket not found")
            exists = False
        return exists

    def get_object(self, bucket_name, filename):
        try:
            response = self.s3_client.get_object(
                Bucket=bucket_name,
                Key=filename,
            )
            file_data = response["Body"].read().decode("utf-8")
        except Exception:
            logger.error("Error: file not found")
        return file_data

    def download_object(self, bucket_name, filepath, filename):
        try:
            self.s3_client.download_file(
                Bucket=bucket_name, Key=filename, Filename=filepath
            )
        except Exception:
            logger.error("Error: file could not be downloaded")

    def put_object(self, bucket_name, filepath, file_name):
        try:
            self.s3_client.upload_file(
                Filename=filepath, Bucket=bucket_name, Key=file_name
            )
        except Exception:
            logger.error("Error: file could not be uploaded")

    def delete_object(self, bucket_name, filename):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=filename)
        except Exception:
            logger.error("Error: file could not be deleted")
