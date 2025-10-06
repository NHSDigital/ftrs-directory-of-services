import os
from typing import List

import boto3
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.utilities.parameters import SSMProvider
from dotenv import load_dotenv
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import UtilsLogBase

secretutils_logger = Logger.get(service="secretutils")
SSM_CLIENT = boto3.client("ssm")
provider = SSMProvider()


def get_secret(secret_name: str, transform: str | None = None) -> str:
    load_dotenv()
    environment = os.getenv("ENVIRONMENT")
    project_name = os.getenv("PROJECT_NAME")

    if not environment or not project_name:
        secretutils_logger.log(UtilsLogBase.UTILS_SECRET_001)
        raise ValueError

    return parameters.get_secret(
        name=f"/{project_name}/{environment}/{secret_name}", transform=transform
    )


def get_dms_workspaces() -> List[str]:
    ssm_path = os.environ.get("SQS_SSM_PATH")
    if not ssm_path:
        raise ValueError("Missing required environment variable: SQS_SSM_PATH")

    params = provider.get_multiple(
        ssm_path,
        recursive=True,
        decrypt=True,
        max_age=300,  # cache TTL = 300 seconds (5 minutes)
    )
    workspaces = list(params.values())
    return workspaces
