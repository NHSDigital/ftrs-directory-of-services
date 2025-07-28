from decimal import Decimal
from uuid import uuid4

from ftrs_data_layer.domain import Address, Location, PositionGCS


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
            latitude=Decimal("51.5074"),
            longitude=Decimal("-0.1278"),
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
