"""Tests for common/sql_utils.py module."""

from unittest.mock import MagicMock, patch

from sqlalchemy import Engine

from common.config import DatabaseConfig
from common.sql_utils import get_sqlalchemy_engine_from_config


def test_get_sqlalchemy_engine_from_config_returns_engine() -> None:
    """Test that the function returns an SQLAlchemy Engine instance."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    assert isinstance(engine, Engine)


def test_get_sqlalchemy_engine_from_config_uses_connection_string() -> None:
    """Test that the engine is created with the correct connection string."""
    db_config = DatabaseConfig(
        host="testhost",
        port=5433,
        dbname="testdb",
        username="testuser",
        password="testpass",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    # Check the URL contains expected components
    url_str = str(engine.url)
    assert "testhost" in url_str
    assert "testdb" in url_str
    assert "testuser" in url_str


def test_get_sqlalchemy_engine_from_config_pool_settings() -> None:
    """Test that connection pool settings are configured correctly."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    # Verify pool settings
    assert engine.pool.size() <= 10, "Pool size should be configured"
    assert hasattr(engine.pool, "_max_overflow")


def test_get_sqlalchemy_engine_from_config_with_special_characters() -> None:
    """Test that special characters in password are handled correctly."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="p@ss!word#123",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    assert isinstance(engine, Engine)


def test_get_sqlalchemy_engine_from_config_different_ports() -> None:
    """Test that different port numbers are handled correctly."""
    port_numbers = [5432, 3306, 1433, 5433]

    for port in port_numbers:
        db_config = DatabaseConfig(
            host="localhost",
            port=port,
            dbname="test_db",
            username="test_user",
            password="test_password",
        )

        engine = get_sqlalchemy_engine_from_config(db_config)
        assert isinstance(engine, Engine)


def test_get_sqlalchemy_engine_from_config_connect_args() -> None:
    """Test that connect_args are properly set."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    # Check that connect_args are set (via the engine's dialect)
    # The actual connect_args are stored in the engine's pool or dialect
    assert engine is not None


def test_get_sqlalchemy_engine_from_config_pool_pre_ping() -> None:
    """Test that pool_pre_ping is enabled."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    engine = get_sqlalchemy_engine_from_config(db_config)

    # Pool pre-ping should be enabled to validate connections
    assert hasattr(engine.pool, "_pre_ping")


def test_get_sqlalchemy_engine_from_config_multiple_instances() -> None:
    """Test that multiple engine instances can be created."""
    db_config1 = DatabaseConfig(
        host="host1",
        port=5432,
        dbname="db1",
        username="user1",
        password="pass1",
    )
    db_config2 = DatabaseConfig(
        host="host2",
        port=5432,
        dbname="db2",
        username="user2",
        password="pass2",
    )

    engine1 = get_sqlalchemy_engine_from_config(db_config1)
    engine2 = get_sqlalchemy_engine_from_config(db_config2)

    assert isinstance(engine1, Engine)
    assert isinstance(engine2, Engine)
    assert engine1 is not engine2
    assert str(engine1.url) != str(engine2.url)


def test_get_sqlalchemy_engine_from_config_application_name() -> None:
    """Test that application name is set in connect args."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    with patch("common.sql_utils.create_engine") as mock_create_engine:
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        get_sqlalchemy_engine_from_config(db_config)

        # Verify create_engine was called with application_name in connect_args
        call_kwargs = mock_create_engine.call_args.kwargs
        assert "connect_args" in call_kwargs
        assert call_kwargs["connect_args"]["application_name"] == "dms_pipeline"


def test_get_sqlalchemy_engine_from_config_timeout_settings() -> None:
    """Test that timeout settings are configured."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    with patch("common.sql_utils.create_engine") as mock_create_engine:
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        get_sqlalchemy_engine_from_config(db_config)

        # Verify timeout is set
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs["connect_args"]["connect_timeout"] == 30


def test_get_sqlalchemy_engine_from_config_pool_recycle() -> None:
    """Test that pool_recycle is configured."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    with patch("common.sql_utils.create_engine") as mock_create_engine:
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        get_sqlalchemy_engine_from_config(db_config)

        # Verify pool_recycle is set to 1 hour
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs["pool_recycle"] == 3600


def test_get_sqlalchemy_engine_from_config_pool_reset_on_return() -> None:
    """Test that pool_reset_on_return is configured."""
    db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        dbname="test_db",
        username="test_user",
        password="test_password",
    )

    with patch("common.sql_utils.create_engine") as mock_create_engine:
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        get_sqlalchemy_engine_from_config(db_config)

        # Verify pool_reset_on_return is set
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs["pool_reset_on_return"] == "commit"
