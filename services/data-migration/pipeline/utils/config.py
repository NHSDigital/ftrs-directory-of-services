from typing import Annotated
from urllib.parse import urlparse

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from pipeline.utils.secret_utils import get_secret


class DatabaseConfig(BaseModel):
    """
    Base model to hold database connection details.
    """

    host: str
    port: int
    username: str
    password: SecretStr
    dbname: str

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.dbname}"

    def __str__(self) -> str:
        """
        Returns a string representation of the database connection details.
        """
        return (
            f"DatabaseConfig(host={self.host}, port={self.port}, username={self.username}, "
            f"password=****, dbname={self.dbname})"
        )

    @classmethod
    def source_db_credentials(cls) -> str:
        return "source-rds-credentials"

    @classmethod
    def from_uri(cls, db_uri: str) -> "DatabaseConfig":
        """
        Parses a database URI and returns a DatabaseConfig instance.
        """
        parsed_uri = urlparse(db_uri)
        return cls(
            host=parsed_uri.hostname,
            port=parsed_uri.port,
            username=parsed_uri.username,
            password=SecretStr(parsed_uri.password),
            dbname=parsed_uri.path.lstrip("/"),
        )

    @classmethod
    def from_secretsmanager(cls) -> "DatabaseConfig":
        """
        Fetches the database credentials from AWS Secrets Manager and returns a DatabaseConfig instance.
        """
        db_credentials = get_secret(cls.source_db_credentials(), transform="json")
        return cls(**db_credentials)


class DataMigrationConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_config: Annotated[
        DatabaseConfig, Field(..., default_factory=DatabaseConfig.from_secretsmanager)
    ]
    env: Annotated[str, Field("local", alias="ENVIRONMENT")]
    workspace: Annotated[str | None, Field(None, alias="WORKSPACE")]
    dynamodb_endpoint: Annotated[str | None, Field(None, alias="ENDPOINT_URL")]
