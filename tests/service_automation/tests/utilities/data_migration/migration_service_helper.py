"""Helper utilities for service creation and database operations."""
from typing import Any, Dict, List

import pytest
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session

from utilities.common.constants import REQUIRED_SERVICE_FIELDS, SERVICES_TABLE
from utilities.common.db_helper import delete_service_if_exists, verify_service_exists
from utilities.common.gherkin_helper import parse_gherkin_table


def validate_service_attributes(attributes: Dict[str, Any]) -> None:
    """Validate that service attributes contain all required fields."""
    missing = [f for f in REQUIRED_SERVICE_FIELDS if f not in attributes]
    if missing:
        pytest.fail(
            f"Missing required fields: {', '.join(missing)}\n"
            f"Required: {', '.join(REQUIRED_SERVICE_FIELDS)}\n"
            f"Provided: {', '.join(attributes.keys())}"
        )


def create_service_in_database(
    session: Session,
    attributes: Dict[str, Any],
) -> None:
    """Create service in database with given attributes."""
    service_id = attributes["id"]

    try:
        delete_service_if_exists(session, service_id)

        columns = list(attributes.keys())
        placeholders = [f":{col}" for col in columns]

        insert_sql = text(
            f"""
            INSERT INTO {SERVICES_TABLE} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            """
        )

        session.exec(insert_sql.bindparams(**attributes))
        session.commit()

        result = verify_service_exists(session, service_id)

        if not result:
            pytest.fail(f"Failed to verify inserted service with ID {service_id}")

        logger.info(
            "Created test service",
            extra={"service_id": service_id, "type_id": result[1]},
        )

    except Exception as e:
        session.rollback()
        pytest.fail(f"Database operation failed: {e}")


def parse_and_create_service(
    session: Session,
    migration_context: Dict[str, Any],
    entity_type: str,
    entity_name: str,
    datatable: List[List[str]],
) -> Dict[str, Any]:
    """Parse Gherkin table and create service in database."""
    attributes = parse_gherkin_table(datatable)
    validate_service_attributes(attributes)

    service_id = attributes["id"]
    migration_context["service_data"] = attributes
    migration_context["service_name"] = entity_name
    migration_context["service_id"] = service_id

    create_service_in_database(session, attributes)

    return attributes
