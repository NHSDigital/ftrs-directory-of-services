import boto3
import os
from loguru import logger


class ODSMockClient:
    """
    Retrieves details from Terraform-deployed ODS mock API Gateway.
    """

    def __init__(self, region_name: str = "eu-west-2"):
        """Initialize the ODS mock manager."""
        self.region_name = region_name
        self.ssm_client = boto3.client("ssm", region_name=region_name)
        self._cached_url = None

    def get_mock_endpoint_url(self) -> str:
        """
        Get ODS mock API URL from Terraform-deployed infrastructure.

        Returns:
            The API Gateway endpoint URL
        """
        if self._cached_url is not None:
            return self._cached_url

        try:
            env = os.environ.get("ENVIRONMENT", "dev")
            project = os.environ.get("PROJECT_NAME", "ftrs-dos")
            workspace = os.environ.get("WORKSPACE", "")

            parameter_name = f"/{project}-{env}/mock-api/endpoint-url-{workspace}"

            response = self.ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
            api_url = response["Parameter"]["Value"]
            logger.info("Retrieved ODS mock API URL")

            self._cached_url = api_url
            return api_url

        except Exception as e:
            logger.error(f"Failed to retrieve ODS mock endpoint URL: {e}")
            raise
