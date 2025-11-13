from uuid import uuid4

from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.telecom import Telecom
from ftrs_data_layer.domain.enums import TelecomType


def test_organisation() -> None:
    org = Organisation(
        id=uuid4(),
        identifier_ODS_ODSCode="123456",
        active=True,
        name="Test Organisation",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="123456789", isPublic=True),
            Telecom(type=TelecomType.PHONE, value="987654321", isPublic=False),
            Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True),
            Telecom(type=TelecomType.WEB, value="test-site.nhs.net", isPublic=True),
        ],
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
        "telecom": [
            {"type": "phone", "value": "123456789", "isPublic": True},
            {"type": "phone", "value": "987654321", "isPublic": False},
            {"type": "email", "value": "test@nhs.net", "isPublic": True},
            {"type": "web", "value": "test-site.nhs.net", "isPublic": True},
        ],
        "type": "GP Practice",
        "endpoints": [],
    }
