import json
import os

import boto3
from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

secrets_logger = Logger.get(service="ods_secrets")


def get_resource_prefix() -> str:
    project = os.environ.get("PROJECT_NAME")
    environment = os.environ.get("ENVIRONMENT")
    return f"{project}/{environment}"


def get_ods_terminology_api_key() -> str:
    env = os.environ.get("ENVIRONMENT")

    if env == "local":
        secrets_logger.log(OdsETLPipelineLogBase.ETL_UTILS_005)
        return os.environ.get(
            "LOCAL_ODS_TERMINOLOGY_API_KEY", os.environ.get("LOCAL_API_KEY", "")
        )

    try:
        resource_prefix = get_resource_prefix()
        secret_name = f"/{resource_prefix}/ods-terminology-api-key"

        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]

        secret_dict = json.loads(secret)
        return secret_dict.get("api_key", secret)

    except json.JSONDecodeError as json_err:
        secrets_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(json_err)
        )
        raise
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            secrets_logger.log(
                OdsETLPipelineLogBase.ETL_UTILS_006,
                secret_name=secret_name,
                error_message=str(e),
            )
        raise
