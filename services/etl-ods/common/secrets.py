import json
import os

import boto3
from botocore.exceptions import ClientError
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

secrets_logger = Logger.get(service="ods_secrets")


class SecretManager:
    @staticmethod
    def get_resource_prefix() -> str:
        project = os.environ.get("PROJECT_NAME")
        environment = os.environ.get("ENVIRONMENT")
        return f"{project}/{environment}"

    @staticmethod
    def get_secret_from_aws(secret_name: str) -> str:
        """Retrieve a secret from AWS Secrets Manager."""
        try:
            client = boto3.client(
                "secretsmanager", region_name=os.environ["AWS_REGION"]
            )
            response = client.get_secret_value(SecretId=secret_name)
            secret = response["SecretString"]

            try:
                secret_dict = json.loads(secret)
                return secret_dict.get("api_key", secret)
            except json.JSONDecodeError:
                return secret

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                secrets_logger.log(
                    OdsETLPipelineLogBase.ETL_COMMON_011,
                    secret_name=secret_name,
                    error_message=str(e),
                )
                err_msg = "Secret not found"
                raise KeyError(err_msg)
            raise
        except json.JSONDecodeError as json_err:
            secrets_logger.log(
                OdsETLPipelineLogBase.ETL_COMMON_012, error_message=str(json_err)
            )
            raise

    @classmethod
    def get_mock_api_key_from_secrets(cls) -> str:
        """Retrieve mock API key from AWS Secrets Manager for testing scenarios."""
        try:
            project = os.environ.get("PROJECT_NAME")
            environment = os.environ.get("ENVIRONMENT")
            workspace = os.environ.get("WORKSPACE", "")

            project_prefix = f"{project}-{environment}"
            workspace_suffix = f"-{workspace}" if workspace else ""
            secret_name = f"/{project_prefix}/mock-api/api-key{workspace_suffix}"

            return cls.get_secret_from_aws(secret_name)

        except KeyError as e:
            err_msg = f"Mock API key secret not found: {e}"
            secrets_logger.log(
                OdsETLPipelineLogBase.ETL_COMMON_011,
                secret_name=secret_name,
                error_message=err_msg,
            )
            raise KeyError(err_msg)
        except Exception as e:
            secrets_logger.log(
                OdsETLPipelineLogBase.ETL_COMMON_012,
                error_message=f"Failed to retrieve mock API key: {e}",
            )
            raise

    @classmethod
    def get_ods_terminology_api_key(cls) -> str:
        """Get ODS terminology API key for the current environment."""
        env = os.environ.get("ENVIRONMENT")

        if env == "local":
            secrets_logger.log(OdsETLPipelineLogBase.ETL_COMMON_021)
            return os.environ.get(
                "LOCAL_ODS_TERMINOLOGY_API_KEY", os.environ.get("LOCAL_API_KEY", "")
            )

        try:
            secrets_logger.log(OdsETLPipelineLogBase.ETL_COMMON_022)
            resource_prefix = cls.get_resource_prefix()
            secret_name = f"/{resource_prefix}/ods-terminology-api-key"
            return cls.get_secret_from_aws(secret_name)

        except KeyError:
            raise
        except Exception as e:
            secrets_logger.log(
                OdsETLPipelineLogBase.ETL_COMMON_012, error_message=str(e)
            )
            raise
