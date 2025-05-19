import pytest
from organisations.models import OrganisationPayload
from pydantic import ValidationError


def test_valid_payload():
    payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ROBOT",
    }
    organisation = OrganisationPayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.active is False
    assert organisation.telecom == "0123456789"
    assert organisation.type == "GP Practice"
    assert organisation.modified_by == "ROBOT"


@pytest.mark.parametrize(
    "name, telecom, type, modified_by",
    [
        ("aa" * 100, "0123456789", "GP Practice", "ROBOT"),
        ("name", "00" * 20, "GP Practice", "ROBOT"),
        ("name", "0123456789", "aa" * 100, "ROBOT"),
        ("name", "0123456789", "GP Practice", "aa" * 100),
    ],
)
def test_field_too_long(name, telecom, type, modified_by):
    payload = {
        "name": name,
        "active": False,
        "telecom": telecom,
        "type": type,
        "modified_by": modified_by
    }
    with pytest.raises(ValidationError) as e:
        OrganisationPayload(**payload)
    assert "string_too_long" in str(e.value)

def test_missing_required_field():
    payload = {
        "name": "Test Organisation",
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ROBOT",
    }
    with pytest.raises(ValidationError) as e:
        OrganisationPayload(**payload)
    assert "validation error" in str(e.value)


def test_additional_field():
    payload = {
        "name": "Test Organisation",
        "active": False,
        "telecom": "0123456789",
        "type": "GP Practice",
        "modified_by": "ROBOT",
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError) as e:
        OrganisationPayload(**payload)
    assert "Extra inputs are not permitted" in str(e.value)
