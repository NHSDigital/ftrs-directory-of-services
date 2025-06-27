from pydantic import BaseModel, ValidationError
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
import pytest


class DummyModel(BaseModel):
    @classmethod
    def model_validate(cls, resource):
        if resource.get("fail"):
            raise ValidationError(
                [
                    {
                        "loc": ("fail",),
                        "msg": "Forced failure",
                        "type": "value_error",
                    }
                ],
                cls,
            )
        return "validated"


def test_validate_success():
    resource = {"foo": "bar"}
    result = FhirValidator.validate(resource, DummyModel)
    assert result == "validated"


def test_validate_failure(mocker):
    resource = {"fail": True}
    mock_outcome = object()
    mock_handler = mocker.patch(
        "ftrs_common.fhir.fhir_validator.OperationOutcomeHandler.from_validation_error",
        return_value=mock_outcome,
    )
    fake_error = mocker.Mock()
    fake_error.__str__ = lambda self: "Fake error"
    mock_validate.side_effect = ValidationError([fake_error], model=SomeModel)
    with pytest.raises(OperationOutcomeException) as exc:
        FhirValidator.validate(resource, DummyModel)
    assert exc.value.outcome is mock_outcome
    mock_handler.assert_called_once()
