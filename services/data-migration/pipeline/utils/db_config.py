from pydantic import BaseModel, SecretStr


class DatabaseConfig(BaseModel):
    """
    Base model to hold database connection details.
    """

    host: str
    port: int
    user: str
    password: SecretStr
    dbname: str

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.dbname}"

    def __str__(self) -> str:
        """
        Returns a string representation of the database connection details.
        """
        return (
            f"DatabaseConfig(host={self.host}, port={self.port}, user={self.user}, "
            f"password=****, dbname={self.dbname})"
        )

    @property
    def source_db_credentials(self) -> str:
        """
        Returns the source database credentials secret name
        """
        return "source-rds-credentials"
