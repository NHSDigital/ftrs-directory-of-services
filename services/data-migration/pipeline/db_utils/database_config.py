# {"dbname":"data_migration","host":"NOT_SET","password":"NOT_SET","port":"5432","username":"NOT_SET"}


class DatabaseConfig:
    # Constants
    SOURCE_DB_CREDENTIALS = "source-rds-credentials"

    """
    Class to hold database connection details.
    """

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

    def getDBdetails(self) -> dict:
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

    def getDBuri(self) -> str:
        """
        Returns the database connection URI.
        """
        return self.connection_string
