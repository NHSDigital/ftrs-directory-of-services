import re
from decimal import Decimal
from uuid import UUID, uuid4

from ftrs_data_layer.domain import Address, Location, PositionGCS


def test_location() -> None:
    loc = Location(
        id=uuid4(),
        active=True,
        address=Address(
            line1="123 Main St",
            line2=None,
            county="Test County",
            town="Test Town",
            postcode="AB12 3CD",
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

    dumped = loc.model_dump(mode="json")

    # --- Key presence checks ---
    expected_keys = {
        "id",
        "active",
        "address",
        "createdBy",
        "createdDateTime",
        "managingOrganisation",
        "modifiedBy",
        "modifiedDateTime",
        "name",
        "positionGCS",
        "positionReferenceNumber_UPRN",
        "positionReferenceNumber_UBRN",
        "primaryAddress",
        "partOf",
    }
    assert expected_keys.issubset(dumped.keys())

    # --- Type checks ---
    UUID(dumped["id"])  # must be valid UUID string
    UUID(dumped["managingOrganisation"])  # must be valid UUID string
    assert isinstance(dumped["active"], bool)
    assert isinstance(dumped["name"], str)

    # --- Address checks ---
    assert "county" in dumped["address"]
    assert "postcode" in dumped["address"]
    assert re.match(r"^[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}$", dumped["address"]["postcode"])

    # --- Position checks ---
    assert "latitude" in dumped["positionGCS"]
    assert "longitude" in dumped["positionGCS"]
    assert isinstance(dumped["positionGCS"]["latitude"], str)
    assert isinstance(dumped["positionGCS"]["longitude"], str)


def test_Address() -> None:
    address = Address(
        line1="123 Main St",
        line2=None,
        county=None,
        town="Test Town",
        postcode="AB12 3CD",
    )

    assert address.model_dump(mode="json") == {
        "line1": "123 Main St",
        "line2": None,
        "county": None,
        "town": "Test Town",
        "postcode": "AB12 3CD",
    }


def test_PositionGCS() -> None:
    position = PositionGCS(latitude=Decimal("51.5074"), longitude=Decimal("-0.1278"))

    assert position.model_dump(mode="json") == {
        "latitude": "51.5074",
        "longitude": "-0.1278",
    }
