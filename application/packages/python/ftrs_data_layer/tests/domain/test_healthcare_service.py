from datetime import datetime, time
from uuid import uuid4

import pytest
from ftrs_data_layer.domain import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    DayOfWeek,
    HealthcareService,
    HealthcareServiceTelecom,
    NotAvailable,
    SymptomGroupSymptomDiscriminatorPair,
)
from pydantic import ValidationError


def test_healthcare_service_round_trip_and_types() -> None:
    # Arrange
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
        telecom=HealthcareServiceTelecom(
            phone_public="123456789",
            phone_private="987654321",
            email="example@mail.com",
            web="www.example.com",
        ),
        symptomGroupSymptomDiscriminators=[
            SymptomGroupSymptomDiscriminatorPair(
                sg=1000,
                sd=4003,
            )
        ],
        dispositions=["DX1", "DX114"],
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

    # Act: round-trip via JSON-style dict
    dumped = hs.model_dump(mode="json")
    reloaded = HealthcareService.model_validate(dumped)

    # Assert: stable and deterministic JSON representation
    assert reloaded.model_dump(mode="json") == dumped

    # Assert: union items resolve to the correct concrete types after round-trip
    assert isinstance(reloaded.openingTime[0], AvailableTime)
    assert isinstance(reloaded.openingTime[1], AvailableTime)
    assert isinstance(reloaded.openingTime[2], AvailableTimeVariation)
    assert isinstance(reloaded.openingTime[3], AvailableTimePublicHolidays)
    assert isinstance(reloaded.openingTime[4], NotAvailable)

    # Assert: field values are preserved and canonicalised
    assert reloaded.openingTime[0].dayOfWeek == DayOfWeek.MONDAY
    assert reloaded.openingTime[1].allDay is True
    # Public-holiday entry should only have times, not dates
    assert reloaded.openingTime[3].startTime.isoformat() == "12:30:00"
    assert reloaded.openingTime[3].endTime.isoformat() == "16:30:00"


def test_healthcare_service_invalid_day_of_week_raises() -> None:
    # Arrange: minimal valid payload with an invalid dayOfWeek
    payload = {
        "id": str(uuid4()),
        "identifier_oldDoS_uid": "123456",
        "active": True,
        "category": "GP Services",
        "type": "GP Consultation Service",
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "providedBy": str(uuid4()),
        "location": str(uuid4()),
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Healthcare Service",
        "telecom": {
            "phone_public": "123456789",
            "phone_private": "987654321",
            "email": "example@mail.com",
            "web": "www.example.com",
        },
        "symptomGroupSymptomDiscriminators": [],
        "dispositions": [],
        "openingTime": [
            {
                "category": "availableTime",
                "dayOfWeek": "monday",  # invalid, expected canonical enum like "mon"
                "startTime": "09:00:00",
                "endTime": "17:00:00",
                "allDay": False,
            }
        ],
    }
    # Act / Assert
    with pytest.raises(ValidationError):
        HealthcareService.model_validate(payload)
