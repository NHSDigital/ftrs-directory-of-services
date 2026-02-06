"""Integration tests for Location CRUD operations.

These tests run against a real DynamoDB instance using LocalStack testcontainers.
They verify actual database operations, serialization, and query patterns.

Run with: pytest -m integration tests/integration/test_location_integration.py
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from ftrs_data_layer.domain import Location
from ftrs_data_layer.domain.location import Address, PositionGCS


@pytest.mark.integration
class TestLocationRepositoryIntegration:
    """Integration tests for Location repository operations."""

    def test_create_and_get_location(
        self,
        location_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should create a location and retrieve it by ID."""
        loc_id = uuid4()
        location = Location(
            id=loc_id,
            active=True,
            name="Test Location",
            address=Address(
                line1="123 Test Street",
                line2="Suite 100",
                county="West Yorkshire",
                town="Leeds",
                postcode="LS1 1AA",
            ),
            positionGCS=PositionGCS(
                latitude=Decimal("53.7997"),
                longitude=Decimal("-1.5492"),
            ),
            managingOrganisation=uuid4(),
            primaryAddress=True,
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
        location_repository.create(location)

        # Retrieve
        retrieved = location_repository.get(loc_id)

        assert retrieved is not None
        assert retrieved.id == loc_id
        assert retrieved.name == "Test Location"
        assert retrieved.address.town == "Leeds"
        assert retrieved.address.postcode == "LS1 1AA"

    def test_update_location(
        self,
        location_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should update an existing location."""
        loc_id = uuid4()
        location = Location(
            id=loc_id,
            active=True,
            name="Original Location",
            address=Address(
                line1="456 Original Street",
                line2=None,
                county="Greater Manchester",
                town="Manchester",
                postcode="M1 1AA",
            ),
            managingOrganisation=uuid4(),
            primaryAddress=True,
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

        location_repository.create(location)

        # Update
        location.name = "Updated Location"
        location.address.town = "Birmingham"
        location_repository.update(loc_id, location)

        # Verify update
        retrieved = location_repository.get(loc_id)
        assert retrieved.name == "Updated Location"
        assert retrieved.address.town == "Birmingham"

    def test_delete_location(
        self,
        location_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should delete a location."""
        loc_id = uuid4()
        location = Location(
            id=loc_id,
            active=True,
            name="To Be Deleted",
            address=Address(
                line1="789 Delete Street",
                line2=None,
                county="Greater London",
                town="London",
                postcode="SW1A 1AA",
            ),
            managingOrganisation=uuid4(),
            primaryAddress=True,
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

        location_repository.create(location)

        # Verify exists
        assert location_repository.get(loc_id) is not None

        # Delete
        location_repository.delete(loc_id)

        # Verify deleted
        assert location_repository.get(loc_id) is None

    def test_location_with_position_coordinates(
        self,
        location_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should correctly store and retrieve decimal coordinates."""
        loc_id = uuid4()
        latitude = Decimal("51.5074")
        longitude = Decimal("-0.1278")

        location = Location(
            id=loc_id,
            active=True,
            name="London Location",
            address=Address(
                line1="10 Downing Street",
                line2=None,
                county="Greater London",
                town="London",
                postcode="SW1A 2AA",
            ),
            positionGCS=PositionGCS(
                latitude=latitude,
                longitude=longitude,
            ),
            managingOrganisation=uuid4(),
            primaryAddress=True,
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

        location_repository.create(location)

        # Retrieve and verify coordinates
        retrieved = location_repository.get(loc_id)
        assert retrieved.positionGCS is not None
        # Compare as strings to avoid floating point issues
        assert str(retrieved.positionGCS.latitude) == str(latitude)
        assert str(retrieved.positionGCS.longitude) == str(longitude)
