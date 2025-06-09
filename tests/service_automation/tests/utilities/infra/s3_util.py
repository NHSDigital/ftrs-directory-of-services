import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from loguru import logger


class S3Utils:
    def __init__(self):
        try:
            # Use default AWS CLI profile and automatically detect region
            session = boto3.Session()
            self.s3_client = session.client("s3")

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
            self.s3_client.download_file(Bucket=bucket_name, Key=filename, Filename=filepath)
        except Exception:
            logger.error("Error: file could not be downloaded")

    def put_object(self, bucket_name, filepath, file_name):
        try:
            self.s3_client.upload_file(Filename=filepath, Bucket=bucket_name, Key=file_name)
        except Exception:
            logger.error("Error: file could not be uploaded")

    def delete_object(self, bucket_name, filename):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=filename)
        except Exception:
            logger.error("Error: file could not be deleted")
