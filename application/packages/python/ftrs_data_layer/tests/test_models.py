from datetime import datetime, time
from decimal import Decimal
from uuid import uuid4

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
                startTime=to_datetime("2025-07-15T00:00:00"),
                endTime=to_datetime("2025-07-15T23:59:59"),
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
                "startTime": "2025-07-15T00:00:00",
                "endTime": "2025-07-15T23:59:59",
            },
        ],
    }


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
                    "startTime": "2025-07-15T00:00:00",
                    "endTime": "2025-07-15T23:59:59",
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
                startTime=to_datetime("2025-07-15T00:00:00"),
                endTime=to_datetime("2025-07-15T23:59:59"),
            ),
        ],
    )


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
