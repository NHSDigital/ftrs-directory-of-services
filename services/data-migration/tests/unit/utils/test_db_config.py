from pipeline.utils.db_config import DatabaseConfig


def test_db_config_successful() -> None:
    """
    Test that the DatabaseConfig class correctly constructs the connection string,
    returns accurate database details, generates the correct URI,
    and formats its string representation properly.
    """
    db_config = DatabaseConfig(
        host="host",
        port="port",
        user="username",
        password="password",
        db_name="dbname",
    )

    # Test initialise_config
    assert (
        db_config.connection_string == "postgresql://username:password@host:port/dbname"
    )

    # Test get_db_details
    db_details = db_config.get_db_details()
    assert db_details == {
        "host": "host",
        "port": "port",
        "user": "username",
        "password": "password",
        "db_name": "dbname",
    }

    # Test get_db_uri
    db_uri = db_config.get_db_uri()
    assert db_uri == "postgresql://username:password@host:port/dbname"

    # Test db_config_to_string
    assert (
        str(db_config)
        == "DatabaseConfig(host=host, port=port, user=username, password=****, db_name=dbname)"
    )
