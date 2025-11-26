import pytest
import boto3
import os
from typing import Generator, Tuple

from loguru import logger

from utilities.common.resource_name import get_resource_name
from utilities.infra.apigateway_vtl_mock import APIGatewayVTLMockManager
from utilities.infra.lambda_util import LambdaWrapper
from utilities.ods.lambda_config_manager import LambdaConfigManager
from utilities.common.constants import ENV_PROJECT_NAME

class VTLMockSetup:
    """Helper class for VTL mock setup operations."""
    @staticmethod
    def create_api_name(workspace: str, env: str) -> str:
        """Create API name following naming conventions."""
        api_base_name = "ods-terminology-api-mock"
        workspace_suffix = f"-{workspace}" if workspace else ""
        return f"{api_base_name}{workspace_suffix}.{env}"
    @staticmethod
    def validate_environment(env: str) -> None:
        """Ensure VTL mock is not run in production."""
        if env.lower() in ["prod", "production"]:
            pytest.skip("VTL mock API Gateway is not allowed in production environment")
    @staticmethod
    def cleanup_session_secret(env: str) -> None:
        """Clean up the mock API key secret at session end."""
        try:
            project = os.environ.get(ENV_PROJECT_NAME, "ftrs-dos")
            resource_prefix = f"{project}/{env}"
            secret_name = f"/{resource_prefix}/mock-api-gateway-key"
            aws_region = os.environ.get("AWS_REGION", "eu-west-2")
            secrets_client = boto3.client("secretsmanager", region_name=aws_region)

            # Delete the secret
            try:
                secrets_client.delete_secret(
                    SecretId=secret_name,
                    ForceDeleteWithoutRecovery=True  # Immediate deletion for test secrets
                )
                logger.info(f"Cleaned up session mock API key secret: {secret_name}")
            except secrets_client.exceptions.InvalidRequestException as e:
                if "currently marked deleted" in str(e) or "scheduled for deletion" in str(e):
                    logger.info(f"Secret {secret_name} already scheduled for deletion")
                else:
                    logger.warning(f"Error deleting secret: {e}")
            except secrets_client.exceptions.ResourceNotFoundException:
                logger.info(f"Secret {secret_name} not found (already deleted)")

        except Exception as e:
            logger.warning(f"Failed to cleanup session secret (non-critical): {e}")


@pytest.fixture(scope="session")
def mock_api_vtl_session(
    workspace: str,
    env: str
) -> Generator[APIGatewayVTLMockManager, None, None]:
    """
    Session-scoped VTL mock API Gateway for ODS API mocking.
    Creates one shared mock API and secret per test session.
    Secret persists for entire test session and is cleaned up at the end.

    Security: Only allowed in dev/test environments.
    Creates temporary API Gateway with API key authentication.
    """
    VTLMockSetup.validate_environment(env)

    api_name = VTLMockSetup.create_api_name(workspace, env)
    logger.info(f"Creating VTL mock API Gateway: {api_name}")

    manager = APIGatewayVTLMockManager(region_name="eu-west-2")

    try:
        result = manager.create_and_deploy_mock_api(
            api_name=api_name,
            resource_path="organisation-data-terminology-api/fhir/Organization",
            api_key_required=True
        )

        logger.info(f"VTL mock API ready: {api_name}")
        logger.info(f"Base URL: {result['endpoint_url']}")

        yield manager

    except Exception as e:
        logger.error(f"Failed to create VTL mock API: {e}")
        raise
    finally:
        logger.info(f"Cleaning up VTL API Gateway: {api_name}")
        try:
            # Clean up the session secret first
            VTLMockSetup.cleanup_session_secret(env)

            if manager and manager.api_id:
                manager.cleanup()
                logger.info("VTL mock API cleanup completed successfully")
            else:
                logger.info("No VTL mock API to clean up")
        except Exception as cleanup_error:
            logger.error(f"VTL mock API cleanup failed: {cleanup_error}")
            logger.warning("Manual cleanup may be required - check AWS console")


@pytest.fixture
def lambda_with_vtl_mock(
    mock_api_vtl_session: APIGatewayVTLMockManager,
    aws_lambda_client: LambdaWrapper,
    project: str,
    workspace: str,
    env: str,
) -> Generator[Tuple[str, APIGatewayVTLMockManager], None, None]:
    """
    Configure Lambda to use VTL mock API Gateway.
    Shares the same mock API and secret across all tests in the session.
    """
    lambda_name = get_resource_name(
        project, workspace, env, "etl-ods-processor", "lambda"
    )

    config_manager = LambdaConfigManager(aws_lambda_client)

    try:
        # Configure Lambda for VTL mock
        config_manager.configure_for_vtl_mock(lambda_name, mock_api_vtl_session)

        yield lambda_name, mock_api_vtl_session

    finally:
        # Always restore original configuration
        try:
            config_manager.restore_original_configuration(lambda_name)
            logger.info("Lambda configuration restored")
        except Exception as restore_error:
            logger.error(f"Failed to restore Lambda configuration: {restore_error}")
            logger.warning("Lambda environment may need manual restoration")
