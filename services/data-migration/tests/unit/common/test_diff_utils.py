"""Tests for common/diff_utils.py module."""

from datetime import UTC, datetime
from uuid import UUID

from ftrs_data_layer.domain import (
    Address,
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
    Telecom,
)
from ftrs_data_layer.domain.enums import TelecomType

from common.diff_utils import (
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)


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
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
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
