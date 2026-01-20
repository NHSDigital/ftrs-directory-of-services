from datetime import datetime
from uuid import UUID, uuid4

import pytest
from ftrs_data_layer.domain import (
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
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

from common.diff_utils import (
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
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
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
