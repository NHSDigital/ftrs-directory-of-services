from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from freezegun import freeze_time
from ftrs_data_layer.domain import Address, Location, PositionGCS

from common.mapping.location import LocationMapper
from service_migration.dependencies import ServiceMigrationDependencies


@freeze_time("2025-07-17T12:00:00")
def test_location_mapper_map_with_full_address_and_position(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the location mapper correctly maps a service with full address and position."""
    mapper = LocationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")

    result = mapper.map(mock_legacy_service, organisation_id)

    assert isinstance(result, Location)
    assert result.id == UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060")
    assert result.identifier_oldDoS_uid == "test-uid"
    assert result.active is True
    assert result.managingOrganisation == organisation_id
    assert result.address is not None
    assert isinstance(result.address, Address)
    assert result.address.line1 == "123 Main St"
    assert result.address.line2 is None
    assert result.address.county == "West Yorkshire"
    assert result.address.town == "Leeds"
    assert result.address.postcode == "AB12 3CD"
    assert result.name is None
    assert result.positionGCS is not None
    assert isinstance(result.positionGCS, PositionGCS)
    assert result.positionGCS.latitude == Decimal("51.5074")
    assert result.positionGCS.longitude == Decimal("-0.1278")
    assert result.primaryAddress is True
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.partOf is None


@freeze_time("2025-07-17T12:00:00")
def test_location_mapper_map_no_position(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the location mapper correctly maps a service without position data."""
    mock_legacy_service.latitude = None
    mock_legacy_service.longitude = None

    mapper = LocationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")

    result = mapper.map(mock_legacy_service, organisation_id)

    assert isinstance(result, Location)
    assert result.positionGCS is None
    assert result.id == UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060")
    assert result.active is True
    assert result.identifier_oldDoS_uid == "test-uid"
    assert result.managingOrganisation == organisation_id
    assert result.address is not None
    assert result.address.line1 == "123 Main St"
    assert result.name is None
    assert result.primaryAddress is True
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    assert result.partOf is None


@freeze_time("2025-07-17T12:00:00")
def test_location_mapper_map_with_partial_position(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the location mapper correctly handles partial position data."""
    # Only latitude provided
    mock_legacy_service.longitude = None

    mapper = LocationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")

    result = mapper.map(mock_legacy_service, organisation_id)

    # Position should be None if both lat and long are not present
    assert result.positionGCS is None


@freeze_time("2025-07-17T12:00:00")
def test_location_mapper_map_with_different_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the location mapper generates different IDs for different services."""
    mock_legacy_service.id = 999
    mock_legacy_service.uid = "different-uid"

    mapper = LocationMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")

    result = mapper.map(mock_legacy_service, organisation_id)

    assert result.identifier_oldDoS_uid == "different-uid"
    # ID should be different from the default service ID
    assert result.id != UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060")
