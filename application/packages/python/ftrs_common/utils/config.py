from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    env: str = Field("local", alias="ENVIRONMENT")
    workspace: str | None = Field(None, alias="WORKSPACE")
    endpoint_url: str | None = Field(None, alias="ENDPOINT_URL")
