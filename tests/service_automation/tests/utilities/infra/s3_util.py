import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from loguru import logger


class S3Utils:
    def __init__(self):
        """Initialize AWS S3 client using credentials from the terminal (AWS CLI)"""
        try:
            # Use default AWS CLI profile and automatically detect region
            session = boto3.Session()
            self.s3_client = session.client("s3")

        except (NoCredentialsError, PartialCredentialsError):
            logger.debug("Error: AWS credentials not found.")
            raise

    def list_buckets(self):
        """Returns a list of S3 bucket names."""
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception:
            logger.debug("Error fetching bucket list")
            return []

    def check_bucket_exists(self, bucket_name):
        """
        Determine whether the bucket exists and you have access to it.
        :return: True when the bucket exists; otherwise, False.
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            exists = True
        except Exception:
            logger.debug("Error: bucket not found")
            exists = False
        return exists
