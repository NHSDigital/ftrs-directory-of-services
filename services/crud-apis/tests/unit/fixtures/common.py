from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from ftrs_data_layer.domain import HealthcareService, Location, Organisation, Telecom
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
    TelecomType,
)
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

FIXED_CREATED_TIME = datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)
ORGANISATION_ID = UUID("00000000-0000-0000-0000-00000000000a")
LOCATION_ID = UUID("10000000-0000-0000-0000-00000000000a")
SERVICE_ID = UUID("20000000-0000-0000-0000-00000000000a")


def make_fhir_organisation_payload(
    organisation_id: str,
    name: str = "Test Org",
    telecom_system: str = "phone",
    telecom_value: str = "0300 311 22 33",
) -> dict[str, Any]:
    return {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ODS1",
            }
        ],
        "active": True,
        "name": name,
        "telecom": [
            {
                "system": telecom_system,
                "value": telecom_value,
                "use": "work",
            }
        ],
    }


@pytest.fixture
def logger_mock() -> MagicMock:
    return MagicMock()


@pytest.fixture
def org_repository_mock() -> MagicMock:
    return MagicMock(spec=AttributeLevelRepository)


@pytest.fixture
def location_repository_mock() -> MagicMock:
    return MagicMock(spec=AttributeLevelRepository)


@pytest.fixture
def healthcare_repository_mock() -> MagicMock:
    return MagicMock(spec=AttributeLevelRepository)


@pytest.fixture
def sample_organisation() -> Organisation:
    return Organisation(
        id=ORGANISATION_ID,
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "app",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_CREATED_TIME,
    )


@pytest.fixture
def sample_location() -> Location:
    return Location(
        id=LOCATION_ID,
        active=True,
        managingOrganisation=ORGANISATION_ID,
        name="Main Site",
        address={
            "line1": "1 Test Street",
            "line2": None,
            "county": "Testshire",
            "town": "Testville",
            "postcode": "TE1 1ST",
        },
        positionGCS={"latitude": Decimal("51.501"), "longitude": Decimal("-0.141")},
        positionReferenceNumber_UPRN=None,
        positionReferenceNumber_UBRN=None,
        partOf=None,
        primaryAddress=True,
        createdBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
        lastUpdatedBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
    )


@pytest.fixture
def sample_healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=SERVICE_ID,
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=ORGANISATION_ID,
        location=LOCATION_ID,
        name="Urgent GP Service",
        telecom={
            "phone_public": "0208 883 5555",
            "phone_private": "0208 111 2222",
            "email": "example@nhs.net",
            "web": "https://example.nhs.uk",
        },
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
        createdBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
        lastUpdatedBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
    )
