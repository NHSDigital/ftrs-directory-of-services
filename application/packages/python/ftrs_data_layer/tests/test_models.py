from uuid import uuid4

from ftrs_data_layer.models import HealthcareService, Location, Organisation


def test_organisation() -> None:
    org = Organisation(
        id=uuid4(),
        identifier_ODS_ODSCode="123456",
        active=True,
        name="Test Organisation",
        telecom="123456789",
        type="NHS",
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
        "type": "NHS",
        "endpoints": [],
    }


def test_healthcare_service() -> None:
    hs = HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid="123456",
        active=True,
        category="General Practice",
        type="General Practice",
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        providedBy=uuid4(),
        location=uuid4(),
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Healthcare Service",
        telecom_phone_public="123456789",
        telecom_phone_private="987654321",
        telecom_email="example@mail.com",
        telecom_web="www.example.com",
    )

    assert hs.model_dump(mode="json") == {
        "id": str(hs.id),
        "identifier_oldDoS_uid": "123456",
        "active": True,
        "type": "General Practice",
        "category": "General Practice",
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "providedBy": str(hs.providedBy),
        "location": str(hs.location),
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Healthcare Service",
        "telecom_phone_public": "123456789",
        "telecom_phone_private": "987654321",
        "telecom_email": "example@mail.com",
        "telecom_web": "www.example.com",
    }


def test_location() -> None:
    loc = Location(
        id=uuid4(),
        active=True,
        address_street="123 Main St",
        address_postcode="AB12 3CD",
        address_town="Test Town",
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        managingOrganisation=uuid4(),
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Location",
        positionGCS_latitude=51.5074,
        positionGCS_longitude=-0.1278,
        positionGCS_easting=123456,
        positionGCS_northing=654321,
        positionReferenceNumber_UPRN=1234567890,
        positionReferenceNumber_UBRN=9876543210,
        primaryAddress=True,
        partOf=None,
    )

    assert loc.model_dump(mode="json") == {
        "id": str(loc.id),
        "active": True,
        "address_street": "123 Main St",
        "address_postcode": "AB12 3CD",
        "address_town": "Test Town",
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "managingOrganisation": str(loc.managingOrganisation),
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Location",
        "positionGCS_latitude": 51.5074,
        "positionGCS_longitude": -0.1278,
        "positionGCS_easting": 123456,
        "positionGCS_northing": 654321,
        "positionReferenceNumber_UPRN": 1234567890,
        "positionReferenceNumber_UBRN": 9876543210,
        "primaryAddress": True,
        "partOf": None,
    }
