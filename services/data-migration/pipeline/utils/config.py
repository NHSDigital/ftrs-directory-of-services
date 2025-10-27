from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.config import DatabaseConfig


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
