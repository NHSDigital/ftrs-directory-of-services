from ftrs_common.utils.config import Settings
from pydantic import Field


class GpHealthCheckSettings(Settings):
    dynamodb_table_name: str = Field(alias="DYNAMODB_TABLE_NAME")
