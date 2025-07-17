from pydantic import BaseModel, SecretStr

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
    def from_secretsmanager(cls) -> "DatabaseConfig":
        """
        Fetches the database credentials from AWS Secrets Manager and returns a DatabaseConfig instance.
        """
        db_credentials = get_secret(cls.source_db_credentials(), transform="json")
        return cls(**db_credentials)
