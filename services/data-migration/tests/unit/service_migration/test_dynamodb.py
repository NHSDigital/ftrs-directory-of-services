from datetime import UTC, datetime
from uuid import UUID

import pytest
from boto3.dynamodb.types import TypeSerializer
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
    Telecom,
)
from ftrs_data_layer.domain.enums import TelecomType

from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.dynamodb import ServiceTransactionBuilder
from service_migration.exceptions import ServiceMigrationException
from service_migration.models import MigrationState


# Helper functions to create valid model instances
def create_organisation(
    name: str = "Test Organisation", active: bool = True
) -> Organisation:
    """Create a valid Organisation instance for testing."""
    return Organisation(
        id=UUID("4539600c-e04e-5b35-a582-9fb36858d0e0"),
        identifier_oldDoS_uid="test-uid",
        identifier_ODS_ODSCode="A12345",
        name=name,
        type="GP Practice",
        active=active,
        telecom=[Telecom(type=TelecomType.PHONE, value="01234567890", isPublic=True)],
        createdBy="DATA_MIGRATION",
        createdDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
    )


def create_location(name: str = "Test Location", active: bool = True) -> Location:
    """Create a valid Location instance for testing."""
    return Location(
        id=UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060"),
        active=active,
        managingOrganisation=UUID("4539600c-e04e-5b35-a582-9fb36858d0e0"),
        address=Address(
            line1="123 Main St",
            line2=None,
            county="Test County",
            town="Test Town",
            postcode="AB12 3CD",
        ),
        name=name,
        primaryAddress=True,
        createdBy="DATA_MIGRATION",
        createdDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
    )


def create_healthcare_service(
    name: str = "Test Healthcare Service", active: bool = True
) -> HealthcareService:
    """Create a valid HealthcareService instance for testing."""
    return HealthcareService(
        id=UUID("903cd48b-5d0f-532f-94f4-937a4517b14d"),
        identifier_oldDoS_uid="test-uid",
        active=active,
        category="GP Services",
        type="GP Consultation Service",
        providedBy=UUID("4539600c-e04e-5b35-a582-9fb36858d0e0"),
        location=UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060"),
        name=name,
        telecom=HealthcareServiceTelecom(
            phone_public="01234567890", phone_private=None, email=None, web=None
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
        createdBy="DATA_MIGRATION",
        createdDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
    )


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_init(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the transaction builder initializes correctly with no existing state."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    assert builder.record_id == service_id
    assert builder.migration_state.source_record_id == "services#1"
    assert builder.migration_state.version == 0
    assert builder.migration_state.organisation_id is None
    assert builder.migration_state.location_id is None
    assert builder.migration_state.healthcare_service_id is None
    assert builder.items == []
    assert isinstance(builder.serialiser, TypeSerializer)


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_init_with_existing_state(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the transaction builder initializes correctly with existing state."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.version = 5
    existing_state.organisation_id = UUID("4539600c-e04e-5b35-a582-9fb36858d0e0")

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    assert builder.migration_state.source_record_id == "services#1"
    assert builder.migration_state.version == 5
    assert builder.migration_state.organisation_id == UUID(
        "4539600c-e04e-5b35-a582-9fb36858d0e0"
    )
    # Verify the state is a copy, not the original
    builder.migration_state.version = 10
    assert existing_state.version == 5


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_init_with_validation_issues(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that the transaction builder stores validation issues."""
    service_id = 1
    validation_issues = [
        {"field": "phone", "message": "Invalid format"},
        {"field": "email", "message": "Missing domain"},
    ]

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        validation_issues=validation_issues,
    )

    assert builder.migration_state.validation_issues == validation_issues


def test_format_migration_state_table_name() -> None:
    """Test the migration state table name formatter."""
    assert (
        ServiceTransactionBuilder.format_migration_state_table_name(env="dev")
        == "ftrs-dos-dev-data-migration-state-table"
    )
    assert (
        ServiceTransactionBuilder.format_migration_state_table_name(
            env="prod", workspace="feature-123"
        )
        == "ftrs-dos-prod-data-migration-state-table-feature-123"
    )
    assert (
        ServiceTransactionBuilder.format_migration_state_table_name(
            env="local", workspace="test-workspace"
        )
        == "ftrs-dos-local-data-migration-state-table-test-workspace"
    )


@freeze_time("2025-07-17T12:00:00")
def test_insert_organisation(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test inserting a new organisation."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    organisation = create_organisation()
    builder.add_organisation(organisation)

    assert builder.migration_state.organisation_id == organisation.id
    assert builder.migration_state.organisation == organisation
    assert len(builder.items) == 1
    assert (
        builder.items[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-organisation-test-workspace"
    )
    assert (
        builder.items[0]["Put"]["ConditionExpression"]
        == "attribute_not_exists(id) AND attribute_not_exists(#field)"
    )
    assert builder.items[0]["Put"]["ExpressionAttributeNames"] == {"#field": "field"}

    assert mock_logger.get_log("SM_PROC_012") == [
        {
            "msg": "Added organisation with ID 4539600c-e04e-5b35-a582-9fb36858d0e0 to migration items",
            "detail": {"organisation_id": "4539600c-e04e-5b35-a582-9fb36858d0e0"},
        }
    ]


@freeze_time("2025-07-17T12:00:00")
def test_insert_organisation_with_none(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that inserting None for organisation is handled gracefully."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    builder.add_organisation(None)

    assert builder.migration_state.organisation_id is None
    assert builder.migration_state.organisation is None
    assert len(builder.items) == 0

    assert mock_logger.was_logged("SM_PROC_011") is True


@freeze_time("2025-07-17T12:00:00")
def test_update_organisation_raises_on_delete(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that updating organisation to None raises an exception."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.organisation = create_organisation()
    existing_state.organisation_id = existing_state.organisation.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    with pytest.raises(ServiceMigrationException) as exc_info:
        builder.add_organisation(None)

    assert "Organisation deletion not currently supported" in str(exc_info.value)
    assert exc_info.value.should_requeue is False


@freeze_time("2025-07-17T12:00:00")
def test_update_organisation_no_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating organisation with no changes skips the update."""
    service_id = 1
    organisation = create_organisation()

    existing_state = MigrationState.create(service_id)
    existing_state.organisation = organisation.model_copy(deep=True)
    existing_state.organisation_id = organisation.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_organisation(organisation)

    assert len(builder.items) == 0
    assert mock_logger.was_logged("SM_PROC_017") is True


@freeze_time("2025-07-17T12:00:00")
def test_update_organisation_with_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating organisation with changes logs the diff."""
    service_id = 1
    old_organisation = create_organisation(name="Old Name")
    new_organisation = old_organisation.model_copy(deep=True)
    new_organisation.name = "New Name"
    new_organisation.active = False

    existing_state = MigrationState.create(service_id)
    existing_state.organisation = old_organisation
    existing_state.organisation_id = old_organisation.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_organisation(new_organisation)

    # TODO: FTRS-1371 - Update logic not yet implemented
    assert len(builder.items) == 0

    assert mock_logger.was_logged("SM_PROC_018") is True
    logs = mock_logger.get_log("SM_PROC_018")
    assert len(logs) == 1
    assert "changes" in logs[0]["detail"]


@freeze_time("2025-07-17T12:00:00")
def test_insert_location(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test inserting a new location."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    location = create_location()
    builder.add_location(location)

    assert builder.migration_state.location_id == location.id
    assert builder.migration_state.location == location
    assert len(builder.items) == 1
    assert (
        builder.items[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-location-test-workspace"
    )
    assert (
        builder.items[0]["Put"]["ConditionExpression"]
        == "attribute_not_exists(id) AND attribute_not_exists(#field)"
    )

    assert mock_logger.get_log("SM_PROC_014") == [
        {
            "msg": "Added location with ID 6ef3317e-c6dc-5e27-b36d-577c375eb060 to migration items",
            "detail": {"location_id": "6ef3317e-c6dc-5e27-b36d-577c375eb060"},
        }
    ]


@freeze_time("2025-07-17T12:00:00")
def test_insert_location_with_none(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that inserting None for location is handled gracefully."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    builder.add_location(None)

    assert builder.migration_state.location_id is None
    assert builder.migration_state.location is None
    assert len(builder.items) == 0

    assert mock_logger.was_logged("SM_PROC_013") is True


@freeze_time("2025-07-17T12:00:00")
def test_update_location_raises_on_delete(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that updating location to None raises an exception."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.location = create_location()
    existing_state.location_id = existing_state.location.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    with pytest.raises(ServiceMigrationException) as exc_info:
        builder.add_location(None)

    assert "Location deletion not currently supported" in str(exc_info.value)
    assert exc_info.value.should_requeue is False


@freeze_time("2025-07-17T12:00:00")
def test_update_location_no_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating location with no changes skips the update."""
    service_id = 1
    location = create_location()

    existing_state = MigrationState.create(service_id)
    existing_state.location = location.model_copy(deep=True)
    existing_state.location_id = location.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_location(location)

    assert len(builder.items) == 0
    assert mock_logger.was_logged("SM_PROC_019") is True


@freeze_time("2025-07-17T12:00:00")
def test_update_location_with_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating location with changes logs the diff."""
    service_id = 1
    old_location = create_location(name="Old Location Name")
    new_location = old_location.model_copy(deep=True)
    new_location.name = "New Location Name"
    new_location.active = False

    existing_state = MigrationState.create(service_id)
    existing_state.location = old_location
    existing_state.location_id = old_location.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_location(new_location)

    # TODO: FTRS-1371 - Update logic not yet implemented
    assert len(builder.items) == 0

    assert mock_logger.was_logged("SM_PROC_020") is True
    logs = mock_logger.get_log("SM_PROC_020")
    assert len(logs) == 1
    assert "changes" in logs[0]["detail"]


@freeze_time("2025-07-17T12:00:00")
def test_insert_healthcare_service(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test inserting a new healthcare service."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    healthcare_service = create_healthcare_service()
    builder.add_healthcare_service(healthcare_service)

    assert builder.migration_state.healthcare_service_id == healthcare_service.id
    assert builder.migration_state.healthcare_service == healthcare_service
    assert len(builder.items) == 1
    assert (
        builder.items[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-healthcare-service-test-workspace"
    )
    assert (
        builder.items[0]["Put"]["ConditionExpression"]
        == "attribute_not_exists(id) AND attribute_not_exists(#field)"
    )

    assert mock_logger.get_log("SM_PROC_016") == [
        {
            "msg": "Added healthcare service with ID 903cd48b-5d0f-532f-94f4-937a4517b14d to migration items",
            "detail": {"healthcare_service_id": "903cd48b-5d0f-532f-94f4-937a4517b14d"},
        }
    ]


@freeze_time("2025-07-17T12:00:00")
def test_insert_healthcare_service_with_none(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that inserting None for healthcare service is handled gracefully."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    builder.add_healthcare_service(None)

    assert builder.migration_state.healthcare_service_id is None
    assert builder.migration_state.healthcare_service is None
    assert len(builder.items) == 0


@freeze_time("2025-07-17T12:00:00")
def test_update_healthcare_service_raises_on_delete(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that updating healthcare service to None raises an exception."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.healthcare_service = create_healthcare_service()
    existing_state.healthcare_service_id = existing_state.healthcare_service.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    with pytest.raises(NotImplementedError) as exc_info:
        builder.add_healthcare_service(None)

    assert "HealthcareService deletion not supported" in str(exc_info.value)


@freeze_time("2025-07-17T12:00:00")
def test_update_healthcare_service_no_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating healthcare service with no changes skips the update."""
    service_id = 1
    healthcare_service = create_healthcare_service()

    existing_state = MigrationState.create(service_id)
    existing_state.healthcare_service = healthcare_service.model_copy(deep=True)
    existing_state.healthcare_service_id = healthcare_service.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_healthcare_service(healthcare_service)

    assert len(builder.items) == 0
    assert mock_logger.was_logged("SM_PROC_021") is True


@freeze_time("2025-07-17T12:00:00")
def test_update_healthcare_service_with_change(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that updating healthcare service with changes logs the diff."""
    service_id = 1
    old_service = create_healthcare_service(name="Old Service Name")
    new_service = old_service.model_copy(deep=True)
    new_service.name = "New Service Name"
    new_service.active = False

    existing_state = MigrationState.create(service_id)
    existing_state.healthcare_service = old_service
    existing_state.healthcare_service_id = old_service.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    builder.add_healthcare_service(new_service)

    # TODO: FTRS-1371 - Update logic not yet implemented
    assert len(builder.items) == 0

    assert mock_logger.was_logged("SM_PROC_022") is True
    logs = mock_logger.get_log("SM_PROC_022")
    assert len(logs) == 1
    assert "changes" in logs[0]["detail"]


@freeze_time("2025-07-17T12:00:00")
def test_build_with_no_items(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that build returns empty list when no items were added."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    result = builder.build()

    assert result == []


@freeze_time("2025-07-17T12:00:00")
def test_build_with_insert_items(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that build includes state record for new inserts."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    organisation = create_organisation()
    builder.add_organisation(organisation)
    result = builder.build()

    # Should have organisation + state record
    assert len(result) == 2
    assert (
        result[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-organisation-test-workspace"
    )
    assert (
        result[1]["Put"]["TableName"]
        == "ftrs-dos-local-data-migration-state-table-test-workspace"
    )
    assert (
        result[1]["Put"]["ConditionExpression"]
        == "attribute_not_exists(source_record_id)"
    )
    assert builder.migration_state.version == 1

    assert mock_logger.get_log("SM_PROC_023") == [
        {
            "msg": "Added migration state insert with source record ID services#1 to migration items",
            "detail": {"source_record_id": "services#1"},
        }
    ]


@freeze_time("2025-07-17T12:00:00")
def test_build_with_update_items(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test that build includes state record update for existing state."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.version = 5
    existing_state.organisation = create_organisation(name="Old Name")

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    # Add location (simulating a change)
    location = create_location()
    builder.add_location(location)
    result = builder.build()

    # Should have location + updated state record
    assert len(result) == 2
    assert (
        result[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-location-test-workspace"
    )
    assert (
        result[1]["Put"]["TableName"]
        == "ftrs-dos-local-data-migration-state-table-test-workspace"
    )
    assert (
        result[1]["Put"]["ConditionExpression"]
        == "attribute_exists(source_record_id) AND version = :current_version"
    )
    assert result[1]["Put"]["ExpressionAttributeValues"] == {
        ":current_version": {"N": "5"}
    }
    assert builder.migration_state.version == 6

    assert mock_logger.get_log("SM_PROC_024") == [
        {
            "msg": "Added migration state update to version 6 with source record ID services#1 to migration items",
            "detail": {"source_record_id": "services#1", "new_version": 6},
        }
    ]


@freeze_time("2025-07-17T12:00:00")
def test_build_with_all_entities(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test building transaction with all three entities."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    organisation = create_organisation()
    location = create_location()
    healthcare_service = create_healthcare_service()

    builder.add_organisation(organisation).add_location(
        location
    ).add_healthcare_service(healthcare_service)
    result = builder.build()

    # Should have org + location + healthcare_service + state record
    assert len(result) == 4
    assert (
        result[0]["Put"]["TableName"]
        == "ftrs-dos-local-database-organisation-test-workspace"
    )
    assert (
        result[1]["Put"]["TableName"]
        == "ftrs-dos-local-database-location-test-workspace"
    )
    assert (
        result[2]["Put"]["TableName"]
        == "ftrs-dos-local-database-healthcare-service-test-workspace"
    )
    assert (
        result[3]["Put"]["TableName"]
        == "ftrs-dos-local-data-migration-state-table-test-workspace"
    )


@freeze_time("2025-07-17T12:00:00")
def test_method_chaining(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that methods return self for chaining."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    organisation = create_organisation()
    location = create_location()

    # Test method chaining
    result = builder.add_organisation(organisation).add_location(location)

    assert result is builder
    assert len(builder.items) == 2


@freeze_time("2025-07-17T12:00:00")
def test_serialise_item(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test the _serialise_item method correctly formats items."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    organisation = create_organisation()
    serialised = builder._serialise_item(organisation, field="document")

    # Verify it's in DynamoDB format
    assert "id" in serialised
    assert "S" in serialised["id"]  # String type
    assert serialised["id"]["S"] == "4539600c-e04e-5b35-a582-9fb36858d0e0"

    assert "field" in serialised
    assert serialised["field"]["S"] == "document"

    assert "name" in serialised
    assert serialised["name"]["S"] == "Test Organisation"
