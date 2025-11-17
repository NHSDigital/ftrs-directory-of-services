import pytest
from pytest import ExceptionInfo

from ftrs_data_layer.domain.telecom import Telecom
from ftrs_data_layer.domain.enums import TelecomType
from pydantic import ValidationError
from email_validator import EmailNotValidError

def test_telecom() -> None:
    telecom = [
        Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True),
        Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=False),
        Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True),
        Telecom(type=TelecomType.WEB, value="https://www.test.co.uk", isPublic=True),
    ]

    telecoms = [tel.model_dump(mode="json") for tel in telecom]
    assert telecoms == [
        {"type": "phone", "value": "0300 311 22 33", "isPublic": True},
        {"type": "phone", "value": "020 7972 3272", "isPublic": False},
        {"type": "email", "value": "test@nhs.net", "isPublic": True},
        {"type": "web", "value": "https://www.test.co.uk", "isPublic": True},
    ]

def test_telecom_invalid_email() -> None:
    with pytest.raises(ValidationError, match=r".* The part after the @-sign is not valid. It should have a period. .*"):
        telecom = [Telecom(type=TelecomType.EMAIL, value="bad@email", isPublic=True)]

def test_telecom_invalid_web() -> None:
    with pytest.raises(ValidationError):
        telecom = [Telecom(type=TelecomType.WEB, value="bad_website", isPublic=True)]

def test_telecom_invalid_phone() -> None:
    with pytest.raises(ValidationError):
        telecom = [Telecom(type=TelecomType.PHONE, value="123", isPublic=True)]

def test_telecom_valid_phone() -> None:
    telecom = [Telecom(type=TelecomType.PHONE, value="01234 567890", isPublic=True)]
