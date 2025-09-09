from datetime import datetime, time
from uuid import uuid4

from ftrs_data_layer.domain import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    DayOfWeek,
    Disposition,
    HealthcareService,
    NotAvailable,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
    Telecom,
)


def test_healthcare_service() -> None:
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
        symptomGroupSymptomDiscriminators=[
            {
                "sd": {
                    "codeID": 4003,
                    "codeType": "Symptom Discriminator (SD)",
                    "codeValue": "PC full Primary Care assessment and prescribing capability",
                    "id": "df046f42-42bc-46ca-a6f0-db496e9a1292",
                    "source": "pathways",
                    "synonyms": [],
                },
                "sg": {
                    "codeID": 1000,
                    "codeType": "Symptom Group (SG)",
                    "codeValue": "Abdominal or Flank Injury, Blunt",
                    "id": "b4d7ceba-77b8-4966-803a-d8291bd7e804",
                    "source": "pathways",
                },
            }
        ],
        dispositions=[
            {
                "id": "39b75651-e40e-4214-b308-8a58cf8046ce",
                "source": "pathways",
                "codeType": "Disposition (Dx)",
                "codeID": 301,
                "codeValue": "Dx1",
                "time": 10,
            }
        ],
        openingTime=[
            AvailableTime(
                dayOfWeek=DayOfWeek.MONDAY,
                startTime=time.fromisoformat("09:00:00"),
                endTime=time.fromisoformat("17:00:00"),
            ),
            AvailableTime(
                dayOfWeek=DayOfWeek.TUESDAY,
                startTime=time.fromisoformat("00:00:00"),
                endTime=time.fromisoformat("23:59:59"),
                allDay=True,
            ),
            AvailableTimeVariation(
                description="staff training",
                startTime=datetime.fromisoformat("2025-06-10T10:30:00"),
                endTime=datetime.fromisoformat("2025-06-10T12:30:00"),
            ),
            AvailableTimePublicHolidays(
                startTime=time.fromisoformat("12:30:00"),
                endTime=time.fromisoformat("16:30:00"),
            ),
            NotAvailable(
                description="special",
                startTime=datetime.fromisoformat("2025-07-15T00:00:00"),
                endTime=datetime.fromisoformat("2025-07-15T23:59:59"),
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
        "migrationNotes": None,
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Healthcare Service",
        "telecom": {
            "phone_public": "123456789",
            "phone_private": "987654321",
            "email": "example@mail.com",
            "web": "www.example.com",
        },
        "symptomGroupSymptomDiscriminators": [
            {
                "sg": {
                    "id": "b4d7ceba-77b8-4966-803a-d8291bd7e804",
                    "source": "pathways",
                    "codeType": "Symptom Group (SG)",
                    "codeID": 1000,
                    "codeValue": "Abdominal or Flank Injury, Blunt",
                },
                "sd": {
                    "id": "df046f42-42bc-46ca-a6f0-db496e9a1292",
                    "source": "pathways",
                    "codeType": "Symptom Discriminator (SD)",
                    "codeID": 4003,
                    "codeValue": "PC full Primary Care assessment and prescribing capability",
                    "synonyms": [],
                },
            }
        ],
        "dispositions": [
            {
                "id": "39b75651-e40e-4214-b308-8a58cf8046ce",
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
                "startTime": "09:00:00",
            },
            {
                "allDay": True,
                "category": "availableTime",
                "dayOfWeek": "tue",
                "endTime": "23:59:59",
                "startTime": "00:00:00",
            },
            {
                "category": "availableTimeVariations",
                "description": "staff training",
                "endTime": "2025-06-10T12:30:00",
                "startTime": "2025-06-10T10:30:00",
            },
            {
                "category": "availableTimePublicHolidays",
                "endTime": "16:30:00",
                "startTime": "12:30:00",
            },
            {
                "category": "notAvailable",
                "description": "special",
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
            "symptomGroupSymptomDiscriminators": [
                {
                    "sg": {
                        "id": "869B79E9-4298-496A-BE89-56ECB8AFB4EA",
                        "source": "pathways",
                        "codeType": "Symptom Group (SG)",
                        "codeID": 1000,
                        "codeValue": "Abdominal or Flank Injury, Blunt",
                    },
                    "sd": {
                        "id": "F379E2BD-FCE2-4385-B119-B8596D15E235",
                        "source": "pathways",
                        "codeType": "Symptom Discriminator (SD)",
                        "codeID": 4003,
                        "codeValue": "PC full Primary Care assessment and prescribing capability",
                        "synonyms": [],
                    },
                }
            ],
            "dispositions": [
                {
                    "id": "3007FF04-9834-4A9B-B2A9-49CDB269F622",
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
        symptomGroupSymptomDiscriminators=[
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    codeID=1000,
                    codeType="Symptom Group (SG)",
                    codeValue="Abdominal or Flank Injury, Blunt",
                    id="869B79E9-4298-496A-BE89-56ECB8AFB4EA",
                    source="pathways",
                ),
                sd=SymptomDiscriminator(
                    codeID=4003,
                    codeType="Symptom Discriminator (SD)",
                    codeValue="PC full Primary Care assessment and prescribing capability",
                    id="F379E2BD-FCE2-4385-B119-B8596D15E235",
                    source="pathways",
                    synonyms=[],
                ),
            )
        ],
        dispositions=[
            Disposition(
                id="3007FF04-9834-4A9B-B2A9-49CDB269F622",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=301,
                codeValue="Dx1",
                time=10,
            )
        ],
        openingTime=[
            AvailableTime(
                id=id1,
                dayOfWeek=DayOfWeek.MONDAY,
                startTime=time.fromisoformat("09:00:00"),
                endTime=time.fromisoformat("17:00:00"),
            ),
            AvailableTime(
                id=id2,
                dayOfWeek=DayOfWeek.TUESDAY,
                startTime=time.fromisoformat("00:00:00"),
                endTime=time.fromisoformat("23:59:59"),
                allDay=True,
            ),
            AvailableTimeVariation(
                id=id3,
                description="staff training",
                startTime=datetime.fromisoformat("2025-06-10T10:30:00"),
                endTime=datetime.fromisoformat("2025-06-10T12:30:00"),
            ),
            AvailableTimePublicHolidays(
                id=id2,
                startTime=time.fromisoformat("12:30:00"),
                endTime=time.fromisoformat("16:30:00"),
            ),
            NotAvailable(
                id=id1,
                description="special",
                startTime=datetime.fromisoformat("2025-07-15T00:00:00"),
                endTime=datetime.fromisoformat("2025-07-15T23:59:59"),
            ),
        ],
    )


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
