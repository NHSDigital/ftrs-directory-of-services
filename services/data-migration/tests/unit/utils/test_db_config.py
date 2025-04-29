from pipeline.utils.db_config import DatabaseConfig


def test_initialise_config() -> None:
    db_config = DatabaseConfig(
        host="host",
        port="port",
        user="username",
        password="password",
        db_name="dbname",
    )

    assert (
        db_config.connection_string == "postgresql://username:password@host:port/dbname"
    )


def test_get_db_details() -> None:
    db_config = DatabaseConfig(
        host="host",
        port="host",
        user="host",
        password="host",
        db_name="dbname",
    )

    db_details = db_config.get_db_details()

    assert db_details == {
        "host": "host",
        "port": "host",
        "user": "host",
        "password": "host",
        "db_name": "dbname",
    }


def test_get_db_uri() -> None:
    db_config = DatabaseConfig(
        host="host",
        port="port",
        user="username",
        password="password",
        db_name="dbname",
    )

    db_uri = db_config.get_db_uri()

    assert db_uri == "postgresql://username:password@host:port/dbname"


def test_db_config_to_string() -> None:
    db_config = DatabaseConfig(
        host="host",
        port="port",
        user="username",
        password="password",
        db_name="dbname",
    )

    assert (
        str(db_config)
        == "DatabaseConfig(host=host, port=port, user=username, password=****, db_name=dbname)"
    )
