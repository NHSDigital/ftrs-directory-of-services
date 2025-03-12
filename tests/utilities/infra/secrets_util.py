import boto3
import json
from infra_automation.tests.config import config  # Ensure Config is correctly imported

class SecretsManagerUtils:
    def __init__(self):
        """Initialize AWS Secrets Manager client"""
        self.region = config["aws"]["region"]
        self.secret_name = config["aws"]["secret_name"]
        self.client = boto3.client("secretsmanager", region_name=self.region)

    def get_aws_credentials(self):
        """Retrieve AWS credentials from Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            secret_data = json.loads(response["SecretString"])
            return {
                "access_key": secret_data["AWS_ACCESS_KEY"],
                "secret_key": secret_data["AWS_SECRET_KEY"]
            }
        except Exception as e:
            print(f"Error fetching AWS credentials: {e}")
            raise
