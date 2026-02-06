"""Integration tests for Organisation CRUD operations.

These tests run against a real DynamoDB instance using LocalStack testcontainers.
They verify actual database operations, serialization, and query patterns.

Run with: pytest -m integration tests/integration/test_organisation_integration.py
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from ftrs_data_layer.domain import Organisation, Telecom
from ftrs_data_layer.domain.enums import OrganisationType, TelecomType


@pytest.mark.integration
class TestOrganisationRepositoryIntegration:
    """Integration tests for Organisation repository operations."""

    def test_create_and_get_organisation(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should create an organisation and retrieve it by ID."""
        org_id = uuid4()
        org = Organisation(
            id=org_id,
            identifier_ODS_ODSCode="TEST001",
            active=True,
            name="Test Organisation",
            type=OrganisationType.GP_PRACTICE,
            telecom=[
                Telecom(
                    type=TelecomType.PHONE,
                    value="0300 311 22 33",
                    isPublic=True,
                )
            ],
            endpoints=[],
            createdBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            createdTime=datetime.now(UTC),
            lastUpdatedBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            lastUpdated=datetime.now(UTC),
        )

        # Create
        organisation_repository.create(org)

        # Retrieve
        retrieved = organisation_repository.get(org_id)

        assert retrieved is not None
        assert retrieved.id == org_id
        assert retrieved.identifier_ODS_ODSCode == "TEST001"
        assert retrieved.name == "Test Organisation"
        assert retrieved.active is True
        assert len(retrieved.telecom) == 1
        assert retrieved.telecom[0].value == "0300 311 22 33"

    def test_update_organisation(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should update an existing organisation."""
        org_id = uuid4()
        org = Organisation(
            id=org_id,
            identifier_ODS_ODSCode="TEST002",
            active=True,
            name="Original Name",
            type=OrganisationType.GP_PRACTICE,
            telecom=[],
            endpoints=[],
            createdBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            createdTime=datetime.now(UTC),
            lastUpdatedBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            lastUpdated=datetime.now(UTC),
        )

        organisation_repository.create(org)

        # Update
        org.name = "Updated Name"
        org.active = False
        organisation_repository.update(org_id, org)

        # Verify update
        retrieved = organisation_repository.get(org_id)
        assert retrieved.name == "Updated Name"
        assert retrieved.active is False

    def test_delete_organisation(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should delete an organisation."""
        org_id = uuid4()
        org = Organisation(
            id=org_id,
            identifier_ODS_ODSCode="TEST003",
            active=True,
            name="To Be Deleted",
            type=OrganisationType.GP_PRACTICE,
            telecom=[],
            endpoints=[],
            createdBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            createdTime=datetime.now(UTC),
            lastUpdatedBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            lastUpdated=datetime.now(UTC),
        )

        organisation_repository.create(org)

        # Verify exists
        assert organisation_repository.get(org_id) is not None

        # Delete
        organisation_repository.delete(org_id)

        # Verify deleted
        assert organisation_repository.get(org_id) is None

    def test_get_nonexistent_organisation_returns_none(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should return None for non-existent organisation."""
        result = organisation_repository.get(uuid4())
        assert result is None

    def test_upsert_creates_new_organisation(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Upsert should create organisation if it doesn't exist."""
        org_id = uuid4()
        org = Organisation(
            id=org_id,
            identifier_ODS_ODSCode="TEST004",
            active=True,
            name="Upserted Organisation",
            type=OrganisationType.GP_PRACTICE,
            telecom=[],
            endpoints=[],
            createdBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            createdTime=datetime.now(UTC),
            lastUpdatedBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            lastUpdated=datetime.now(UTC),
        )

        # Upsert (create)
        organisation_repository.upsert(org)

        # Verify created
        retrieved = organisation_repository.get(org_id)
        assert retrieved is not None
        assert retrieved.name == "Upserted Organisation"

    def test_upsert_updates_existing_organisation(
        self,
        organisation_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Upsert should update organisation if it exists."""
        org_id = uuid4()
        org = Organisation(
            id=org_id,
            identifier_ODS_ODSCode="TEST005",
            active=True,
            name="Original",
            type=OrganisationType.GP_PRACTICE,
            telecom=[],
            endpoints=[],
            createdBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            createdTime=datetime.now(UTC),
            lastUpdatedBy={
                "type": "user",
                "value": "test-user",
                "display": "Test User",
            },
            lastUpdated=datetime.now(UTC),
        )

        organisation_repository.create(org)

        # Upsert (update)
        org.name = "Upserted Update"
        organisation_repository.upsert(org)

        # Verify updated
        retrieved = organisation_repository.get(org_id)
        assert retrieved.name == "Upserted Update"
