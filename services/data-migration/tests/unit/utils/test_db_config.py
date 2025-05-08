from pipeline.utils.db_config import DatabaseConfig


def test_db_config_successful() -> None:
    """
    Test that the DatabaseConfig class correctly constructs the connection string,
    returns accurate database details, generates the correct URI,
    and formats its string representation properly.
    """
    db_config = DatabaseConfig(
        host="host",
        port=5432,
        username="username",
        password="password",
        dbname="dbname",
    )

    assert (
        db_config.connection_string == "postgresql://username:password@host:5432/dbname"
    )

    assert (
        str(db_config)
        == "DatabaseConfig(host=host, port=5432, username=username, password=****, dbname=dbname)"
    )

    assert db_config.source_db_credentials() == "source-rds-credentials"
