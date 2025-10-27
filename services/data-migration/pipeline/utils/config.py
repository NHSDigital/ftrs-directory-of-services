import logging
import os
from typing import Annotated, Tuple

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.config import DatabaseConfig
from common.secret_utils import get_secret


class DataMigrationConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_config: Annotated[
        DatabaseConfig, Field(..., default_factory=DatabaseConfig.from_secretsmanager)
    ]
    env: Annotated[str, Field("local", alias="ENVIRONMENT")]
    workspace: Annotated[str | None, Field(None, alias="WORKSPACE")]
    dynamodb_endpoint: Annotated[str | None, Field(None, alias="ENDPOINT_URL")]


class QueuePopulatorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    db_config: Annotated[
        DatabaseConfig, Field(..., default_factory=DatabaseConfig.from_secretsmanager)
    ]
    sqs_queue_url: Annotated[str, Field(..., alias="SQS_QUEUE_URL")]
    type_ids: Annotated[
        list[int] | None,
        Field(default=None, description="List of type IDs to filter services by"),
    ]
    status_ids: Annotated[
        list[int] | None,
        Field(default=None, description="List of status IDs to filter services by"),
    ]


class DmsDatabaseConfig:
    """Handles configuration and environment variables for the DMS pipeline."""

    def __init__(self) -> None:
        self.logger = logging.getLogger()
        self._load_environment_variables()

    def _load_environment_variables(self) -> None:
        """Load required environment variables with error handling."""
        try:
            self.target_rds_details = os.environ["TARGET_RDS_DETAILS"]
            self.dms_user_details = os.environ["DMS_USER_DETAILS"]
            self.trigger_lambda_arn = os.environ["TRIGGER_LAMBDA_ARN"]
        except KeyError:
            self.logger.exception("Missing required environment variable")
            raise

    def get_values(self) -> Tuple[str, str, str]:
        """Return the config values as a tuple."""
        return (
            self.target_rds_details,
            self.dms_user_details,
            self.trigger_lambda_arn,
        )

    def get_target_rds_details(self) -> DatabaseConfig:
        """Get target RDS details using the existing DatabaseConfig infrastructure."""
        target_rds_details_secret = get_secret(
            self.target_rds_details, transform="json"
        )
        return DatabaseConfig(**target_rds_details_secret)

    def get_dms_user_details(self) -> tuple[str, SecretStr]:
        """Get DMS user details using existing secret retrieval methods."""
        rds_password = get_secret(self.dms_user_details)
        rds_username = "dms_user"
        return rds_username, rds_password
