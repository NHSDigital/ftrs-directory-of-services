from uuid import uuid4

from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.enums import TelecomType
from ftrs_data_layer.domain.telecom import Telecom


def test_organisation() -> None:
    org = Organisation(
        id=uuid4(),
        identifier_ODS_ODSCode="123456",
        identifier_oldDoS_uid="test_UUID",
        active=True,
        name="Test GP Organisation",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True),
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=False),
            Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True),
            Telecom(
                type=TelecomType.WEB, value="https://test-site.nhs.net", isPublic=True
            ),
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
        "identifier_oldDoS_uid": "test_UUID",
        "active": True,
        "createdBy": "test_user",
        "createdDateTime": "2023-10-01T00:00:00Z",
        "modifiedBy": "test_user",
        "modifiedDateTime": "2023-10-01T00:00:00Z",
        "name": "Test GP Organisation",
        "telecom": [
            {"type": "phone", "value": "020 7972 3272", "isPublic": True},
            {"type": "phone", "value": "0300 311 22 33", "isPublic": False},
            {"type": "email", "value": "test@nhs.net", "isPublic": True},
            {"type": "web", "value": "https://test-site.nhs.net", "isPublic": True},
        ],
        "type": "GP Practice",
        "endpoints": [],
        "legalDates": None,
    }
