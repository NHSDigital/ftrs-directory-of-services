<<<<<<< HEAD
"""Tests for common/diff_utils.py module."""

from datetime import UTC, datetime
from uuid import UUID

from ftrs_data_layer.domain import (
    Address,
=======
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from ftrs_data_layer.domain import (
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
<<<<<<< HEAD
    Telecom,
)
from ftrs_data_layer.domain.enums import TelecomType
=======
    SymptomGroupSymptomDiscriminatorPair,
)
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
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))

from common.diff_utils import (
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)


<<<<<<< HEAD
def create_test_organisation(name: str = "Test Organisation") -> Organisation:
    """Create a test organisation with standard values."""
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
    """Create a test location with standard values."""
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
    """Create a test healthcare service with standard values."""
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
=======
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
        createdBy="test_user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedBy="test_user",
        modifiedDateTime=datetime(2023, 1, 1),
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
        createdBy="test_user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedBy="test_user",
        modifiedDateTime=datetime(2023, 1, 1),
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
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
<<<<<<< HEAD
        createdBy="DATA_MIGRATION",
        createdDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime=datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC),
    )


def test_get_organisation_diff_no_changes() -> None:
    """Test that identical organisations produce no diff."""
    org1 = create_test_organisation()
    org2 = org1.model_copy(deep=True)

    diff = get_organisation_diff(org1, org2)

    assert not diff, "Identical organisations should produce no diff"


def test_get_organisation_diff_ignores_timestamps() -> None:
    """Test that differences in created/modified timestamps are ignored."""
    org1 = create_test_organisation()
    org2 = org1.model_copy(deep=True)
    org2.createdDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    org2.modifiedDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)

    diff = get_organisation_diff(org1, org2)

    assert not diff, "Timestamp differences should be ignored"


def test_get_organisation_diff_name_change() -> None:
    """Test that name changes are detected."""
    org1 = create_test_organisation(name="Old Name")
    org2 = org1.model_copy(deep=True)
    org2.name = "New Name"

    diff = get_organisation_diff(org1, org2)

    assert diff, "Name change should be detected"
    assert "values_changed" in diff
    assert "root['name']" in str(diff)


def test_get_organisation_diff_active_status_change() -> None:
    """Test that active status changes are detected."""
    org1 = create_test_organisation()
    org2 = org1.model_copy(deep=True)
    org2.active = False

    diff = get_organisation_diff(org1, org2)

    assert diff, "Active status change should be detected"
    assert "values_changed" in diff


def test_get_organisation_diff_telecom_changes() -> None:
    """Test that telecom changes are detected."""
    org1 = create_test_organisation()
    org2 = org1.model_copy(deep=True)
    org2.telecom = [
        Telecom(type=TelecomType.PHONE, value="02087654321", isPublic=False)
    ]

    diff = get_organisation_diff(org1, org2)

    assert diff, "Telecom changes should be detected"


def test_get_organisation_diff_multiple_changes() -> None:
    """Test that multiple simultaneous changes are detected."""
    org1 = create_test_organisation(name="Original Name")
    org2 = org1.model_copy(deep=True)
    org2.name = "Updated Name"
    org2.active = False
    org2.identifier_ODS_ODSCode = "B54321"

    diff = get_organisation_diff(org1, org2)

    assert diff, "Multiple changes should be detected"
    diff_str = str(diff)
    assert "name" in diff_str
    assert "active" in diff_str
    assert "identifier_ODS_ODSCode" in diff_str


def test_get_location_diff_no_changes() -> None:
    """Test that identical locations produce no diff."""
    loc1 = create_test_location()
    loc2 = loc1.model_copy(deep=True)

    diff = get_location_diff(loc1, loc2)

    assert not diff, "Identical locations should produce no diff"


def test_get_location_diff_ignores_timestamps() -> None:
    """Test that differences in created/modified timestamps are ignored."""
    loc1 = create_test_location()
    loc2 = loc1.model_copy(deep=True)
    loc2.createdDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    loc2.modifiedDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)

    diff = get_location_diff(loc1, loc2)

    assert not diff, "Timestamp differences should be ignored"


def test_get_location_diff_name_change() -> None:
    """Test that location name changes are detected."""
    loc1 = create_test_location(name="Old Location")
    loc2 = loc1.model_copy(deep=True)
    loc2.name = "New Location"

    diff = get_location_diff(loc1, loc2)

    assert diff, "Name change should be detected"
    assert "values_changed" in diff


def test_get_location_diff_address_change() -> None:
    """Test that address changes are detected."""
    loc1 = create_test_location()
    loc2 = loc1.model_copy(deep=True)
    loc2.address.line1 = "456 New Street"
    loc2.address.postcode = "XY98 7ZW"

    diff = get_location_diff(loc1, loc2)

    assert diff, "Address changes should be detected"
    diff_str = str(diff)
    assert "line1" in diff_str or "address" in diff_str


def test_get_location_diff_active_status_change() -> None:
    """Test that location active status changes are detected."""
    loc1 = create_test_location()
    loc2 = loc1.model_copy(deep=True)
    loc2.active = False

    diff = get_location_diff(loc1, loc2)

    assert diff, "Active status change should be detected"


def test_get_location_diff_managing_organisation_change() -> None:
    """Test that managing organisation changes are detected."""
    loc1 = create_test_location()
    loc2 = loc1.model_copy(deep=True)
    loc2.managingOrganisation = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")

    diff = get_location_diff(loc1, loc2)

    assert diff, "Managing organisation change should be detected"


def test_get_healthcare_service_diff_no_changes() -> None:
    """Test that identical healthcare services produce no diff."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)

    diff = get_healthcare_service_diff(svc1, svc2)

    assert not diff, "Identical healthcare services should produce no diff"


def test_get_healthcare_service_diff_ignores_timestamps() -> None:
    """Test that differences in created/modified timestamps are ignored."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.createdDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    svc2.modifiedDateTime = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)

    diff = get_healthcare_service_diff(svc1, svc2)

    assert not diff, "Timestamp differences should be ignored"


def test_get_healthcare_service_diff_name_change() -> None:
    """Test that service name changes are detected."""
    svc1 = create_test_healthcare_service(name="Old Service")
    svc2 = svc1.model_copy(deep=True)
    svc2.name = "New Service"

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "Name change should be detected"
    assert "values_changed" in diff


def test_get_healthcare_service_diff_active_status_change() -> None:
    """Test that active status changes are detected."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.active = False

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "Active status change should be detected"


def test_get_healthcare_service_diff_telecom_changes() -> None:
    """Test that telecom changes are detected."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.telecom.phone_public = "09876543210"
    svc2.telecom.email = "new@example.com"

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "Telecom changes should be detected"


def test_get_healthcare_service_diff_category_type_changes() -> None:
    """Test that category and type changes are detected."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.category = "Emergency Services"
    svc2.type = "Urgent Care Service"

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "Category and type changes should be detected"
    diff_str = str(diff)
    assert "category" in diff_str or "type" in diff_str


def test_get_healthcare_service_diff_location_change() -> None:
    """Test that location changes are detected."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.location = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "Location change should be detected"


def test_get_healthcare_service_diff_provided_by_change() -> None:
    """Test that providedBy changes are detected."""
    svc1 = create_test_healthcare_service()
    svc2 = svc1.model_copy(deep=True)
    svc2.providedBy = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")

    diff = get_healthcare_service_diff(svc1, svc2)

    assert diff, "ProvidedBy change should be detected"


def test_diff_utils_ignore_order() -> None:
    """Test that diff functions ignore order in lists."""
    org1 = create_test_organisation()
    org1.telecom = [
        Telecom(type=TelecomType.PHONE, value="01234567890", isPublic=True),
        Telecom(type=TelecomType.PHONE, value="02012345678", isPublic=False),
    ]

    org2 = org1.model_copy(deep=True)
    org2.telecom = [
        Telecom(type=TelecomType.PHONE, value="02012345678", isPublic=False),
        Telecom(type=TelecomType.PHONE, value="01234567890", isPublic=True),
    ]

    diff = get_organisation_diff(org1, org2)

    assert not diff, "Reordered identical lists should produce no diff"
=======
        createdBy="test_user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedBy="test_user",
        modifiedDateTime=datetime(2023, 1, 1),
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
        createdBy="test_user",
        createdDateTime=datetime(2023, 1, 1),
        modifiedBy="test_user",
        modifiedDateTime=datetime(2023, 1, 1),
    )


def test_organisation_excludes_created_datetime(organisation: Organisation) -> None:
    modified = organisation.model_copy(
        update={"createdDateTime": datetime(2025, 12, 31)}
    )
    diff = get_organisation_diff(organisation, modified)
    assert len(diff) == 0


def test_organisation_excludes_modified_datetime(organisation: Organisation) -> None:
    modified = organisation.model_copy(
        update={"modifiedDateTime": datetime(2025, 12, 31)}
    )
    diff = get_organisation_diff(organisation, modified)
    assert len(diff) == 0


def test_organisation_excludes_endpoint_created_datetime(
    organisation: Organisation,
) -> None:
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(update={"createdDateTime": datetime(2025, 6, 15)})

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)
    assert len(diff) == 0


def test_organisation_excludes_endpoint_modified_datetime(
    organisation: Organisation,
) -> None:
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(update={"modifiedDateTime": datetime(2025, 6, 15)})

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)
    assert len(diff) == 0


def test_organisation_detects_endpoint_data_changes(organisation: Organisation) -> None:
    service_id = uuid4()
    endpoint1 = make_endpoint(organisation.id, service_id)
    endpoint2 = endpoint1.model_copy(
        update={"status": EndpointStatus.OFF, "address": "https://changed.endpoint.com"}
    )

    org1 = organisation.model_copy(update={"endpoints": [endpoint1]})
    org2 = organisation.model_copy(update={"endpoints": [endpoint2]})

    diff = get_organisation_diff(org1, org2)

    assert "values_changed" in diff
    changed_paths = [str(item.path()) for item in diff["values_changed"]]
    assert any("status" in path for path in changed_paths)
    assert any("address" in path for path in changed_paths)


def test_organisation_tree_view_has_old_and_new_values(
    organisation: Organisation,
) -> None:
    modified = organisation.model_copy(update={"name": "New Name"})
    diff = get_organisation_diff(organisation, modified)

    assert "values_changed" in diff
    change = list(diff["values_changed"])[0]
    assert change.t1 == "Test Organisation"
    assert change.t2 == "New Name"


def test_location_excludes_created_datetime(location: Location) -> None:
    modified = location.model_copy(update={"createdDateTime": datetime(2025, 12, 31)})
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_excludes_modified_datetime(location: Location) -> None:
    modified = location.model_copy(update={"modifiedDateTime": datetime(2025, 12, 31)})
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_excludes_both_datetimes(location: Location) -> None:
    modified = location.model_copy(
        update={
            "createdDateTime": datetime(2025, 1, 1),
            "modifiedDateTime": datetime(2025, 1, 1),
        }
    )
    diff = get_location_diff(location, modified)
    assert len(diff) == 0


def test_location_tree_view_has_old_and_new_values(location: Location) -> None:
    modified = location.model_copy(update={"name": "New Name"})
    diff = get_location_diff(location, modified)

    assert "values_changed" in diff
    change = list(diff["values_changed"])[0]
    assert change.t1 == "Test Location"
    assert change.t2 == "New Name"


def test_healthcare_service_excludes_created_datetime(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={"createdDateTime": datetime(2025, 12, 31)}
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)
    assert len(diff) == 0


def test_healthcare_service_excludes_modified_datetime(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={"modifiedDateTime": datetime(2025, 12, 31)}
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)
    assert len(diff) == 0


def test_healthcare_service_ignores_dispositions_order(
    healthcare_service: HealthcareService,
) -> None:
    service1 = healthcare_service.model_copy(
        update={"dispositions": ["DX1", "DX114", "DX200"]}
    )
    service2 = healthcare_service.model_copy(
        update={"dispositions": ["DX200", "DX1", "DX114"]}
    )

    diff = get_healthcare_service_diff(service1, service2)
    assert len(diff) == 0


def test_healthcare_service_ignores_sgsd_order(
    healthcare_service: HealthcareService,
) -> None:
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
    change = list(diff["values_changed"])[0]
    assert change.t1 == "DX114"
    assert change.t2 == "DX999"


def test_healthcare_service_tree_view_has_old_and_new_values(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(update={"name": "New Name"})
    diff = get_healthcare_service_diff(healthcare_service, modified)

    assert "values_changed" in diff
    change = list(diff["values_changed"])[0]
    assert change.t1 == "Test Healthcare Service"
    assert change.t2 == "New Name"


def test_organisation_detects_changes_but_excludes_datetimes(
    organisation: Organisation,
) -> None:
    modified = organisation.model_copy(
        update={
            "name": "Changed Name",
            "createdDateTime": datetime(2025, 1, 1),
            "modifiedDateTime": datetime(2025, 1, 1),
        }
    )
    diff = get_organisation_diff(organisation, modified)

    assert "values_changed" in diff
    changed_paths = [str(item.path()) for item in diff["values_changed"]]
    assert any("name" in path for path in changed_paths)
    assert not any("createdDateTime" in path for path in changed_paths)
    assert not any("modifiedDateTime" in path for path in changed_paths)


def test_location_detects_changes_but_excludes_datetimes(location: Location) -> None:
    modified = location.model_copy(
        update={
            "name": "Changed Location",
            "createdDateTime": datetime(2025, 1, 1),
            "modifiedDateTime": datetime(2025, 1, 1),
        }
    )
    diff = get_location_diff(location, modified)

    assert "values_changed" in diff
    changed_paths = [str(item.path()) for item in diff["values_changed"]]
    assert any("name" in path for path in changed_paths)
    assert not any("createdDateTime" in path for path in changed_paths)
    assert not any("modifiedDateTime" in path for path in changed_paths)


def test_healthcare_service_detects_changes_but_excludes_datetimes(
    healthcare_service: HealthcareService,
) -> None:
    modified = healthcare_service.model_copy(
        update={
            "name": "Changed Service",
            "createdDateTime": datetime(2025, 1, 1),
            "modifiedDateTime": datetime(2025, 1, 1),
        }
    )
    diff = get_healthcare_service_diff(healthcare_service, modified)

    assert "values_changed" in diff
    changed_paths = [str(item.path()) for item in diff["values_changed"]]
    assert any("name" in path for path in changed_paths)
    assert not any("createdDateTime" in path for path in changed_paths)
    assert not any("modifiedDateTime" in path for path in changed_paths)
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
