import os

import boto3
from aws_lambda_powertools.utilities import parameters
from dotenv import load_dotenv
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import UtilsLogBase

secretutils_logger = Logger.get(service="secretutils")
SSM_CLIENT = boto3.client("ssm")


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


def get_dms_workspaces() -> list[str]:
    paginator = SSM_CLIENT.get_paginator("get_parameters_by_path")
    workspaces = []

    for page in paginator.paginate(
        Path=os.environ.get("SQS_SSM_PATH"), Recursive=True, WithDecryption=True
    ):
        workspaces.extend([param["Value"] for param in page["Parameters"]])
    return workspaces
