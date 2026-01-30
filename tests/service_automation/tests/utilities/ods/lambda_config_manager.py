import time
from typing import Any, Dict

from loguru import logger
from utilities.infra.apigateway_ods_mock import ODSMockClient
from utilities.infra.lambda_util import LambdaWrapper


class LambdaConfigManager:
    """Manages Lambda environment configuration for ODS mock testing."""

    # Test-specific environment variables that must be cleaned up
    TEST_ENV_VARS = {"MOCK_TESTING_SCENARIOS"}

    def __init__(self, lambda_client: LambdaWrapper):
        self.lambda_client = lambda_client
        self.original_env_vars: Dict[str, Any] = {}

    def configure_for_ods_mock(
        self, lambda_name: str, mock_client: ODSMockClient
    ) -> None:
        """Configure Lambda to use ODS mock API Gateway."""
        mock_url = mock_client.get_mock_endpoint_url()

        # Get current lambda configuration
        lambda_client = self.lambda_client.lambda_client
        current_config = lambda_client.get_function_configuration(
            FunctionName=lambda_name
        )

        # Store original environment for restoration
        self.original_env_vars = (
            current_config.get("Environment", {}).get("Variables", {}).copy()
        )

        # Update environment to enable mock testing mode
        env_vars = self.original_env_vars.copy()
        env_vars["ODS_URL"] = mock_url
        env_vars["MOCK_TESTING_SCENARIOS"] = "true"

        # Apply configuration
        lambda_client.update_function_configuration(
            FunctionName=lambda_name, Environment={"Variables": env_vars}
        )

        # Wait for lambda update to complete
        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=lambda_name)

        # Additional wait to ensure environment variables are fully propagated
        # Lambda runtime may take a moment to pick up new environment variables
        time.sleep(5)

        logger.info("Lambda configured for ODS mock testing mode")
        logger.info("Lambda will read API key from Secrets Manager for security")

    def restore_original_configuration(self, lambda_name: str) -> None:
        """Restore Lambda's original environment configuration."""
        if not self.original_env_vars:
            logger.warning("No original environment stored - removing test vars only")
            self._remove_test_vars_only(lambda_name)
            return

        logger.info(f"Restoring original environment for lambda {lambda_name}")

        cleaned_env_vars = self._remove_test_variables(self.original_env_vars)

        lambda_client = self.lambda_client.lambda_client
        lambda_client.update_function_configuration(
            FunctionName=lambda_name, Environment={"Variables": cleaned_env_vars}
        )

        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=lambda_name)

        # Additional wait to ensure environment variables are fully propagated
        time.sleep(5)

        logger.info("Lambda configuration restored")

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
        current_config = lambda_client.get_function_configuration(
            FunctionName=lambda_name
        )
        current_env_vars = (
            current_config.get("Environment", {}).get("Variables", {}).copy()
        )

        cleaned_env_vars = self._remove_test_variables(current_env_vars)

        # Only update if there were changes
        if cleaned_env_vars != current_env_vars:
            lambda_client.update_function_configuration(
                FunctionName=lambda_name, Environment={"Variables": cleaned_env_vars}
            )

            waiter = lambda_client.get_waiter("function_updated")
            waiter.wait(FunctionName=lambda_name)

            # Additional wait to ensure environment variables are fully propagated
            time.sleep(2)

            logger.info("Test variables removed from Lambda")
        else:
            logger.info("No test variables found in Lambda")
