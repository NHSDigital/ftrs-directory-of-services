from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from pydantic import ValidationError


def test_operation_outcome_exception_message() -> None:
    outcome = {"issue": [{"diagnostics": "Something went wrong"}]}
    exc = OperationOutcomeException(outcome)
    assert exc.outcome == outcome
    assert str(exc) == "Something went wrong"


def test_operation_outcome_exception_default_message() -> None:
    outcome = {"issue": [{}]}
    exc = OperationOutcomeException(outcome)
    assert str(exc) == "FHIR OperationOutcome error"


def test_operation_outcome_handler_build_basic() -> None:
    diagnostics = "Test diagnostics"
    outcome = OperationOutcomeHandler.build(diagnostics)
    assert isinstance(outcome, dict)
    assert outcome["issue"][0]["diagnostics"] == diagnostics
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"


def test_operation_outcome_handler_build_with_details_and_issues() -> None:
    diagnostics = "Test diagnostics"
    details = {"text": "More info"}
    issues = [{"severity": "warning", "code": "processing", "diagnostics": "Warn"}]
    outcome = OperationOutcomeHandler.build(diagnostics, details=details, issues=issues)
    assert outcome["issue"][0]["severity"] == "warning"
    assert outcome["issue"][0]["diagnostics"] == "Warn"


def test_operation_outcome_handler_from_exception() -> None:
    exc = Exception("Boom!")
    outcome = OperationOutcomeHandler.from_exception(exc)
    assert outcome["issue"][0]["diagnostics"] == "Boom!"
    assert outcome["issue"][0]["code"] == "exception"
    assert outcome["issue"][0]["severity"] == "fatal"


def test_operation_outcome_handler_from_validation_error_default_diagnostics() -> None:
    dummy_model_path = "tests.fhir.test_operation_outcome.DummyModel"

    error = ValidationError.from_exception_data(
        dummy_model_path,
        [
            {
                "type": "value_error",
                "loc": ("foo",),
                "msg": "Fake error",
                "input": "bad_value",
                "ctx": {"error": ValueError("Fake error")},
            }
        ],
    )
    outcome = OperationOutcomeHandler.from_validation_error(error)
    assert outcome["issue"][0]["diagnostics"] == "Validation failed for resource."
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"
    assert "Invalid Resource" in outcome["issue"][0]["details"]["coding"][0]["display"]


def test_operation_outcome_handler_from_validation_error_with_diagnostics() -> None:
    dummy_model_path = "tests.fhir.test_operation_outcome.DummyModel"

    error = ValidationError.from_exception_data(
        dummy_model_path,
        [
            {
                "type": "value_error",
                "loc": ("foo",),
                "msg": "Fake error",
                "input": "bad_value",
                "ctx": {"error": ValueError("Fake error")},
            }
        ],
    )

    outcome = OperationOutcomeHandler.from_validation_error(error)
    assert outcome["issue"][0]["diagnostics"] == "Validation failed for resource."
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"
