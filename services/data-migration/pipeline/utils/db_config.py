class DatabaseConfig:
    """
    Class to hold database connection details.
    """

    SOURCE_DB_CREDENTIALS = "source-rds-credentials"

    def __init__(
        self, host: str, port: str, user: str, password: str, db_name: str
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection_string = (
            f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        )

    def __str__(self) -> str:
        """
        Returns a string representation of the database connection details.
        """
        return (
            f"DatabaseConfig(host={self.host}, port={self.port}, user={self.user}, "
            f"password=****, db_name={self.db_name})"
        )

    def get_db_details(self) -> dict:
        """
        Returns the database connection details.
        """
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "db_name": self.db_name,
        }

    def get_db_uri(self) -> str:
        """
        Returns the database connection URI.
        """
        return self.connection_string
