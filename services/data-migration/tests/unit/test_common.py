from sqlalchemy.engine import Engine

from pipeline.common import get_db_engine


def test_get_db_engine_creates_engine() -> None:
    """
    Test that get_db_engine creates an engine with the correct URI
    """
    engine = get_db_engine("sqlite:///:memory:")

    assert engine is not None
    assert engine.url.drivername == "sqlite"
    assert isinstance(engine, Engine)


def test_get_db_engine_returns_same_engine() -> None:
    """
    Test that get_db_engine returns the same engine for the same URI
    """
    engine1 = get_db_engine("sqlite:///:memory:")
    engine2 = get_db_engine("sqlite:///:memory:")

    assert engine1 is engine2


def test_get_db_engine_returns_different_engines() -> None:
    """
    Test that get_db_engine returns different engines for different URIs
    """
    engine1 = get_db_engine("sqlite:///:memory:")
    engine2 = get_db_engine("sqlite:///different.db")

    assert engine1 is not engine2
    assert engine1.url.drivername == "sqlite"
    assert engine2.url.drivername == "sqlite"
