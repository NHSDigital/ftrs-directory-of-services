from pydantic import BaseModel, SecretStr


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
