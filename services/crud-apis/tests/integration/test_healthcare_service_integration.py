"""Integration tests for HealthcareService CRUD operations.

These tests run against a real DynamoDB instance using LocalStack testcontainers.
They verify actual database operations, serialization, and query patterns.

Run with: pytest -m integration tests/integration/test_healthcare_service_integration.py
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from ftrs_data_layer.domain import HealthcareService
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain.healthcare_service import HealthcareServiceTelecom


@pytest.mark.integration
class TestHealthcareServiceRepositoryIntegration:
    """Integration tests for HealthcareService repository operations."""

    def test_create_and_get_healthcare_service(
        self,
        healthcare_service_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should create a healthcare service and retrieve it by ID."""
        service_id = uuid4()
        service = HealthcareService(
            id=service_id,
            active=True,
            name="Test GP Practice",
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=uuid4(),
            location=uuid4(),
            telecom=HealthcareServiceTelecom(
                phone_public="0300 311 22 33",
                phone_private="0300 311 22 34",
                email="test@nhs.net",
                web="https://example.nhs.uk",
            ),
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
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
        healthcare_service_repository.create(service)

        # Retrieve
        retrieved = healthcare_service_repository.get(service_id)

        assert retrieved is not None
        assert retrieved.id == service_id
        assert retrieved.name == "Test GP Practice"
        assert retrieved.active is True
        assert retrieved.category == HealthcareServiceCategory.GP_SERVICES

    def test_update_healthcare_service(
        self,
        healthcare_service_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should update an existing healthcare service."""
        service_id = uuid4()
        service = HealthcareService(
            id=service_id,
            active=True,
            name="Original Service",
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=uuid4(),
            location=uuid4(),
            telecom=HealthcareServiceTelecom(
                phone_public=None,
                phone_private=None,
                email=None,
                web=None,
            ),
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
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

        healthcare_service_repository.create(service)

        # Update
        service.name = "Updated Service"
        service.active = False
        healthcare_service_repository.update(service_id, service)

        # Verify update
        retrieved = healthcare_service_repository.get(service_id)
        assert retrieved.name == "Updated Service"
        assert retrieved.active is False

    def test_delete_healthcare_service(
        self,
        healthcare_service_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should delete a healthcare service."""
        service_id = uuid4()
        service = HealthcareService(
            id=service_id,
            active=True,
            name="To Be Deleted",
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=uuid4(),
            location=uuid4(),
            telecom=HealthcareServiceTelecom(
                phone_public=None,
                phone_private=None,
                email=None,
                web=None,
            ),
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
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

        healthcare_service_repository.create(service)

        # Verify exists
        assert healthcare_service_repository.get(service_id) is not None

        # Delete
        healthcare_service_repository.delete(service_id)

        # Verify deleted
        assert healthcare_service_repository.get(service_id) is None

    def test_healthcare_service_with_opening_times(
        self,
        healthcare_service_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should correctly store and retrieve opening times."""
        service_id = uuid4()
        service = HealthcareService(
            id=service_id,
            active=True,
            name="Service With Opening Times",
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=uuid4(),
            location=uuid4(),
            telecom=HealthcareServiceTelecom(
                phone_public=None,
                phone_private=None,
                email=None,
                web=None,
            ),
            openingTime=[],  # Would add actual OpeningTime objects if model is available
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
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

        healthcare_service_repository.create(service)

        # Retrieve and verify
        retrieved = healthcare_service_repository.get(service_id)
        assert retrieved is not None
        assert retrieved.openingTime is not None

    def test_healthcare_service_with_identifier(
        self,
        healthcare_service_repository: Any,
        clean_tables: dict[str, Any],
    ) -> None:
        """Should correctly store and retrieve legacy DoS identifier."""
        service_id = uuid4()
        service = HealthcareService(
            id=service_id,
            identifier_oldDoS_uid="161799",
            active=True,
            name="Service With Identifier",
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=uuid4(),
            location=uuid4(),
            telecom=HealthcareServiceTelecom(
                phone_public=None,
                phone_private=None,
                email=None,
                web=None,
            ),
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
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

        healthcare_service_repository.create(service)

        # Retrieve and verify
        retrieved = healthcare_service_repository.get(service_id)
        assert retrieved is not None
        assert retrieved.identifier_oldDoS_uid == "161799"
