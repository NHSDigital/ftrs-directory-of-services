from datetime import UTC, datetime
from uuid import uuid4

import pytest
from freezegun import freeze_time
from pydantic_core import ValidationError
from pytest_mock import MockerFixture

from ftrs_data_layer.models import (
    Address,
    Endpoint,
    HealthcareService,
    Location,
    Organisation,
    PositionGCS,
    Telecom,
)


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
                    "interaction": "urn:nhs:example:interaction",
                    "format": "xml",
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
                "format": "xml",
                "identifier_oldDoS_id": 67890,
                "isCompressionEnabled": True,
                "managedByOrganisation": "d5a852ef-12c7-4014-b398-661716a63027",
                "createdBy": "ROBOT",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "ROBOT",
                "modifiedDateTime": "2023-10-01T00:00:00Z",
                "name": None,
                "order": 1,
                "payloadType": "urn:nhs:example:interaction",
                "service": None,
                "status": "active",
            }
        ],
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
        telecom=Telecom(
            phone_public="123456789",
            phone_private="987654321",
            email="example@mail.com",
            web="www.example.com",
        ),
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
        "telecom": {
            "phone_public": "123456789",
            "phone_private": "987654321",
            "email": "example@mail.com",
            "web": "www.example.com",
        },
    }


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
        "category": "unknown",
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
        "type": "GP Practice",
    }


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
        positionGCS=PositionGCS(latitude="51.5074", longitude="-0.1278"),
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
        "positionGCS": {"latitude": float("51.5074"), "longitude": float("-0.1278")},
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
            "latitude": "0.123456",
            "longitude": "-0.123456",
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
            "latitude": float("0.123456"),
            "longitude": float("-0.123456"),
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


def test_endpoint() -> None:
    endpoint = Endpoint(
        id=uuid4(),
        identifier_oldDoS_id=123456,
        status="active",
        connectionType="itk",
        description="Test Endpoint",
        format="xml",
        identifier_oldDoS_uid="123456",
        isCompressionEnabled=True,
        managedByOrganisation=uuid4(),
        createdBy="test_user",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="test_user",
        modifiedDateTime="2023-10-01T00:00:00Z",
        name="Test Endpoint Name",
        payloadType="urn:nhs:example:interaction",
        service=None,
        address="https://example.com/endpoint",
        order=1,
    )

    assert endpoint.model_dump(mode="json") == {
        "id": str(endpoint.id),
        "identifier_oldDoS_id": 123456,
        "status": "active",
        "connectionType": "itk",
        "description": "Test Endpoint",
        "format": "xml",
        "isCompressionEnabled": True,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test Endpoint Name",
        "payloadType": "urn:nhs:example:interaction",
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
            "interaction": "urn:nhs:example:interaction",
            "format": "xml",
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
        "format": "xml",
        "isCompressionEnabled": False,
        "managedByOrganisation": str(endpoint.managedByOrganisation),
        "createdBy": "ROBOT",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "ROBOT",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": None,
        "payloadType": "urn:nhs:example:interaction",
        "service": None,
        "address": "https://example.com/endpoint",
        "order": 1,
    }


@freeze_time("2023-10-01T00:00:00Z")
def test_endpoint_from_dos_telno_transport() -> None:
    endpoint = Endpoint.from_dos(
        data={
            "id": 123456,
            "transport": "telno",
            "businessscenario": "Primary",
            "interaction": "urn:nhs:example:interaction",
            "format": "xml",
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
        "format": None,
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
    position = PositionGCS(latitude="51.5074", longitude="-0.1278")

    assert position.model_dump(mode="json") == {
        "latitude": float("51.5074"),
        "longitude": float("-0.1278"),
    }


def test_PositionGCS_error_Nonetypes() -> None:
    position = PositionGCS.from_dos(latitude=None, longitude=None)
    assert position is None

    with pytest.raises(ValidationError):
        position = PositionGCS.from_dos(latitude="51.5074", longitude=None)

    with pytest.raises(ValidationError):
        position = PositionGCS.from_dos(latitude=None, longitude="-0.1278")

    position = PositionGCS.from_dos(latitude="51.5074", longitude="-0.1278")
    assert position == PositionGCS(latitude="51.5074", longitude="-0.1278")
