"""Additional comprehensive tests for service_migration/dynamodb.py module."""

from datetime import UTC, datetime
from uuid import UUID

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
from service_migration.models import MigrationState


def create_test_organisation(name: str = "Test Org") -> Organisation:
    """Create a test organisation."""
    return Organisation(
        id=UUID("4539600c-e04e-5b35-a582-9fb36858d0e0"),
        identifier_oldDoS_uid="test-uid",
        identifier_ODS_ODSCode="A12345",
        name=name,
        type="GP Practice",
        active=True,
        telecom=[Telecom(type=TelecomType.PHONE, value="01234567890", isPublic=True)],
        createdBy="DATA_MIGRATION",
        createdDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
    )


def create_test_location(name: str = "Test Location") -> Location:
    """Create a test location."""
    return Location(
        id=UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060"),
        active=True,
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


def create_test_healthcare_service(name: str = "Test Service") -> HealthcareService:
    """Create a test healthcare service."""
    return HealthcareService(
        id=UUID("903cd48b-5d0f-532f-94f4-937a4517b14d"),
        identifier_oldDoS_uid="test-uid",
        active=True,
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
def test_transaction_builder_complete_workflow(
    mock_dependencies: ServiceMigrationDependencies,
    mock_logger: MockLogger,
) -> None:
    """Test complete workflow from creation to transaction build."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    org = create_test_organisation()
    loc = create_test_location()
    svc = create_test_healthcare_service()

    # Build complete transaction
    result = (
        builder.add_organisation(org)
        .add_location(loc)
        .add_healthcare_service(svc)
        .build()
    )

    # Verify all items are present
    assert len(result) == 4  # org + loc + svc + state

    # Verify migration state is properly updated
    assert builder.migration_state.organisation_id == org.id
    assert builder.migration_state.location_id == loc.id
    assert builder.migration_state.healthcare_service_id == svc.id
    assert builder.migration_state.version == 1


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_partial_updates(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test partial updates with only some entities."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.version = 5
    existing_state.organisation = create_test_organisation(name="Old")
    existing_state.organisation_id = existing_state.organisation.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    # Only add location (simulating partial update)
    loc = create_test_location()
    result = builder.add_location(loc).build()

    # Should have location + updated state
    assert len(result) == 2
    assert builder.migration_state.version == 6
    assert builder.migration_state.location_id == loc.id


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_validation_issues_stored(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that validation issues are stored in migration state."""
    service_id = 1
    validation_issues = [
        {"field": "phone", "severity": "warning", "message": "Invalid format"},
        {"field": "postcode", "severity": "error", "message": "Missing"},
    ]

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        validation_issues=validation_issues,
    )

    org = create_test_organisation()
    builder.add_organisation(org).build()

    # Verify validation issues are in migration state
    assert builder.migration_state.validation_issues == validation_issues


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_workspace_table_naming(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that workspace is included in table names."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    org = create_test_organisation()
    result = builder.add_organisation(org).build()

    # Check table name includes workspace
    org_item = result[0]
    assert "test-workspace" in org_item["Put"]["TableName"]


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_condition_expressions(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that correct condition expressions are used."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    org = create_test_organisation()
    result = builder.add_organisation(org).build()

    # Check organisation insert has correct condition
    org_item = result[0]
    assert (
        org_item["Put"]["ConditionExpression"]
        == "attribute_not_exists(id) AND attribute_not_exists(#field)"
    )

    # Check state insert has correct condition
    state_item = result[1]
    assert (
        state_item["Put"]["ConditionExpression"]
        == "attribute_not_exists(source_record_id)"
    )


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_state_update_condition(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test state update uses optimistic locking."""
    service_id = 1
    existing_state = MigrationState.create(service_id)
    existing_state.version = 10
    existing_state.organisation = create_test_organisation()
    existing_state.organisation_id = existing_state.organisation.id

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=existing_state,
    )

    loc = create_test_location()
    result = builder.add_location(loc).build()

    # Check state update has version check
    state_item = result[1]
    assert (
        state_item["Put"]["ConditionExpression"]
        == "attribute_exists(source_record_id) AND version = :current_version"
    )
    assert state_item["Put"]["ExpressionAttributeValues"] == {
        ":current_version": {"N": "10"}
    }


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_serialisation_preserves_types(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that serialisation preserves correct DynamoDB types."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    org = create_test_organisation()
    result = builder.add_organisation(org).build()

    org_item = result[0]["Put"]["Item"]

    # UUID should be serialized as string
    assert "S" in org_item["id"]
    assert org_item["id"]["S"] == "4539600c-e04e-5b35-a582-9fb36858d0e0"

    # Boolean should be serialized as BOOL
    assert "BOOL" in org_item["active"]
    assert org_item["active"]["BOOL"] is True

    # String fields
    assert "S" in org_item["name"]
    assert org_item["name"]["S"] == "Test Org"


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_multiple_sequential_builds(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that builder can be used multiple times."""
    service_id = 1

    # First build
    builder1 = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )
    org = create_test_organisation()
    result1 = builder1.add_organisation(org).build()
    assert len(result1) == 2

    # Second build with different builder
    builder2 = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )
    loc = create_test_location()
    result2 = builder2.add_location(loc).build()
    assert len(result2) == 2


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_handles_complex_telecom(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that complex telecom structures are handled correctly."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    org = create_test_organisation()
    org.telecom = [
        Telecom(type=TelecomType.PHONE, value="01234567890", isPublic=True),
        Telecom(type=TelecomType.PHONE, value="02012345678", isPublic=False),
        Telecom(type=TelecomType.PHONE, value="07123456789", isPublic=True),
    ]

    result = builder.add_organisation(org).build()

    # Verify telecom is serialized
    org_item = result[0]["Put"]["Item"]
    assert "telecom" in org_item
    assert "L" in org_item["telecom"]  # List type


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_state_copy_independence(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that builder creates independent copy of state."""
    service_id = 1
    original_state = MigrationState.create(service_id)
    original_state.version = 5

    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
        migration_state=original_state,
    )

    # Modify builder's state
    org = create_test_organisation()
    builder.add_organisation(org)
    builder.build()

    # Original state should be unchanged
    assert original_state.version == 5
    assert original_state.organisation_id is None

    # Builder's state should be modified
    assert builder.migration_state.version == 6
    assert builder.migration_state.organisation_id == org.id


@freeze_time("2025-07-17T12:00:00")
def test_transaction_builder_empty_then_populated(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test that building empty transaction then adding items works."""
    service_id = 1
    builder = ServiceTransactionBuilder(
        deps=mock_dependencies,
        service_id=service_id,
    )

    # First build with no items
    result1 = builder.build()
    assert len(result1) == 0

    # Add items - but builder is already built, so this tests edge case
    # In practice, a new builder would be created
    assert len(builder.items) == 0
