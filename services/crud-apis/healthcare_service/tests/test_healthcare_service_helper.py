import uuid
from datetime import UTC, datetime, time
from typing import NoReturn
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest
from freezegun import freeze_time
from ftrs_data_layer.enums import DayOfWeek
from ftrs_data_layer.models import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    HealthcareService,
    NotAvailable,
    Telecom,
)
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from healthcare_service.app.services.healthcare_service_helper import (
    apply_updates,
    create_healthcare_service,
    get_outdated_fields,
)

FIXED_CREATED_TIME = datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)
FIXED_MODIFIED_TIME = datetime(2023, 12, 16, 12, 0, 0, tzinfo=UTC)


def test_create_healthcare_service_successful() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    test_service = HealthcareService(
        identifier_oldDoS_uid=None,
        active=True,
        category="GP Services",
        type="Primary Care Network Enhanced Access Service",
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=None,
        openingTime=None,
    )
    response = create_healthcare_service(
        healthcare_service=test_service, repository=mock_repository
    )

    assert response.id is not None
    assert isinstance(response.id, uuid4().__class__)
    assert response.name == test_service.name
    assert response.type == test_service.type
    mock_repository.create.assert_called_once_with(test_service)


def test_create_healthcare_service_invalid_healthcare_service() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    invalid_service = None  # Representing an invalid HealthcareService instance

    with pytest.raises(AttributeError):
        create_healthcare_service(
            healthcare_service=invalid_service, repository=mock_repository
        )


def test_create_healthcare_service_repository_error() -> NoReturn:
    mock_repository = Mock(spec=AttributeLevelRepository)
    test_service = HealthcareService(
        identifier_oldDoS_uid=None,
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        providedBy=uuid4(),
        location=uuid4(),
        name="Test Healthcare Service",
        telecom=None,
        openingTime=None,
    )
    mock_repository.create.side_effect = Exception("Repository error")

    with pytest.raises(Exception) as exc_info:
        create_healthcare_service(
            healthcare_service=test_service, repository=mock_repository
        )

    assert str(exc_info.value) == "Repository error"
    mock_repository.create.assert_called_once_with(test_service)


def to_time(time: str) -> time:
    return datetime.strptime(time, "%H:%M:%S").time()


def to_datetime(dt: str) -> time:
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")


def get_mock_service() -> HealthcareService:
    id1 = uuid4()
    id2 = uuid4()
    id3 = uuid4()
    return HealthcareService(
        id="26104435-409f-433d-aca7-a6822ab956b0",
        identifier_oldDoS_uid="123456",
        active=True,
        category="GP Services",
        type="GP Consultation Service",
        createdBy="test_user",
        createdDateTime=FIXED_CREATED_TIME,
        providedBy="26104435-409f-433d-aca7-a6822ab956c0",
        location="26104435-409f-433d-aca7-a6822ab956d0",
        modifiedBy="test_user",
        modifiedDateTime=FIXED_MODIFIED_TIME,
        name="Test Healthcare Service",
        telecom=Telecom(
            phone_public="123456789",
            phone_private="987654321",
            email="example@mail.com",
            web="www.example.com",
        ),
        openingTime=[
            AvailableTime(
                id="64fdcbc1-ec4b-49c6-9e1f-b93b69ad6109",
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


def test_get_outdated_fields_no_changes() -> None:
    service = get_mock_service()
    payload = MagicMock(
        model_dump=lambda: {
            "identifier_oldDoS_uid": "123456",
            "active": True,
            "type": "GP Consultation Service",
            "category": "GP Services",
            "createdBy": "test_user",
            "createdDateTime": FIXED_CREATED_TIME,
            "providedBy": uuid.UUID("26104435-409f-433d-aca7-a6822ab956c0"),
            "location": uuid.UUID("26104435-409f-433d-aca7-a6822ab956d0"),
            "modifiedBy": "test_user",
            "modifiedDateTime": FIXED_MODIFIED_TIME,
            "name": "Test Healthcare Service",
        }
    )

    result = get_outdated_fields(service, payload)

    assert result == {}


def test_apply_updates_with_modified_by_and_two_fields() -> None:
    service = get_mock_service()
    updates = {
        "name": "Updated service name",
        "telecom": {
            "phone_public": "987654321",
        },
        "modified_by": "UserX",
    }

    with patch(
        "healthcare_service.app.services.healthcare_service_helper.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)
        apply_updates(service, updates)

    assert service.name == "Updated service name"
    assert service.telecom == {"phone_public": "987654321"}
    assert service.modifiedBy == "UserX"
    assert service.modifiedDateTime == datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)


@freeze_time(FIXED_MODIFIED_TIME)
def test_get_outdated_fields_with_changes() -> None:
    service = get_mock_service()
    payload = MagicMock(
        model_dump=lambda: {
            "active": False,
            "name": "Updated Healthcare Service",
            "telecom": {
                "phone_public": "123456789",
                "phone_private": "987654321",
                "email": "updatedexample@mail.com",
                "web": None,
            },
            "type": "Primary Care Network Enhanced Access Service",
            "category": "GP Services",
            "providedBy": uuid.UUID("26104435-409f-433d-aca7-a6822ab956c0"),
            "location": uuid.UUID("26104435-409f-433d-aca7-a6822ab956d0"),
            "modified_by": "ETL_ODS_PIPELINE",
            "openingTime": {
                "allDay": False,
                "category": "availableTime",
                "dayOfWeek": "mon",
                "endTime": "17:00:00",
                "id": "64fdcbc1-ec4b-49c6-9e1f-b93b69ad6109",
                "startTime": "09:00:00",
            },
        }
    )

    result = get_outdated_fields(service, payload)

    assert result == {
        "active": False,
        "type": "Primary Care Network Enhanced Access Service",
        "modified_by": "ETL_ODS_PIPELINE",
        "name": "Updated Healthcare Service",
        "telecom": {
            "phone_public": "123456789",
            "phone_private": "987654321",
            "email": "updatedexample@mail.com",
            "web": None,
        },
        "openingTime": {
            "allDay": False,
            "category": "availableTime",
            "dayOfWeek": "mon",
            "endTime": "17:00:00",
            "id": "64fdcbc1-ec4b-49c6-9e1f-b93b69ad6109",
            "startTime": "09:00:00",
        },
    }
