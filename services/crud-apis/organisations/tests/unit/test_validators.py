import pytest

from organisations.validators import (
    NAME_EMPTY_ERROR,
    UpdatePayloadValidator,
)


def test_update_payload_validator_valid_details() -> None:
    payload = UpdatePayloadValidator(
        name="NHS Digital",
        modified_by="test_user",
        type="NHS",
        active=True,
        telecom="123456789",
    )
    assert payload.name == "NHS Digital"
    assert payload.modified_by == "test_user"
    assert payload.type == "NHS"
    assert payload.telecom == "123456789"
    assert payload.active is True


def test_update_payload_validator_empty_name() -> None:
    with pytest.raises(ValueError, match=NAME_EMPTY_ERROR):
        UpdatePayloadValidator(
            name="   ",
            modified_by="test_user",
            type="NHS",
            active=True,
            telecom="123456789",
        )
