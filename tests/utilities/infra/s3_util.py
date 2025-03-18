import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


class S3Utils:
    def __init__(self):
        """Initialize AWS S3 client using credentials from the terminal (AWS CLI)"""
        try:
            # Use default AWS CLI profile and automatically detect region
            session = boto3.Session()
            self.s3_client = session.client("s3")

        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error: AWS credentials not found. Run 'aws configure'.\n{e}")
            raise

    def list_buckets(self):
        """Returns a list of S3 bucket names."""
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception as e:
            print(f"Error fetching bucket list: {e}")
            return []

    def check_bucket_exists(self, bucket_name):
        """
        Determine whether the bucket exists and you have access to it.
        :return: True when the bucket exists; otherwise, False.
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            print("Bucket %s exists.", bucket_name)
            exists = True
        except Exception as e:
            print(f"Error: bucket not found'.\n{e}")
            exists = False
        return exists
