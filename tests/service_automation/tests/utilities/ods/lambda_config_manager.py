"""
Lambda configuration manager for ODS ETL testing.

Handles Lambda environment variable configuration for VTL mock integration
using secure Secrets Manager approach instead of plain text environment variables.
"""
import boto3
import json
import os
from typing import Dict, Any
from loguru import logger

from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.apigateway_vtl_mock import APIGatewayVTLMockManager
from utilities.common.constants import ENV_ENVIRONMENT, ENV_WORKSPACE, ENV_PROJECT_NAME


class LambdaConfigManager:
    """Manages Lambda environment configuration for VTL mock testing."""

    # Test-specific environment variables that must be cleaned up
    TEST_ENV_VARS = {"MOCK_TESTING_SCENARIOS"}

    def __init__(self, lambda_client: LambdaWrapper):
        self.lambda_client = lambda_client
        self.original_env_vars: Dict[str, Any] = {}
        self.current_secret_name: str = ""  # Track created secret name for cleanup
        self.created_secret: bool = False  # Track if we created the secret (vs reused existing)

    def configure_for_vtl_mock(self, lambda_name: str, mock_manager: APIGatewayVTLMockManager) -> None:
        """Configure Lambda to use VTL mock API Gateway with secure Secrets Manager approach."""
        mock_details = mock_manager.get_mock_details()
        mock_url = mock_details["endpoint_url"]
        mock_api_key = mock_details["api_key_value"]

        # Build complete ODS URL with full path
        complete_ods_url = f"{mock_url}/organisation-data-terminology-api/fhir/Organization"

        # Store mock API key in Secrets Manager for secure access
        self._store_mock_api_key_in_secrets(mock_api_key)

        # Get current lambda configuration
        lambda_client = self.lambda_client.lambda_client
        current_config = lambda_client.get_function_configuration(FunctionName=lambda_name)

        # Store original environment for restoration
        self.original_env_vars = current_config.get("Environment", {}).get("Variables", {}).copy()

        # Update environment to enable mock testing mode
        env_vars = self.original_env_vars.copy()
        env_vars["ODS_URL"] = complete_ods_url
        env_vars["MOCK_TESTING_SCENARIOS"] = "true"

        # Apply configuration
        lambda_client.update_function_configuration(
            FunctionName=lambda_name, Environment={"Variables": env_vars}
        )

        # Wait for lambda update to complete
        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=lambda_name)

        logger.info("Lambda configured for mock testing mode")

    def _store_mock_api_key_in_secrets(self, api_key: str) -> None:
        """Store mock API key in AWS Secrets Manager for secure access."""
        try:
            # Get environment and workspace from environment variables
            env = os.environ.get(ENV_ENVIRONMENT, "dev")
            workspace = os.environ.get(ENV_WORKSPACE, "")

            project = os.environ.get(ENV_PROJECT_NAME, "ftrs-dos")
            resource_prefix = f"{project}/{env}"
            secret_name = f"/{resource_prefix}/mock-api-gateway-key"

            # Store secret name for cleanup
            self.current_secret_name = secret_name

            # Use the default region for secrets
            aws_region = os.environ.get("AWS_REGION", "eu-west-2")
            secrets_client = boto3.client("secretsmanager", region_name=aws_region)

            # Create or update secret
            secret_value = json.dumps({"api_key": api_key})

            # Try to create the secret, if it exists, update it instead
            try:
                secrets_client.create_secret(
                    Name=secret_name,
                    Description="Temporary mock API Gateway key for testing",
                    SecretString=secret_value,
                    Tags=[
                        {"Key": "Purpose", "Value": "Testing"},
                        {"Key": "AutoCleanup", "Value": "true"},
                        {"Key": "Environment", "Value": env},
                        {"Key": "Workspace", "Value": workspace}
                    ]
                )
                logger.info(f"Created mock API key secret: {secret_name}")
                self.created_secret = True

            except secrets_client.exceptions.ResourceExistsException:
                # Secret already exists, update it instead
                secrets_client.update_secret(
                    SecretId=secret_name,
                    SecretString=secret_value
                )
                logger.info(f"Updated existing mock API key secret: {secret_name}")
                self.created_secret = False  # We didn't create it, just updated

            except secrets_client.exceptions.InvalidRequestException as e:
                if "currently marked deleted" in str(e) or "scheduled for deletion" in str(e):
                    # Wait for deletion to complete and recreate
                    logger.info(f"Secret {secret_name} is scheduled for deletion, waiting...")
                    import time
                    time.sleep(5)  # Wait a bit for deletion to process
                    # Try to create again
                    secrets_client.create_secret(
                        Name=secret_name,
                        Description="Temporary mock API Gateway key for testing",
                        SecretString=secret_value,
                        Tags=[
                            {"Key": "Purpose", "Value": "Testing"},
                            {"Key": "AutoCleanup", "Value": "true"},
                            {"Key": "Environment", "Value": env},
                            {"Key": "Workspace", "Value": workspace}
                        ]
                    )
                    logger.info(f"Created mock API key secret after deletion: {secret_name}")
                    self.created_secret = True
                else:
                    raise

        except Exception as e:
            logger.error(f"Failed to store mock API key in secrets: {e}")
            raise

    def restore_original_configuration(self, lambda_name: str) -> None:
        """Restore Lambda's original environment configuration. Don't clean up secrets during session."""
        # Don't clean up secrets here - they should persist for the session
        # Secret cleanup will happen in the session fixture cleanup

        if not self.original_env_vars:
            logger.warning("No original environment stored - removing test vars only")
            self._remove_test_vars_only(lambda_name)
            return

        logger.info(f"Restoring original environment for lambda {lambda_name}")

        # Remove test variables from original config (in case they existed before)
        cleaned_env_vars = self._remove_test_variables(self.original_env_vars)

        lambda_client = self.lambda_client.lambda_client
        lambda_client.update_function_configuration(
            FunctionName=lambda_name, Environment={"Variables": cleaned_env_vars}
        )

        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=lambda_name)

        logger.info("Lambda configuration restored")

    def _cleanup_mock_api_key_secret(self) -> None:
        """Remove mock API key from AWS Secrets Manager."""
        try:
            # Use stored secret name
            secret_name = self.current_secret_name

            if not secret_name:
                logger.warning("No secret name stored - skipping cleanup")
                return

            aws_region = os.environ.get("AWS_REGION", "eu-west-2")
            secrets_client = boto3.client("secretsmanager", region_name=aws_region)

            # Delete the secret
            try:
                secrets_client.delete_secret(
                    SecretId=secret_name,
                    ForceDeleteWithoutRecovery=True  # Immediate deletion for test secrets
                )
                logger.info(f"Cleaned up mock API key secret: {secret_name}")
            except secrets_client.exceptions.InvalidRequestException as e:
                if "currently marked deleted" in str(e) or "scheduled for deletion" in str(e):
                    logger.info(f"Secret {secret_name} already scheduled for deletion")
                else:
                    raise

            # Clear the stored secret name after cleanup
            self.current_secret_name = ""

        except secrets_client.exceptions.ResourceNotFoundException:
            logger.info("Mock API key secret already cleaned up or not found")
        except Exception as e:
            logger.warning(f"Failed to cleanup mock API key secret (non-critical): {e}")

    def _remove_test_variables(self, env_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Remove test environment variables from env vars dict."""
        cleaned_vars = env_vars.copy()

        for test_var in self.TEST_ENV_VARS:
            if test_var in cleaned_vars:
                del cleaned_vars[test_var]
                logger.debug(f"Removed test variable: {test_var}")

        return cleaned_vars

    def _remove_test_vars_only(self, lambda_name: str) -> None:
        """Remove only test variables from Lambda environment."""
        lambda_client = self.lambda_client.lambda_client
        current_config = lambda_client.get_function_configuration(FunctionName=lambda_name)
        current_env_vars = current_config.get("Environment", {}).get("Variables", {}).copy()

        cleaned_env_vars = self._remove_test_variables(current_env_vars)

        # Only update if there were changes
        if cleaned_env_vars != current_env_vars:
            lambda_client.update_function_configuration(
                FunctionName=lambda_name, Environment={"Variables": cleaned_env_vars}
            )

            waiter = lambda_client.get_waiter("function_updated")
            waiter.wait(FunctionName=lambda_name)

            logger.info("Test variables removed from Lambda")
        else:
            logger.info("No test variables found in Lambda")
