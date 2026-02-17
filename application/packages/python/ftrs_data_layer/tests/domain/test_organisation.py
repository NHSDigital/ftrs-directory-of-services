from uuid import uuid4

from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.domain.enums import TelecomType
from ftrs_data_layer.domain.telecom import Telecom


def test_organisation() -> None:
    created_by = AuditEvent(
        type=AuditEventType.user, value="test_user", display="Test User"
    )
    modified_by = AuditEvent(
        type=AuditEventType.user, value="test_user", display="Test User"
    )

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
        createdBy=created_by,
        created="2023-10-01T00:00:00Z",
        lastUpdatedBy=modified_by,
        lastUpdated="2023-10-01T00:00:00Z",
    )

    assert org.model_dump(mode="json") == {
        "id": str(org.id),
        "identifier_ODS_ODSCode": "123456",
        "identifier_oldDoS_uid": "test_UUID",
        "active": True,
        "createdBy": {"type": "user", "value": "test_user", "display": "Test User"},
        "lastUpdatedBy": {"type": "user", "value": "test_user", "display": "Test User"},
        "created": "2023-10-01T00:00:00Z",
        "lastUpdated": "2023-10-01T00:00:00Z",
        "non_primary_role_codes": [],
        "primary_role_code": None,
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


def test_organisation_no_type() -> None:
    created_by = AuditEvent(
        type=AuditEventType.user, value="test_user", display="Test User"
    )
    modified_by = AuditEvent(
        type=AuditEventType.user, value="test_user", display="Test User"
    )

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
        createdBy=created_by,
        created="2023-10-01T00:00:00Z",
        lastUpdatedBy=modified_by,
        lastUpdated="2023-10-01T00:00:00Z",
    )

    assert org.model_dump(mode="json") == {
        "id": str(org.id),
        "identifier_ODS_ODSCode": "123456",
        "identifier_oldDoS_uid": "test_UUID",
        "active": True,
        "createdBy": {"type": "user", "value": "test_user", "display": "Test User"},
        "lastUpdatedBy": {"type": "user", "value": "test_user", "display": "Test User"},
        "created": "2023-10-01T00:00:00Z",
        "lastUpdated": "2023-10-01T00:00:00Z",
        "non_primary_role_codes": [],
        "primary_role_code": None,
        "name": "Test GP Organisation",
        "telecom": [
            {"type": "phone", "value": "020 7972 3272", "isPublic": True},
            {"type": "phone", "value": "0300 311 22 33", "isPublic": False},
            {"type": "email", "value": "test@nhs.net", "isPublic": True},
            {"type": "web", "value": "https://test-site.nhs.net", "isPublic": True},
        ],
        "type": None,
        "endpoints": [],
        "legalDates": None,
    }
