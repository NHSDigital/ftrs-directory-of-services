from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    env: str = Field("local", alias="ENVIRONMENT")
    workspace: str | None = Field(None, alias="WORKSPACE")
    endpoint_url: str | None = Field(None, alias="ENDPOINT_URL")

    # AppConfig Feature Flags configuration
    appconfig_application_id: str | None = Field(None, alias="APPCONFIG_APPLICATION_ID")
    appconfig_environment_id: str | None = Field(None, alias="APPCONFIG_ENVIRONMENT_ID")
    appconfig_configuration_profile_id: str | None = Field(
        None, alias="APPCONFIG_CONFIGURATION_PROFILE_ID"
    )
