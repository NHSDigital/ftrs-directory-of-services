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
            logger.error("Error: AWS credentials not found.")
            raise

    def list_buckets(self):
        """Returns a list of S3 bucket names."""
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception:
            logger.error("Error fetching bucket list")
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
            logger.error("Error: bucket not found")
            exists = False
        return exists

    def get_bucket(self, project, workspace, env, stack, bucket):
        if workspace == "":
            bucket_name = project + "-" + env + "-" + stack + "-" + bucket
        else:
            bucket_name = project + "-" + env + "-" + stack + "-" + bucket + "-" + workspace
        return bucket_name

    def get_object(bucket_name, filename):
        # bucket = get_bucket(context)
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=filename,
        )
        file_data = response["Body"].read().decode("utf-8")
        return file_data

    def download_object(bucket_name, filepath, filename):
        # bucket = get_bucket(bucket_name)
        s3_client.download_file(Bucket=bucket_name, Key=filename, Filename=filepath)

    def put_object(bucket_name, filepath, file_name):
        # bucket = get_bucket(bucket_name)
        s3_client.upload_file(Filename=filepath, Bucket=bucket_name, Key=file_name)

    def delete_object(bucket_name, filename):
        # bucket = get_bucket(bucket_name)
        s3_client.delete_object(Bucket=bucket_name, Key=filename)
