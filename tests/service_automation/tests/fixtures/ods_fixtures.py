from typing import Generator, Tuple

import pytest
from loguru import logger
from utilities.common.resource_name import get_resource_name
from utilities.infra.apigateway_ods_mock import ODSMockClient
from utilities.infra.lambda_util import LambdaWrapper
from utilities.ods.lambda_config_manager import LambdaConfigManager


@pytest.fixture(scope="module")
def lambda_with_ods_mock(
    aws_lambda_client: LambdaWrapper,
    project: str,
    workspace: str,
    env: str,
) -> Generator[Tuple[str, ODSMockClient], None, None]:
    """
    Configure Lambda to use ODS mock API Gateway.
    Retrieves ODS mock details from Terraform-deployed infrastructure.
    """
    logger.info(f"Setting up Lambda with ODS mock in environment: {env}")

    mock_client = ODSMockClient(region_name="eu-west-2")

    lambda_name = get_resource_name(
        project, workspace, env, "etl-ods-processor", "lambda"
    )

    config_manager = LambdaConfigManager(aws_lambda_client)

    try:
        config_manager.configure_for_ods_mock(lambda_name, mock_client)

        yield lambda_name, mock_client

    finally:
        try:
            config_manager.restore_original_configuration(lambda_name)
            logger.info("Lambda configuration restored")
        except Exception as restore_error:
            logger.error(f"Failed to restore Lambda configuration: {restore_error}")
            logger.warning("Lambda environment may need manual restoration")
