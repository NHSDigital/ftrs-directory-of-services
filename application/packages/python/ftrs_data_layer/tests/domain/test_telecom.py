import pytest
from ftrs_data_layer.domain.enums import TelecomType
from ftrs_data_layer.domain.telecom import Telecom
from pydantic import ValidationError


def test_telecom() -> None:
    """
    Test to check a full list of expected telecoms for a given Organisation or HealthcareService
    Additional proof the following data standards (happy paths):
    - Tel-003 Telecom type field is a string (when the model is dumped to json)
    - Tel-011 Telecom isPublic field is a boolean
    - Tel-021 and Tel-022 Telecom value can be set to a valid string UK phone number
    - Tel-024 & Tel-025 Telecom value can be set to a valid string email address
    - Tel-026 & Tel-027 Telecom value can be set to a valid web address
    """
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


def test_telecom_string_representation() -> None:
    """
    Test the string representation of the Telecom class.
    """
    telecom = Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
    assert str(telecom) == "Telecom(type=phone,value=0300 311 22 33,isPublic=True)"


@pytest.mark.parametrize(
    "email",
    [
        ("invalidemail.com"),
        ("plainaddress"),
        ("john..test@example.com "),
        ("@missinglocal.com"),
        ("username@.leadingdot.com"),
        ("user@invalid_domain.com"),
        ("user@domain"),
        ("user@domain.c"),
    ],
)
def test_telecom_invalid_email(email: str) -> None:
    """
    Tel-024 & Tel-025 data standard requirement proof
    This check that a given email address is flagged invalid if it isn't a valid str email address
    """
    with pytest.raises(
        ValidationError,
        match=r".* The part after the @-sign is not valid. It should have a period. .*",
    ):
        Telecom(type=TelecomType.EMAIL, value="bad@email", isPublic=True)


@pytest.mark.parametrize(
    "web",
    [
        ("bad_website.com"),
        ("http://exa mple.com"),
    ],
)
def test_telecom_invalid_web(web: str) -> None:
    """
    Tel-026 data standard requirement proof
    This check that a given web url is flagged invalid if it isn't a valid urn
    """
    with pytest.raises(ValidationError):
        Telecom(type=TelecomType.WEB, value=web, isPublic=True)


@pytest.mark.parametrize(
    "phone, expected_error_field",
    [
        ("+++ABC123", "invalid characters in phone number"),  # invalid characters
        ("12345", "value is not a valid phone number"),  # too short
        ("+9991234567890", "value is not a valid phone number"),  # invalid country code
        (
            "+1 415-555-2671x1234",
            "invalid characters in phone number",
        ),  # extension not allowed
        (
            "+1415555267",
            "value is not a valid phone number",
        ),  # valid US number but invalid for GB region
        (
            "++14155552671",
            "value is not from a supported region",
        ),  # malformed plus signs
        ("+00000000000", "value is not a valid phone number"),  # non-existent number
        ("@0300 311 22 33", "invalid characters in phone number"),  # invalid characters
        ("0300-311-2233", "invalid characters in phone number"),  # invalid characters
        ("<020 7972 327", "invalid characters in phone number"),  # invalid characters
        ("020;7972;3272", "invalid characters in phone number"),  # invalid characters
        ("020,7972,3272", "invalid characters in phone number"),  # invalid characters
        ("0300_311_2234", "invalid characters in phone number"),  # invalid characters
    ],
)
def test_telecom_invalid_phone(phone: str, expected_error_field: str) -> None:
    """
    Covers Tel-021,Tel-022, and Tel-023 data standard requirement
    Check any phone number that is not on the ofcom list of valid numbers
    or has any character not in this list: 1-9, +, (, ), space is marked as invalid
    """
    with pytest.raises(ValidationError) as exc_info:
        Telecom(type=TelecomType.PHONE, value=phone, isPublic=True)
    assert expected_error_field in str(exc_info.value)


def test_telecom_type_cannot_be_changed() -> None:
    """
    Tel-001 data standard requirement proof
    This test checks a Telecom object's type cannot be change after initialization.
    """
    telecom = Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True)
    telecom.value = "https://www.test.co.uk"
    telecom.isPublic = False
    with pytest.raises(ValidationError, match=r".*Field is frozen*"):
        telecom.type = TelecomType.WEB


def test_telecom_not_none_type() -> None:
    """
    Tel-002 data standard requirement proof
    This test checks a Telecom object's type cannot be set to none
    """
    with pytest.raises(
        ValidationError, match=r".*Input should be 'phone', 'email' or 'web'.*"
    ):
        Telecom(type=None, value="test", isPublic=True)


def test_telecom_not_none_ispublic() -> None:
    """
    Tel-010 data standard requirement proof
    This test checks a Telecom object's isPublic cannot be set to none
    """
    with pytest.raises(ValidationError, match=r".*Input should be a valid boolean.*"):
        Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=None)


def test_telecom_not_none_value() -> None:
    """
    Tel-020 data standard requirement proof
    This test checks a Telecom object's value cannot be set to none
    """
    with pytest.raises(ValidationError, match=r".*Input should be a valid string.*"):
        Telecom(type=TelecomType.EMAIL, value=None, isPublic=True)


def test_telecom_none_type() -> None:
    """
    This test checks a Telecom object's type cannot be set to a null enum value
    """
    with pytest.raises(
        ValidationError, match=r".*Input should be 'phone', 'email' or 'web'.*"
    ):
        Telecom(type=None, value="test", isPublic=True)


def test_telecom_type_enum_from_fhir_value_unset_type() -> None:
    """
    This this checks that passing a unset valid telecom type from FHIR raises a ValueError
    """
    with pytest.raises(
        ValueError, match=r"Telecom type \(system\) cannot be None or empty"
    ):
        TelecomType.from_fhir_value(None)
