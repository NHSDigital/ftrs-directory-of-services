import pytest
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import BaseModel


class DummyModel(BaseModel):
    foo: str


def test_validate_success() -> None:
    resource = {"foo": "bar"}
    result = FhirValidator.validate(resource, DummyModel)
    assert isinstance(result, DummyModel)
    assert result.foo == "bar"


def test_validate_failure(caplog: pytest.LogCaptureFixture) -> None:
    resource = {"foo": 123}
    with caplog.at_level("WARNING"):
        with pytest.raises(OperationOutcomeException):
            FhirValidator.validate(resource, DummyModel)
        assert "FHIR validation failed for resource DummyModel" in caplog.text
