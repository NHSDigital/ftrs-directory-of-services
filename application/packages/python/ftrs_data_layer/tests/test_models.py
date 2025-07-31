from datetime import UTC, datetime, time
from decimal import Decimal
from uuid import uuid4

import pytest
from freezegun import freeze_time
from ftrs_data_layer.models import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    DayOfWeek,
    Endpoint,
    HealthcareService,
    Location,
    NotAvailable,
    Organisation,
    PositionGCS,
    Telecom,
)
from pytest_mock import MockerFixture


def to_time(time: str) -> time:
    return datetime.strptime(time, "%H:%M:%S").time()


def to_datetime(dt: str) -> time:
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")


def test_organisation() -> None:
    org = Organisation(
        id=uuid4(),
        identifier_ODS_ODSCode="123456",
        active=True,
        name="Test Organisation",
        telecom="123456789",
        type="GP Practice",
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
    )

    assert org.model_dump(mode="json") == {
        "id": str(org.id),
        "identifier_ODS_ODSCode": "123456",
        "active": True,
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Organisation",
        "telecom": "123456789",
        "type": "GP Practice",
        "endpoints": [],
    }

    assert org.indexes == {
        "identifier_ODS_ODSCode": "123456",
    }


@freeze_time("2023-10-01T00:00:00Z")
def test_organisation_from_dos(mocker: MockerFixture) -> None:
    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="d5a852ef-12c7-4014-b398-661716a63027",
    )

    org = Organisation.from_dos(
        data={
            "odscode": "12345",
            "name": "Test Organisation",
            "type": "GP Practice",
            "endpoints": [
                {
                    "id": "67890",
                    "transport": "itk",
                    "businessscenario": "Primary",
                    "interaction": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
                    "format": "FHIR",
                    "address": "https://example.com/endpoint",
                    "endpointorder": 1,
                    "iscompressionenabled": "compressed",
                }
            ],
        }
    )

    assert org.model_dump(mode="json") == {
        "id": "d5a852ef-12c7-4014-b398-661716a63027",
        "identifier_ODS_ODSCode": "12345",
        "active": True,
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Organisation",
        "telecom": None,
        "type": "GP Practice",
        "endpoints": [
            {
                "id": "d5a852ef-12c7-4014-b398-661716a63027",
                "address": "https://example.com/endpoint",
                "connectionType": "itk",
                "description": "Primary",
                "payloadMimeType": "application/fhir",
                "identifier_oldDoS_id": 67890,
                "isCompressionEnabled": True,
                "managedByOrganisation": "d5a852ef-12c7-4014-b398-661716a63027",
                "createdBy": "ROBOT",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "ROBOT",
                "modifiedDateTime": "2023-10-01T00:00:00Z",
                "name": None,
                "order": 1,
                "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
                "service": None,
                "status": "active",
            }
        ],
    }

    assert org.indexes == {
        "identifier_ODS_ODSCode": "12345",
    }


def test_organisation_from_dos_existing_timestamp(mocker: MockerFixture) -> None:
    expected_created_datetime = datetime(2023, 10, 1, 0, 0, 0, tzinfo=UTC)
    expected_modified_datetime = datetime(2023, 11, 1, 0, 0, 0, tzinfo=UTC)

    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="d5a852ef-12c7-4014-b398-661716a63027",
    )

    org = Organisation.from_dos(
        data={
            "odscode": "12345",
            "name": "Test Organisation",
            "type": "GP Practice",
            "endpoints": [],
        },
        created_datetime=expected_created_datetime,
        updated_datetime=expected_modified_datetime,
    )

    assert org.model_dump(mode="json") == {
        "id": "d5a852ef-12c7-4014-b398-661716a63027",
        "identifier_ODS_ODSCode": "12345",
        "active": True,
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-11-01T00:00:00Z",
        "name": "Test Organisation",
        "telecom": None,
        "type": "GP Practice",
        "endpoints": [],
    }


def test_healthcare_service() -> None:
    # Some pregenerated ids for comparison
    id1 = uuid4()
    id2 = uuid4()
    id3 = uuid4()

    hs = HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid="123456",
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        providedBy=uuid4(),
        location=uuid4(),
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Healthcare Service",
        telecom=Telecom(
            phone_public="123456789",
            phone_private="987654321",
            email="example@mail.com",
            web="www.example.com",
        ),
        symptomGroupSymptomDiscriminators={
            "SG_SD": [
                {
                    "sd": {
                        "codeID": 4003,
                        "codeType": "Symptom Discriminator (SD)",
                        "codeValue": "PC full Primary Care assessment and prescribing capability",
                        "id": "SD4003",
                        "source": "pathways",
                        "synonyms": None,
                    },
                    "sg": {
                        "codeID": 1000,
                        "codeType": "Symptom Group (SG)",
                        "codeValue": "Abdominal or Flank Injury, Blunt",
                        "id": "SG1000",
                        "source": "pathways",
                        "zCodeExists": False,
                    },
                }
            ]
        },
        dispositions=[
            {
                "id": "1",
                "source": "pathways",
                "codeType": "Disposition (Dx)",
                "codeID": 301,
                "codeValue": "Dx1",
                "time": 10,
            }
        ],
        openingTime=[
            AvailableTime(
                id=id1,
                dayOfWeek=DayOfWeek.MONDAY,
                startTime=to_time("09:00:00"),
                endTime=to_time("17:00:00"),
            ),
            AvailableTime(
                id=id2,
                dayOfWeek=DayOfWeek.TUESDAY,
                startTime=to_time("00:00:00"),
                endTime=to_time("23:59:59"),
                allDay=True,
            ),
            AvailableTimeVariation(
                id=id3,
                description="staff training",
                startTime=to_datetime("2025-06-10T10:30:00"),
                endTime=to_datetime("2025-06-10T12:30:00"),
            ),
            AvailableTimePublicHolidays(
                id=id2, startTime=to_time("12:30:00"), endTime=to_time("16:30:00")
            ),
            NotAvailable(
                id=id1,
                description="special",
                unavailableDate=to_datetime("2025-07-15T00:00:00"),
            ),
        ],
    )

    assert hs.model_dump(mode="json") == {
        "id": str(hs.id),
        "identifier_oldDoS_uid": "123456",
        "active": True,
        "type": "GP Consultation Service",
        "category": "GP Services",
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "providedBy": str(hs.providedBy),
        "location": str(hs.location),
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Healthcare Service",
        "telecom": {
            "phone_public": "123456789",
            "phone_private": "987654321",
            "email": "example@mail.com",
            "web": "www.example.com",
        },
        "symptomGroupSymptomDiscriminators": {
            "SG_SD": [
                {
                    "sg": {
                        "id": "SG1000",
                        "source": "pathways",
                        "codeType": "Symptom Group (SG)",
                        "codeID": 1000,
                        "codeValue": "Abdominal or Flank Injury, Blunt",
                        "zCodeExists": False,
                    },
                    "sd": {
                        "id": "SD4003",
                        "source": "pathways",
                        "codeType": "Symptom Discriminator (SD)",
                        "codeID": 4003,
                        "codeValue": "PC full Primary Care assessment and prescribing capability",
                        "synonyms": None,
                    },
                }
            ]
        },
        "dispositions": [
            {
                "id": "1",
                "source": "pathways",
                "codeType": "Disposition (Dx)",
                "codeID": 301,
                "codeValue": "Dx1",
                "time": 10,
            }
        ],
        "openingTime": [
            {
                "allDay": False,
                "category": "availableTime",
                "dayOfWeek": "mon",
                "endTime": "17:00:00",
                "id": str(id1),
                "startTime": "09:00:00",
            },
            {
                "allDay": True,
                "category": "availableTime",
                "dayOfWeek": "tue",
                "endTime": "23:59:59",
                "id": str(id2),
                "startTime": "00:00:00",
            },
            {
                "category": "availableTimeVariations",
                "description": "staff training",
                "endTime": "2025-06-10T12:30:00",
                "id": str(id3),
                "startTime": "2025-06-10T10:30:00",
            },
            {
                "category": "availableTimePublicHolidays",
                "endTime": "16:30:00",
                "id": str(id2),
                "startTime": "12:30:00",
            },
            {
                "category": "notAvailable",
                "description": "special",
                "id": str(id1),
                "unavailableDate": "2025-07-15",
            },
        ],
    }

    assert hs.indexes == {}


def test_healthcare_service_from_json() -> None:
    # additional test for opening times to ensure the union is
    #   matching the json values to correct types for openingTimes
    # this functionality is used in the load file, and may be needed to load data into models for writing/updating.

    id1 = uuid4()
    id2 = uuid4()
    id3 = uuid4()

    item = HealthcareService.model_validate(
        {
            "id": str(id1),
            "identifier_oldDoS_uid": "123456",
            "active": True,
            "type": "Primary Care Network Enhanced Access Service",
            "category": "GP Services",
            "createdBy": "test_user",
            "createdDateTime": "2023-10-01T00:00:00Z",
            "providedBy": str(id2),
            "location": str(id3),
            "modifiedBy": "test_user",
            "modifiedDateTime": "2023-10-01T00:00:00Z",
            "name": "Test Healthcare Service",
            "telecom": {
                "phone_public": "123456789",
                "phone_private": "987654321",
                "email": "example@mail.com",
                "web": "www.example.com",
            },
            "symptomGroupSymptomDiscriminators": {
                "SG_SD": [
                    {
                        "sg": {
                            "id": "SG1000",
                            "source": "pathways",
                            "codeType": "Symptom Group (SG)",
                            "codeID": 1000,
                            "codeValue": "Abdominal or Flank Injury, Blunt",
                            "zCodeExists": False,
                        },
                        "sd": {
                            "id": "SD4003",
                            "source": "pathways",
                            "codeType": "Symptom Discriminator (SD)",
                            "codeID": 4003,
                            "codeValue": "PC full Primary Care assessment and prescribing capability",
                            "synonyms": None,
                        },
                    }
                ]
            },
            "dispositions": [
                {
                    "id": "1",
                    "source": "pathways",
                    "codeType": "Disposition (Dx)",
                    "codeID": 301,
                    "codeValue": "Dx1",
                    "time": 10,
                }
            ],
            "openingTime": [
                {
                    "allDay": False,
                    "category": "availableTime",
                    "dayOfWeek": "mon",
                    "endTime": "17:00:00",
                    "id": str(id1),
                    "startTime": "09:00:00",
                },
                {
                    "allDay": True,
                    "category": "availableTime",
                    "dayOfWeek": "tue",
                    "endTime": "23:59:59",
                    "id": str(id2),
                    "startTime": "00:00:00",
                },
                {
                    "category": "availableTimeVariations",
                    "description": "staff training",
                    "endTime": "2025-06-10T12:30:00",
                    "id": str(id3),
                    "startTime": "2025-06-10T10:30:00",
                },
                {
                    "category": "availableTimePublicHolidays",
                    "endTime": "16:30:00",
                    "id": str(id2),
                    "startTime": "12:30:00",
                },
                {
                    "category": "notAvailable",
                    "description": "special",
                    "id": str(id1),
                    "unavailableDate": "2025-07-15",
                },
            ],
        }
    )

    assert item == HealthcareService(
        id=id1,
        identifier_oldDoS_uid="123456",
        active=True,
        category="GP Services",
        type="Primary Care Network Enhanced Access Service",
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        providedBy=id2,
        location=id3,
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Healthcare Service",
        telecom=Telecom(
            phone_public="123456789",
            phone_private="987654321",
            email="example@mail.com",
            web="www.example.com",
        ),
        symptomGroupSymptomDiscriminators={
            "SG_SD": [
                {
                    "sd": {
                        "codeID": 4003,
                        "codeType": "Symptom Discriminator (SD)",
                        "codeValue": "PC full Primary Care assessment and prescribing capability",
                        "id": "SD4003",
                        "source": "pathways",
                        "synonyms": None,
                    },
                    "sg": {
                        "codeID": 1000,
                        "codeType": "Symptom Group (SG)",
                        "codeValue": "Abdominal or Flank Injury, Blunt",
                        "id": "SG1000",
                        "source": "pathways",
                        "zCodeExists": False,
                    },
                }
            ]
        },
        dispositions=[
            {
                "id": "1",
                "source": "pathways",
                "codeType": "Disposition (Dx)",
                "codeID": 301,
                "codeValue": "Dx1",
                "time": 10,
            }
        ],
        openingTime=[
            AvailableTime(
                id=id1,
                dayOfWeek=DayOfWeek.MONDAY,
                startTime=to_time("09:00:00"),
                endTime=to_time("17:00:00"),
            ),
            AvailableTime(
                id=id2,
                dayOfWeek=DayOfWeek.TUESDAY,
                startTime=to_time("00:00:00"),
                endTime=to_time("23:59:59"),
                allDay=True,
            ),
            AvailableTimeVariation(
                id=id3,
                description="staff training",
                startTime=to_datetime("2025-06-10T10:30:00"),
                endTime=to_datetime("2025-06-10T12:30:00"),
            ),
            AvailableTimePublicHolidays(
                id=id2, startTime=to_time("12:30:00"), endTime=to_time("16:30:00")
            ),
            NotAvailable(
                id=id1,
                description="special",
                unavailableDate=to_datetime("2025-07-15T00:00:00"),
            ),
        ],
    )


@freeze_time("2023-10-01T00:00:00Z")
def test_healthcare_service_from_dos(mocker: MockerFixture) -> None:
    expected_created_datetime = datetime(2023, 10, 1, 0, 0, 0, tzinfo=UTC)
    expected_modified_datetime = datetime(2023, 11, 1, 0, 0, 0, tzinfo=UTC)

    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="d5a852ef-12c7-4014-b398-661716a63027",
    )

    organisation_id = "9bb0f952-ab23-4398-a9b8-e2a6b3896107"
    location_id = "9bb0f952-ab23-4398-a9b8-1234567890ab"

    hs = HealthcareService.from_dos(
        data={
            "uid": "12345",
            "name": "test GP consulting service",
            "publicphone": "09876543210",
            "nonpublicphone": "12345678901",
            "email": "test@nhs.net",
            "web": "abc.co.uk",
            "type": "GP Practice",
            "sg_sd_pairs": '{"sg" : {"id" : "SG1000", "source" : "pathways", "codeType" : "Symptom Group (SG)", "codeID" : 1000, "codeValue" : "Abdominal or Flank Injury, Blunt", "zCodeExists" : false}, "sd" : {"id" : "SD4003", "source" : "pathways", "codeType" : "Symptom Discriminator (SD)", "codeID" : 4003, "codeValue" : "PC full Primary Care assessment and prescribing capability", "synonyms" : null}}',
            "dispositions": '{"id": "1", "source": "pathways", "codeType": "Disposition (Dx)", "codeID": 301, "codeValue": "Dx1", "dispositiontime": 10}',
            "availability": {
                "availableTime": [],
                "availableTimePublicHolidays": [],
                "availableTimeVariations": [],
                "notAvailable": [],
            },
        },
        created_datetime=expected_created_datetime,
        updated_datetime=expected_modified_datetime,
        organisation_id=organisation_id,
        location_id=location_id,
    )

    assert hs.model_dump(mode="json") == {
        "id": "d5a852ef-12c7-4014-b398-661716a63027",
        "identifier_oldDoS_uid": "12345",
        "active": True,
        "category": "GP Services",
        "providedBy": organisation_id,
        "location": "9bb0f952-ab23-4398-a9b8-1234567890ab",
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-11-01T00:00:00Z",
        "name": "test GP consulting service",
        "telecom": {
            "phone_public": "09876543210",
            "phone_private": "12345678901",
            "email": "test@nhs.net",
            "web": "abc.co.uk",
        },
        "type": "GP Consultation Service",
        "openingTime": None,
        "symptomGroupSymptomDiscriminators": {
            "SG_SD": [
                {
                    "sg": {
                        "id": "SG1000",
                        "source": "pathways",
                        "codeType": "Symptom Group (SG)",
                        "codeID": 1000,
                        "codeValue": "Abdominal or Flank Injury, Blunt",
                        "zCodeExists": False,
                    },
                    "sd": {
                        "id": "SD4003",
                        "source": "pathways",
                        "codeType": "Symptom Discriminator (SD)",
                        "codeID": 4003,
                        "codeValue": "PC full Primary Care assessment and prescribing capability",
                        "synonyms": None,
                    },
                }
            ]
        },
        "dispositions": [
            {
                "id": "1",
                "source": "pathways",
                "codeType": "Disposition (Dx)",
                "codeID": 301,
                "codeValue": "Dx1",
                "time": 10,
            }
        ],
    }

    assert hs.indexes == {}


def test_location() -> None:
    loc = Location(
        id=uuid4(),
        active=True,
        address=Address(
            street="123 Main St",
            postcode="AB12 3CD",
            town="Test Town",
        ),
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        managingOrganisation=uuid4(),
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Location",
        positionGCS=PositionGCS(
            latitude=Decimal("51.5074"), longitude=Decimal("-0.1278")
        ),
        positionReferenceNumber_UPRN=1234567890,
        positionReferenceNumber_UBRN=9876543210,
        primaryAddress=True,
        partOf=None,
    )

    assert loc.model_dump(mode="json") == {
        "id": str(loc.id),
        "active": True,
        "address": {
            "street": "123 Main St",
            "town": "Test Town",
            "postcode": "AB12 3CD",
        },
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "managingOrganisation": str(loc.managingOrganisation),
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Location",
        "positionGCS": {"latitude": "51.5074", "longitude": "-0.1278"},
        "positionReferenceNumber_UPRN": 1234567890,
        "positionReferenceNumber_UBRN": 9876543210,
        "primaryAddress": True,
        "partOf": None,
    }


@freeze_time("2023-10-01T00:00:00Z")
def test_location_from_dos(mocker: MockerFixture) -> None:
    expected_created_datetime = datetime(2023, 10, 1, 0, 0, 0, tzinfo=UTC)
    expected_modified_datetime = datetime(2023, 11, 1, 0, 0, 0, tzinfo=UTC)

    mocker.patch(
        "ftrs_data_layer.models.uuid4",
        return_value="d5a852ef-12c7-4014-b398-661716a63027",
    )

    organisation_id = "9bb0f952-ab23-4398-a9b8-e2a6b3896107"

    hs = Location.from_dos(
        data={
            "address": "123 fake road",
            "town": "thingyplace",
            "postcode": "AB123CD",
            "latitude": Decimal("0.123456"),
            "longitude": Decimal("-0.123456"),
        },
        created_datetime=expected_created_datetime,
        updated_datetime=expected_modified_datetime,
        organisation_id=organisation_id,
    )

    assert hs.model_dump(mode="json") == {
        "id": "d5a852ef-12c7-4014-b398-661716a63027",
        "address": {
            "street": "123 fake road",
            "town": "thingyplace",
            "postcode": "AB123CD",
        },
        "positionGCS": {
            "latitude": "0.123456",
            "longitude": "-0.123456",
        },
        "active": True,
        "managingOrganisation": organisation_id,
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-11-01T00:00:00Z",
        "name": None,
        "partOf": None,
        "positionReferenceNumber_UBRN": None,
        "positionReferenceNumber_UPRN": None,
        "primaryAddress": True,
    }

    assert hs.indexes == {}


def test_endpoint() -> None:
    endpoint = Endpoint(
        id=uuid4(),
        identifier_oldDoS_id=123456,
        status="active",
        connectionType="itk",
        description="Copy",
        payloadMimeType="application/fhir",
        identifier_oldDoS_uid="123456",
        isCompressionEnabled=True,
        managedByOrganisation=uuid4(),
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Endpoint Name",
        payloadType="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        service=None,
        address="https://example.com/endpoint",
        order=1,
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "itk",
        "description": "Copy",
        "payloadMimeType": "application/fhir",
        "isCompressionEnabled": True,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Endpoint Name",
        "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        "service": None,
        "address": "https://example.com/endpoint",
        "order": 1,
    }


@freeze_time("2023-10-01T00:00:00Z")
def test_endpoint_from_dos() -> None:
    endpoint = Endpoint.from_dos(
        data={
            "id": 123456,
            "transport": "itk",
            "businessscenario": "Primary",
            "interaction": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
            "format": "FHIR",
            "address": "https://example.com/endpoint",
            "endpointorder": 1,
            "iscompressionenabled": "uncompressed",
        },
        managed_by_id=uuid4(),
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "itk",
        "description": "Primary",
        "payloadMimeType": "application/fhir",
        "isCompressionEnabled": False,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": None,
        "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        "service": None,
        "address": "https://example.com/endpoint",
        "order": 1,
    }

    assert endpoint.indexes == {}


@freeze_time("2023-10-01T00:00:00Z")
def test_endpoint_from_dos_telno_transport() -> None:
    endpoint = Endpoint.from_dos(
        data={
            "id": 123456,
            "transport": "telno",
            "businessscenario": "Primary",
            "interaction": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
            "format": "FHIR",
            "address": "01234567890",
            "endpointorder": 1,
            "iscompressionenabled": "uncompressed",
        },
        managed_by_id=uuid4(),
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "telno",
        "description": "Primary",
        "payloadMimeType": None,
        "isCompressionEnabled": False,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": None,
        "payloadType": None,
        "service": None,
        "address": "01234567890",
        "order": 1,
    }

    assert endpoint.indexes == {}


@freeze_time("2023-10-01T00:00:00Z")
@pytest.mark.parametrize(
    "format_value, expected_payload_mime_type",
    [
        ("PDF", "application/pdf"),
        ("HTML", "text/html"),
        ("FHIR", "application/fhir"),
        ("email", "message/rfc822"),
        ("telno", "text/vcard"),
        ("xml", "xml"),
    ],
)
def test_endpoint_from_dos_format_mapping(
    format_value: str, expected_payload_mime_type: str
) -> None:
    endpoint = Endpoint.from_dos(
        data={
            "id": 123456,
            "transport": "itk",
            "businessscenario": "Primary",
            "interaction": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
            "format": format_value,
            "address": "01234567890",
            "endpointorder": 1,
            "iscompressionenabled": "uncompressed",
        },
        managed_by_id=uuid4(),
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "itk",
        "description": "Primary",
        "payloadMimeType": expected_payload_mime_type,
        "isCompressionEnabled": False,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": None,
        "payloadType": "urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        "service": None,
        "address": "01234567890",
        "order": 1,
    }

    assert endpoint.indexes == {}


def test_telecom() -> None:
    telecom = Telecom(
        phone_public="00000000000",
        phone_private="12345678901#EXT0123",
        email="test@nhs.net",
        web="ww.test.co.u",
    )

    assert telecom.model_dump(mode="json") == {
        "phone_public": "00000000000",
        "phone_private": "12345678901#EXT0123",
        "email": "test@nhs.net",
        "web": "ww.test.co.u",
    }


def test_Address() -> None:
    address = Address(
        street="123 Main St",
        postcode="AB12 3CD",
        town="Test Town",
    )

    assert address.model_dump(mode="json") == {
        "street": "123 Main St",
        "postcode": "AB12 3CD",
        "town": "Test Town",
    }


def test_PositionGCS() -> None:
    position = PositionGCS(latitude=Decimal("51.5074"), longitude=Decimal("-0.1278"))

    assert position.model_dump(mode="json") == {
        "latitude": "51.5074",
        "longitude": "-0.1278",
    }


def test_PositionGCS_error_Nonetypes() -> None:
    position = PositionGCS.from_dos(latitude=Decimal("nan"), longitude=Decimal("nan"))
    assert position is None

    with pytest.raises(ValueError, match="provide both latitude and longitude"):
        position = PositionGCS.from_dos(
            latitude=Decimal("51.5074"), longitude=Decimal("nan")
        )

    with pytest.raises(ValueError, match="provide both latitude and longitude"):
        position = PositionGCS.from_dos(
            latitude=Decimal("nan"), longitude=Decimal("-0.1278")
        )

    position = PositionGCS.from_dos(
        latitude=Decimal("51.5074"), longitude=Decimal("-0.1278")
    )
    assert position == PositionGCS(
        latitude=Decimal("51.5074"), longitude=Decimal("-0.1278")
    )

    position = PositionGCS.from_dos(latitude=None, longitude=None)
    assert position is None
