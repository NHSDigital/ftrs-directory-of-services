from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    env: str = Field(..., alias="ENVIRONMENT")
    workspace: str | None = Field(None, alias="WORKSPACE")
    endpoint_url: str | None = Field(None, alias="ENDPOINT_URL")
