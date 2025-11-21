"""Database helper utilities for testing."""
from sqlalchemy import text
from sqlmodel import Session
import pytest


def verify_service_exists(
    session: Session,
    service_id: int
) -> tuple[int, int, str, int]:
    """
    Verify service exists in database and return key attributes.

    Args:
        session: Database session
        service_id: Service ID to verify

    Returns:
        Tuple of (id, typeid, odscode, statusid)

    Raises:
        pytest.fail: If service not found
    """
    stmt = text(
        "SELECT id, typeid, odscode, statusid FROM pathwaysdos.services "
        "WHERE id = :id"
    )
    result = session.exec(stmt.bindparams(id=service_id)).fetchone()

    if not result:
        pytest.fail(f"Service {service_id} not found in database")

    return result


def delete_service_if_exists(session: Session, service_id: int) -> None:
    """
    Delete service from database if it exists (test isolation).

    Args:
        session: Database session
        service_id: Service ID to delete
    """
    stmt = text("DELETE FROM pathwaysdos.services WHERE id = :id")
    session.exec(stmt.bindparams(id=service_id))
