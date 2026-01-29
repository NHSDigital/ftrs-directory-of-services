from datetime import datetime
from uuid import UUID, uuid4

import pytest
from boto3.dynamodb.types import TypeSerializer
from ftrs_data_layer.domain import (
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
    HealthcareServiceCategory,
    HealthcareServiceType,
    OrganisationType,
)
from ftrs_data_layer.domain.location import Address, PositionGCS

from common.diff_utils import (
    DynamoDBUpdateExpressions,
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)


@pytest.fixture
def organisation() -> Organisation:
    return Organisation(
        id=uuid4(),
        identifier_oldDoS_uid="UID123",
        identifier_ODS_ODSCode="ODS001",
        active=True,
        name="Test Organisation",
        type=OrganisationType.GP_PRACTICE,
        telecom=None,
        endpoints=[],
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


@pytest.fixture
def location() -> Location:
    return Location(
        id=uuid4(),
        identifier_oldDoS_uid="LOC123",
        active=True,
        address=Address(
            line1="123 Test Street",
            line2="Test Area",
            county="Test County",
            town="Test Town",
            postcode="TE1 1ST",
        ),
        managingOrganisation=uuid4(),
        name="Test Location",
        positionGCS=PositionGCS(latitude=51.5074, longitude=-0.1278),
        primaryAddress=True,
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


@pytest.fixture
def healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid="HS123",
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=HealthcareServiceTelecom(
            phone_public="0123456789",
            phone_private="9876543210",
            email="test@example.com",
            web="https://www.example.com",
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


@pytest.fixture
def serializer() -> TypeSerializer:
    """Provide a TypeSerializer instance."""
    return TypeSerializer()


@pytest.fixture
def timestamp() -> str:
    """Provide a valid ISO timestamp."""
    return "2026-01-28T12:00:00+00:00"


@pytest.fixture
def updated_by() -> AuditEvent:
    """Provide valid updater metadata."""
    return AuditEvent(
        type=AuditEventType.app, value="INTERNAL001", display="Data Migration"
    )


def make_endpoint(organisation_id: UUID, service_id: UUID) -> Endpoint:
    return Endpoint(
        id=uuid4(),
        identifier_oldDoS_id=123,
        status=EndpointStatus.ACTIVE,
        connectionType=EndpointConnectionType.ITK,
        name=None,
        businessScenario=EndpointBusinessScenario.PRIMARY,
        payloadType=EndpointPayloadType.GP_PRIMARY,
        payloadMimeType=EndpointPayloadMimeType.CDA,
        address="https://test.endpoint.com",
        managedByOrganisation=organisation_id,
        service=service_id,
        order=1,
        isCompressionEnabled=False,
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


def test_organisation_excludes_created_datetime(organisation: Organisation) -> None:
    modified = organisation.model_copy(update={"createdTime": datetime(2025, 12, 31)})
    diff = get_organisation_diff(organisation, modified)
    assert len(diff) == 0


def test_organisation_excludes_modified_datetime(organisation: Organisation) -> None:
    modified = organisation.model_copy(update={"lastUpdated": datetime(2025, 12, 31)})
    diff = get_organisation_diff(organisation, modified)
    assert len(diff) == 0


def test_organisation_excludes_endpoint_created_datetime(
    organisation: Organisation,
) -> None:
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(update={"createdTime": datetime(2025, 6, 15)})

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)
    assert len(diff) == 0


def test_organisation_excludes_endpoint_modified_datetime(
    organisation: Organisation,
) -> None:
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(update={"lastUpdated": datetime(2025, 6, 15)})

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)
    assert len(diff) == 0


def test_organisation_detects_endpoint_data_changes(organisation: Organisation) -> None:
    """Endpoint status and address changes are detected."""
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(
        update={"status": EndpointStatus.OFF, "address": "https://changed.endpoint.com"}
    )

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 2  # noqa: PLR2004

    changes = {}
    for change in diff["values_changed"]:
        path = str(change.path())
        changes[path] = {"old": change.t1, "new": change.t2}

    status_path = "root['endpoints'][0]['status']"
    assert status_path in changes
    assert changes[status_path]["old"] == EndpointStatus.ACTIVE.value
    assert changes[status_path]["new"] == EndpointStatus.OFF.value

    address_path = "root['endpoints'][0]['address']"
    assert address_path in changes
    assert changes[address_path]["old"] == "https://test.endpoint.com"
    assert changes[address_path]["new"] == "https://changed.endpoint.com"


def test_organisation_tree_view_has_old_and_new_values(
    organisation: Organisation,
) -> None:
    modified = organisation.model_copy(update={"name": "New Name"})
    diff = get_organisation_diff(organisation, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Organisation"
    assert change.t2 == "New Name"


def test_location_excludes_created_datetime(location: Location) -> None:
    modified = location.model_copy(update={"createdTime": datetime(2025, 12, 31)})
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_excludes_modified_datetime(location: Location) -> None:
    modified = location.model_copy(update={"lastUpdated": datetime(2025, 12, 31)})
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_excludes_both_datetimes(location: Location) -> None:
    modified = location.model_copy(
        update={
            "createdTime": datetime(2025, 1, 1),
            "lastUpdated": datetime(2025, 1, 1),
        }
    )
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_tree_view_has_old_and_new_values(location: Location) -> None:
    modified = location.model_copy(update={"name": "New Name"})
    diff = get_location_diff(location, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Location"
    assert change.t2 == "New Name"


def test_healthcare_service_excludes_created_datetime(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={"createdTime": datetime(2025, 12, 31)}
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)
    assert len(diff) == 0


def test_healthcare_service_excludes_modified_datetime(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={"lastUpdated": datetime(2025, 12, 31)}
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)
    assert len(diff) == 0


def test_healthcare_service_detects_dispositions_order_changes(
    healthcare_service: HealthcareService,
) -> None:
    """Reordering identical dispositions at different positions produces no diff."""

    service1 = healthcare_service.model_copy(
        update={"dispositions": ["DX1", "DX114", "DX200"]}
    )
    service2 = healthcare_service.model_copy(
        update={"dispositions": ["DX200", "DX1", "DX114"]}
    )

    diff = get_healthcare_service_diff(service1, service2)
    assert len(diff) == 0


def test_healthcare_service_detects_sgsd_order_changes(
    healthcare_service: HealthcareService,
) -> None:
    """Reordering identical SGSD objects at different positions produces no diff."""
    sgsd1 = SymptomGroupSymptomDiscriminatorPair(sg=1000, sd=4003)
    sgsd2 = SymptomGroupSymptomDiscriminatorPair(sg=2000, sd=5003)

    service1 = healthcare_service.model_copy(
        update={"symptomGroupSymptomDiscriminators": [sgsd1, sgsd2]}
    )
    service2 = healthcare_service.model_copy(
        update={"symptomGroupSymptomDiscriminators": [sgsd2, sgsd1]}
    )

    diff = get_healthcare_service_diff(service1, service2)

    assert len(diff) == 0


def test_healthcare_service_detects_disposition_changes(
    healthcare_service: HealthcareService,
) -> None:
    service1 = healthcare_service.model_copy(update={"dispositions": ["DX1", "DX114"]})
    service2 = healthcare_service.model_copy(update={"dispositions": ["DX1", "DX999"]})

    diff = get_healthcare_service_diff(service1, service2)

    assert len(diff) > 0
    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['dispositions'][1]"
    assert change.t1 == "DX114"
    assert change.t2 == "DX999"


def test_healthcare_service_tree_view_has_old_and_new_values(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(update={"name": "New Name"})
    diff = get_healthcare_service_diff(healthcare_service, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Healthcare Service"
    assert change.t2 == "New Name"


def test_organisation_detects_changes_but_excludes_datetimes(
    organisation: Organisation,
) -> None:
    """Datetime fields are excluded while other changes are detected."""
    modified = organisation.model_copy(
        update={
            "name": "Changed Name",
            "createdTime": datetime(2025, 1, 1),
            "lastUpdated": datetime(2025, 1, 1),
        }
    )
    diff = get_organisation_diff(organisation, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Organisation"
    assert change.t2 == "Changed Name"


def test_location_detects_changes_but_excludes_datetimes(location: Location) -> None:
    modified = location.model_copy(
        update={
            "name": "Changed Location",
            "createdTime": datetime(2025, 1, 1),
            "lastUpdated": datetime(2025, 1, 1),
        }
    )
    diff = get_location_diff(location, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Location"
    assert change.t2 == "Changed Location"


def test_healthcare_service_detects_changes_but_excludes_datetimes(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={
            "name": "Changed Service",
            "createdTime": datetime(2025, 1, 1),
            "lastUpdated": datetime(2025, 1, 1),
        }
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)

    assert "values_changed" in diff
    assert len(diff["values_changed"]) == 1

    change = list(diff["values_changed"])[0]
    assert str(change.path()) == "root['name']"
    assert change.t1 == "Test Healthcare Service"
    assert change.t2 == "Changed Service"


@pytest.mark.parametrize(
    "initial_expression,expected_prefix",
    [
        ("", "SET #lastUpdated = :lastUpdated, #lastUpdatedBy = :lastUpdatedBy"),
        (
            "SET #name = :name",
            "SET #lastUpdated = :lastUpdated, #lastUpdatedBy = :lastUpdatedBy, ",
        ),
        (
            "REMOVE #field",
            "SET #lastUpdated = :lastUpdated, #lastUpdatedBy = :lastUpdatedBy",
        ),
    ],
)
def test_add_audit_timestamps_to_expressions(
    serializer: TypeSerializer,
    timestamp: str,
    updated_by: AuditEvent,
    initial_expression: str,
    expected_prefix: str,
) -> None:
    """Audit timestamps are correctly added to various expression types."""
    expressions = DynamoDBUpdateExpressions(update_expression=initial_expression)

    expressions.add_audit_timestamps(timestamp, updated_by, serializer)

    assert expressions.update_expression.startswith(expected_prefix)
    assert expressions.expression_attribute_names == {
        "#lastUpdated": "lastUpdated",
        "#lastUpdatedBy": "lastUpdatedBy",
    }
    assert ":lastUpdated" in expressions.expression_attribute_values
    assert ":lastUpdatedBy" in expressions.expression_attribute_values


def test_add_audit_timestamps_empty_timestamp_raises_value_error(
    serializer: TypeSerializer,
    updated_by: AuditEvent,
) -> None:
    """Empty timestamp raises ValueError."""
    expressions = DynamoDBUpdateExpressions()

    with pytest.raises(ValueError, match="timestamp cannot be empty"):
        expressions.add_audit_timestamps("", updated_by, serializer)


def test_add_audit_timestamps_invalid_updater_raises_type_error(
    serializer: TypeSerializer,
    timestamp: str,
) -> None:
    """Non-AuditEvent updater raises ValueError."""
    expressions = DynamoDBUpdateExpressions()

    with pytest.raises(TypeError, match="updated_by must be an AuditEvent instance"):
        expressions.add_audit_timestamps(timestamp, "not_an_audit_event", serializer)


def test_add_audit_timestamps_serializes_correctly(
    serializer: TypeSerializer,
    timestamp: str,
    updated_by: AuditEvent,
) -> None:
    """Audit values are properly serialized to DynamoDB format."""
    expressions = DynamoDBUpdateExpressions()

    expressions.add_audit_timestamps(timestamp, updated_by, serializer)

    assert expressions.expression_attribute_values[":lastUpdated"] == {"S": timestamp}
    assert expressions.expression_attribute_values[":lastUpdatedBy"] == {
        "M": {
            "type": {"S": "app"},
            "value": {"S": "INTERNAL001"},
            "display": {"S": "Data Migration"},
        }
    }
