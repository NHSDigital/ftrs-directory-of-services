import pytest

from organisations.validators import (
    NAME_EMPTY_ERROR,
    UpdatePayloadValidator,
)


def test_update_payload_validator_valid_name() -> None:
    payload = UpdatePayloadValidator(name="NHS Digital")
    assert payload.name == "NHS Digital"


def test_update_payload_validator_empty_name() -> None:
    with pytest.raises(ValueError, match=NAME_EMPTY_ERROR):
        UpdatePayloadValidator(name="   ")
