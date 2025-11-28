from pydantic import SecretStr
from pytest_mock import MockerFixture

from pipeline.utils.config import DatabaseConfig

POSTGRES_DEFAULT_PORT = 5432


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

    assert db_config.source_db_credentials() == "replica-rds-credentials"


def test_db_config_from_uri() -> None:
    """
    Test that the DatabaseConfig class can be constructed from a URI.
    """
    db_config = DatabaseConfig.from_uri(
        "postgresql://username:password@host:5432/dbname"
    )

    assert db_config.host == "host"
    assert db_config.port == POSTGRES_DEFAULT_PORT
    assert db_config.username == "username"
    assert db_config.password == SecretStr("password")
    assert db_config.dbname == "dbname"


def test_db_config_from_secretsmanager(mocker: MockerFixture) -> None:
    """
    Test that the DatabaseConfig class can fetch credentials from AWS Secrets Manager.
    """
    mock_get_secret = mocker.patch(
        "pipeline.utils.config.get_secret",
        return_value={
            "host": "host",
            "port": 5432,
            "username": "username",
            "password": "password",
            "dbname": "dbname",
        },
    )

    db_config = DatabaseConfig.from_secretsmanager()

    mock_get_secret.assert_called_once_with("replica-rds-credentials", transform="json")

    assert db_config.host == "host"
    assert db_config.port == POSTGRES_DEFAULT_PORT
    assert db_config.username == "username"
    assert db_config.password == SecretStr("password")
    assert db_config.dbname == "dbname"
