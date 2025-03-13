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
