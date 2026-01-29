from datetime import datetime
from uuid import UUID

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
    PositionGCS,
)

from service_migration.ddb_transactions import ServiceTransactionBuilder
from service_migration.exceptions import ServiceMigrationException
from service_migration.models import ServiceMigrationState


@pytest.fixture
def mock_organisation() -> Organisation:
    return Organisation(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        type="GP Practice",
        active=True,
        name="Test Organisation",
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        identifier_ODS_ODSCode="ABC123",
        identifier_oldDoS_uid="test-uid",
        endpoints=[],
        telecom=[],
    )


@pytest.fixture
def mock_location() -> Location:
    return Location(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        active=True,
        managingOrganisation=UUID("11111111-1111-1111-1111-111111111111"),
        address=Address(
            line1="123 Test St",
            line2=None,
            town="Test Town",
            county="Test County",
            postcode="TE1 1ST",
        ),
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        positionGCS=PositionGCS(latitude="51.5", longitude="-0.1"),
        identifier_oldDoS_uid="test-uid",
        primaryAddress=True,
    )


@pytest.fixture
def mock_healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        active=True,
        type="GP Consultation Service",
        name="Test Service",
        providedBy=UUID("11111111-1111-1111-1111-111111111111"),
        location=UUID("22222222-2222-2222-2222-222222222222"),
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime.fromisoformat("2025-01-01T00:00:00Z"),
        identifier_oldDoS_uid="test-uid",
        telecom=HealthcareServiceTelecom(
            phone_public=None,
            phone_private=None,
            email=None,
            web=None,
        ),
        category="GP Services",
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )


def test_builder_init(mock_logger: MockLogger) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    assert builder.service_id == 123  # noqa: PLR2004
    assert builder.migration_state.source_record_id == "services#123"
    assert builder.migration_state.version == 0
    assert builder.migration_state.organisation is None
    assert builder.migration_state.location is None
    assert builder.migration_state.healthcare_service is None
    assert builder.items == []


def test_builder_init_with_existing_state(mock_logger: MockLogger) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#456",
        version=3,
        organisation_id=UUID("11111111-1111-1111-1111-111111111111"),
        organisation=None,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=456, logger=mock_logger, migration_state=existing_state
    )

    assert builder.migration_state.version == 3  # noqa: PLR2004
    assert builder.migration_state.organisation_id == UUID(
        "11111111-1111-1111-1111-111111111111"
    )


def test_insert_organisation(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_organisation(mock_organisation)

    assert result is builder
    assert len(builder.items) == 1
    assert "organisation" in builder.items[0]["Put"]["TableName"]
    assert builder.migration_state.organisation == mock_organisation
    assert builder.migration_state.organisation_id == mock_organisation.id
    assert mock_logger.was_logged("DM_ETL_024")


def test_insert_organisation_none(mock_logger: MockLogger) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_organisation(None)

    assert result is builder
    assert len(builder.items) == 0
    assert builder.migration_state.organisation is None
    assert mock_logger.was_logged("DM_ETL_023")


def test_update_organisation_no_changes(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    result = builder.add_organisation(mock_organisation)

    assert result is builder
    assert len(builder.items) == 0
    assert mock_logger.was_logged("DM_ETL_029")


def test_update_organisation_with_changes(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    updated_org = mock_organisation.model_copy(update={"name": "Updated Name"})
    result = builder.add_organisation(updated_org)

    assert result is builder

    assert len(builder.items) == 1
    assert mock_logger.was_logged("DM_ETL_030")


def test_update_organisation_none_raises(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    with pytest.raises(ServiceMigrationException, match="deletion not currently"):
        builder.add_organisation(None)


def test_insert_location(
    mock_logger: MockLogger,
    mock_location: Location,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_location(mock_location)

    assert result is builder
    assert len(builder.items) == 1
    assert "location" in builder.items[0]["Put"]["TableName"]
    assert builder.migration_state.location == mock_location
    assert builder.migration_state.location_id == mock_location.id
    assert mock_logger.was_logged("DM_ETL_026")


def test_insert_location_none(mock_logger: MockLogger) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_location(None)

    assert result is builder
    assert len(builder.items) == 0
    assert builder.migration_state.location is None
    assert mock_logger.was_logged("DM_ETL_025")


def test_update_location_no_changes(
    mock_logger: MockLogger,
    mock_location: Location,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=mock_location.id,
        location=mock_location,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123,
        logger=mock_logger,
        migration_state=existing_state,
    )

    result = builder.add_location(mock_location)

    assert result is builder
    assert len(builder.items) == 0
    assert mock_logger.was_logged("DM_ETL_031")


def test_update_location_with_changes(
    mock_logger: MockLogger,
    mock_location: Location,
) -> None:
    modified_location = mock_location.model_copy(update={"name": "Updated Location"})
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=mock_location.id,
        location=mock_location,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    builder.add_location(modified_location)

    assert len(builder.items) == 1
    assert mock_logger.was_logged("DM_ETL_032")


def test_update_location_none_raises(
    mock_logger: MockLogger,
    mock_location: Location,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=mock_location.id,
        location=mock_location,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    with pytest.raises(ServiceMigrationException, match="deletion not currently"):
        builder.add_location(None)


def test_insert_healthcare_service(
    mock_logger: MockLogger,
    mock_healthcare_service: HealthcareService,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_healthcare_service(mock_healthcare_service)

    assert result is builder
    assert len(builder.items) == 1
    assert "healthcare-service" in builder.items[0]["Put"]["TableName"]
    assert builder.migration_state.healthcare_service == mock_healthcare_service
    assert builder.migration_state.healthcare_service_id == mock_healthcare_service.id
    assert mock_logger.was_logged("DM_ETL_028")


def test_insert_healthcare_service_none(mock_logger: MockLogger) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.add_healthcare_service(None)

    assert result is builder
    assert len(builder.items) == 0
    assert builder.migration_state.healthcare_service is None


def test_update_healthcare_service_no_changes(
    mock_logger: MockLogger,
    mock_healthcare_service: HealthcareService,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=None,
        location=None,
        healthcare_service_id=mock_healthcare_service.id,
        healthcare_service=mock_healthcare_service,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    result = builder.add_healthcare_service(mock_healthcare_service)

    assert result is builder
    assert len(builder.items) == 0
    assert mock_logger.was_logged("DM_ETL_033")


def test_update_healthcare_service_with_changes(
    mock_logger: MockLogger,
    mock_healthcare_service: HealthcareService,
) -> None:
    modified_service = mock_healthcare_service.model_copy(
        update={"name": "Updated Service Name"}
    )
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=None,
        location=None,
        healthcare_service_id=mock_healthcare_service.id,
        healthcare_service=mock_healthcare_service,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    builder.add_healthcare_service(modified_service)

    assert len(builder.items) == 1
    assert mock_logger.was_logged("DM_ETL_034")


def test_update_healthcare_service_none_raises(
    mock_logger: MockLogger,
    mock_healthcare_service: HealthcareService,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=None,
        location=None,
        healthcare_service_id=mock_healthcare_service.id,
        healthcare_service=mock_healthcare_service,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    with pytest.raises(ServiceMigrationException, match="deletion not supported"):
        builder.add_healthcare_service(None)


def test_build_empty_returns_empty_list(mock_logger: MockLogger) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = builder.build()

    assert result == []
    assert mock_logger.was_logged("DM_ETL_037")


def test_build_with_insert_adds_state_record(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)
    builder.add_organisation(mock_organisation)

    result = builder.build()

    assert len(result) == 2  # noqa: PLR2004
    assert "data-migration-state" in result[-1]["Put"]["TableName"]
    assert builder.migration_state.version == 1
    assert mock_logger.was_logged("DM_ETL_035")


def test_build_with_update_increments_version(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
    mock_location: Location,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=2,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )
    builder.add_location(mock_location)

    result = builder.build()

    assert len(result) == 2  # noqa: PLR2004
    assert builder.migration_state.version == 3  # noqa: PLR2004
    state_item = result[-1]["Put"]
    assert "ConditionExpression" in state_item
    assert ":current_version" in state_item.get("ExpressionAttributeValues", {})
    assert mock_logger.was_logged("DM_ETL_036")


def test_method_chaining(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
    mock_location: Location,
    mock_healthcare_service: HealthcareService,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)

    result = (
        builder.add_organisation(mock_organisation)
        .add_location(mock_location)
        .add_healthcare_service(mock_healthcare_service)
        .build()
    )

    assert len(result) == 4  # noqa: PLR2004 - org, location, healthcare_service, state
    assert builder.migration_state.organisation == mock_organisation
    assert builder.migration_state.location == mock_location
    assert builder.migration_state.healthcare_service == mock_healthcare_service


def test_serialise_item_includes_additional_fields(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)
    builder.add_organisation(mock_organisation)

    item = builder.items[0]["Put"]["Item"]
    assert "field" in item
    assert item["field"]["S"] == "document"


def test_insert_state_record_condition(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)
    builder.add_organisation(mock_organisation)
    builder.build()

    state_item = builder.items[-1]["Put"]
    assert state_item["ConditionExpression"] == "attribute_not_exists(source_record_id)"


def test_update_state_record_condition(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
    mock_location: Location,
) -> None:
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=5,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )
    builder.add_location(mock_location)
    builder.build()

    state_item = builder.items[-1]["Put"]
    assert "attribute_exists(source_record_id)" in state_item["ConditionExpression"]
    assert "version = :current_version" in state_item["ConditionExpression"]
    assert state_item["ExpressionAttributeValues"][":current_version"]["N"] == "5"


def test_put_item_condition_expression(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    builder = ServiceTransactionBuilder(service_id=123, logger=mock_logger)
    builder.add_organisation(mock_organisation)

    put_item = builder.items[0]["Put"]
    assert "attribute_not_exists(id)" in put_item["ConditionExpression"]
    assert "attribute_not_exists(#field)" in put_item["ConditionExpression"]
    assert put_item["ExpressionAttributeNames"]["#field"] == "field"


def test_update_organisation_includes_audit_timestamps(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    """UPDATE operations include audit timestamp fields."""
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    updated_org = mock_organisation.model_copy(update={"name": "Updated Name"})
    builder.add_organisation(updated_org)

    update_item = builder.items[0]["Update"]

    # Verify audit fields are in the update expression
    assert "#lastUpdated" in update_item["UpdateExpression"]
    assert "#lastUpdatedBy" in update_item["UpdateExpression"]

    # Verify attribute names are registered
    assert update_item["ExpressionAttributeNames"]["#lastUpdated"] == "lastUpdated"
    assert update_item["ExpressionAttributeNames"]["#lastUpdatedBy"] == "lastUpdatedBy"

    # Verify values are present
    assert ":lastUpdated" in update_item["ExpressionAttributeValues"]
    assert ":lastUpdatedBy" in update_item["ExpressionAttributeValues"]


def test_update_location_includes_audit_timestamps(
    mock_logger: MockLogger,
    mock_location: Location,
) -> None:
    """Location UPDATE operations include audit timestamp fields."""
    modified_location = mock_location.model_copy(update={"name": "Updated Location"})
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=mock_location.id,
        location=mock_location,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    builder.add_location(modified_location)

    update_item = builder.items[0]["Update"]

    assert "#lastUpdated" in update_item["UpdateExpression"]
    assert "#lastUpdatedBy" in update_item["UpdateExpression"]
    assert ":lastUpdated" in update_item["ExpressionAttributeValues"]
    assert ":lastUpdatedBy" in update_item["ExpressionAttributeValues"]


def test_update_healthcare_service_includes_audit_timestamps(
    mock_logger: MockLogger,
    mock_healthcare_service: HealthcareService,
) -> None:
    """HealthcareService UPDATE operations include audit timestamp fields."""
    modified_service = mock_healthcare_service.model_copy(
        update={"name": "Updated Service Name"}
    )
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=None,
        organisation=None,
        location_id=None,
        location=None,
        healthcare_service_id=mock_healthcare_service.id,
        healthcare_service=mock_healthcare_service,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    builder.add_healthcare_service(modified_service)

    update_item = builder.items[0]["Update"]

    assert "#lastUpdated" in update_item["UpdateExpression"]
    assert "#lastUpdatedBy" in update_item["UpdateExpression"]
    assert ":lastUpdated" in update_item["ExpressionAttributeValues"]
    assert ":lastUpdatedBy" in update_item["ExpressionAttributeValues"]


def test_audit_updater_metadata_is_correct(
    mock_logger: MockLogger,
    mock_organisation: Organisation,
) -> None:
    """Audit updater metadata contains correct values."""
    existing_state = ServiceMigrationState(
        source_record_id="services#123",
        version=1,
        organisation_id=mock_organisation.id,
        organisation=mock_organisation,
        location_id=None,
        location=None,
        healthcare_service_id=None,
        healthcare_service=None,
        validation_issues=[],
    )
    builder = ServiceTransactionBuilder(
        service_id=123, logger=mock_logger, migration_state=existing_state
    )

    updated_org = mock_organisation.model_copy(update={"name": "Updated Name"})
    builder.add_organisation(updated_org)

    update_item = builder.items[0]["Update"]
    updated_by = update_item["ExpressionAttributeValues"][":lastUpdatedBy"]["M"]

    assert updated_by["type"]["S"] == "app"
    assert updated_by["value"]["S"] == "INTERNAL001"
    assert updated_by["display"]["S"] == "Data Migration"
