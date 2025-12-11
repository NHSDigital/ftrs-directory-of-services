from typing import Annotated, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.config import DatabaseConfig


class QueuePopulatorConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
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
    service_id: Annotated[Optional[int], Field(default=None, description="Service ID")]
    record_id: Annotated[Optional[int], Field(default=None, description="Record ID")]
    full_sync: Annotated[bool, Field(default=True, description="Perform full sync")]
    table_name: Annotated[str, Field(default="services", description="Table name")]
