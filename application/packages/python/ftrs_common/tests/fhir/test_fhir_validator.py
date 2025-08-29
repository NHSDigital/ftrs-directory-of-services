import typing

import pytest
from fhir.resources.R4B.organization import Organization
from ftrs_common.fhir.fhir_validator import FhirValidator
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import BaseModel


class DummyModel(BaseModel):
    resourceType: str = "DummyResource"
    foo: str


def assert_operation_outcome(
    error: OperationOutcomeException,
    expected_code: str,
    expected_severity: str,
    expected_diagnostics: str,
) -> None:
    assert error.outcome["issue"][0]["code"] == expected_code
    assert error.outcome["issue"][0]["severity"] == expected_severity
    assert error.outcome["issue"][0]["diagnostics"] == expected_diagnostics


@pytest.mark.parametrize(
    "resource,model,assertions",
    [
        (
            {
                "resourceType": "Organization",
                "active": True,
                "name": "Test Organization",
            },
            Organization,
            lambda result: (
                isinstance(result, Organization)
                and result.active is True
                and result.name == "Test Organization"
            ),
        ),
    ],
)
def test_validate_success(
    resource: dict, model: type, assertions: typing.Callable[[object], bool]
) -> None:
    result = FhirValidator.validate(resource, model)
    assert assertions(result)


@pytest.mark.parametrize(
    "invalid_input,model",
    [
        ("not a dict", Organization),
        (123, Organization),
        (["list", "not", "dict"], Organization),
        (None, Organization),
        ("not a dict", DummyModel),
        (123, DummyModel),
        (["list", "not", "dict"], DummyModel),
        (None, DummyModel),
    ],
)
def test_validate_not_a_dict(
    caplog: pytest.LogCaptureFixture, invalid_input: object, model: type
) -> None:
    """Test validation fails when resource is not a dictionary."""
    with caplog.at_level("WARNING"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            FhirValidator.validate(invalid_input, model)  # type: ignore
        error = exc_info.value
        assert_operation_outcome(
            error,
            expected_code="structure",
            expected_severity="error",
            expected_diagnostics="Invalid request body: must be a JSON object",
        )


@pytest.mark.parametrize("model", [Organization, DummyModel])
def test_validate_missing_resource_type(
    caplog: pytest.LogCaptureFixture, model: type
) -> None:
    resource = {}
    with caplog.at_level("WARNING"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            FhirValidator.validate(resource, model)
        error = exc_info.value
        assert_operation_outcome(
            error,
            expected_code="structure",
            expected_severity="error",
            expected_diagnostics="Missing required field 'resourceType'",
        )


@pytest.mark.parametrize(
    "resource,model,expected_type",
    [
        (
            {"resourceType": "Patient", "active": True, "name": "Test Organization"},
            Organization,
            "Organization",
        ),
    ],
)
def test_validate_wrong_resource_type(
    caplog: pytest.LogCaptureFixture, resource: dict, model: type, expected_type: str
) -> None:
    """Test validation fails when resourceType is wrong."""
    with caplog.at_level("WARNING"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            FhirValidator.validate(resource, model)
        error = exc_info.value
        assert_operation_outcome(
            error,
            expected_code="structure",
            expected_severity="error",
            expected_diagnostics=f"Invalid resourceType: must be '{expected_type}'",
        )


@pytest.mark.parametrize(
    "resource,model",
    [
        # Organization: 'active' should be a boolean
        (
            {
                "resourceType": "Organization",
                "active": "not a boolean",
                "name": "Test Organization",
            },
            Organization,
        ),
        # DummyModel: 'foo' should be a string, so pass an int
        (
            {"resourceType": "DummyResource", "foo": 123},
            DummyModel,
        ),
    ],
)
def test_validate_fhir_validation_error(
    caplog: pytest.LogCaptureFixture, resource: dict, model: type
) -> None:
    with caplog.at_level("WARNING"):
        with pytest.raises(OperationOutcomeException):
            FhirValidator.validate(resource, model)


@pytest.mark.parametrize(
    "resource",
    [
        {"resourceType": "DummyResource", "name": "Valid Name"},
        {"resourceType": "DummyResource", "modifiedBy": "ValidUser"},
        {"resourceType": "DummyResource", "telecom": [{"value": "123456"}]},
        {"resourceType": "DummyResource", "type": [{"text": "Type1"}]},
    ],
)
def test_check_for_special_characters_valid(resource: dict) -> None:
    model = DummyModel
    assert FhirValidator._check_for_special_characters(resource, model) == resource


@pytest.mark.parametrize(
    "resource,expected_error_field",
    [
        ({"resourceType": "DummyResource", "name": 'Invalid"Name'}, "name"),
        ({"resourceType": "DummyResource", "modifiedBy": "Invalid#User"}, "modifiedBy"),
        (
            {"resourceType": "DummyResource", "telecom": [{"value": "123;456"}]},
            "telecom[0].value",
        ),
        (
            {"resourceType": "DummyResource", "type": [{"text": "Type$1"}]},
            "type[0].text",
        ),
    ],
)
def test_check_for_special_characters_invalid(
    resource: dict, expected_error_field: str
) -> None:
    model = DummyModel
    with pytest.raises(OperationOutcomeException) as exc_info:
        FhirValidator._check_for_special_characters(resource, model)
    assert f"Field '{expected_error_field}' contains invalid characters" in str(
        exc_info.value
    )
