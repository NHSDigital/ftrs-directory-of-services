from datetime import UTC, datetime
from uuid import UUID

from freezegun import freeze_time
from ftrs_data_layer.domain import Endpoint, Organisation

from common.mapping.organisation import OrganisationMapper
from service_migration.dependencies import ServiceMigrationDependencies


@freeze_time("2025-07-17T12:00:00")
def test_organisation_mapper_map(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the organisation mapper correctly maps a legacy service to an Organisation."""
    mapper = OrganisationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    result = mapper.map(mock_legacy_service)

    assert isinstance(result, Organisation)
    assert result.id == UUID("4539600c-e04e-5b35-a582-9fb36858d0e0")
    assert result.identifier_oldDoS_uid == "test-uid"
    assert result.name == "Public Test Service"
    assert result.type == "GP Practice"
    assert result.active is True
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.identifier_ODS_ODSCode == "A12345"
    assert result.telecom == []
    assert len(result.endpoints) == 2


@freeze_time("2025-07-17T12:00:00")
def test_organisation_mapper_map_endpoints(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the organisation mapper correctly maps service endpoints."""
    mapper = OrganisationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    result = mapper.map(mock_legacy_service)

    assert len(result.endpoints) == 2

    # First endpoint
    endpoint1 = result.endpoints[0]
    assert isinstance(endpoint1, Endpoint)
    assert endpoint1.id == UUID("a226aaa5-392c-59c8-8d79-563bb921cb0d")
    assert endpoint1.createdBy == "DATA_MIGRATION"
    assert endpoint1.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert endpoint1.modifiedBy == "DATA_MIGRATION"
    assert endpoint1.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert endpoint1.identifier_oldDoS_id == 1
    assert endpoint1.status == "active"
    assert endpoint1.connectionType == "http"
    assert endpoint1.name is None
    assert endpoint1.payloadMimeType is None
    assert endpoint1.description == "Primary"
    assert (
        endpoint1.payloadType
        == "urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0"
    )
    assert endpoint1.address == "http://example.com/endpoint"
    assert endpoint1.managedByOrganisation == UUID(
        "4539600c-e04e-5b35-a582-9fb36858d0e0"
    )
    assert endpoint1.service is None
    assert endpoint1.order == 1
    assert endpoint1.isCompressionEnabled is True

    # Second endpoint
    endpoint2 = result.endpoints[1]
    assert isinstance(endpoint2, Endpoint)
    assert endpoint2.id == UUID("4d678d9c-61db-584f-a64c-bd8eb829d8db")
    assert endpoint2.identifier_oldDoS_id == 2
    assert endpoint2.connectionType == "email"
    assert endpoint2.description == "Copy"
    assert endpoint2.address == "mailto:test@example.com"
    assert endpoint2.order == 2
    assert endpoint2.isCompressionEnabled is False


@freeze_time("2025-07-17T12:00:00")
def test_organisation_mapper_with_different_service_type(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the organisation mapper handles different service types correctly."""
    # Change service type to GP Access Hub
    mock_legacy_service.typeid = 136

    mapper = OrganisationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    result = mapper.map(mock_legacy_service)

    assert result.type == "GP Access Hub"
