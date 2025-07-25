from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue
from pydantic import ValidationError


class OperationOutcomeException(Exception):
    def __init__(self, outcome: dict) -> None:
        self.outcome = outcome
        message = (
            outcome.get("issue", [{}])[0].get("diagnostics")
            or "FHIR OperationOutcome error"
        )
        super().__init__(message)


class OperationOutcomeHandler:
    """
    Utility class for creating FHIR OperationOutcome resources in a reusable and version-agnostic way.
    """

    @staticmethod
    def build(
        diagnostics: str,
        code: str = "invalid",
        severity: str = "error",
        details: dict | None = None,
        issues: list | None = None,
    ) -> OperationOutcome:
        if issues is None:
            issue_dict = {
                "severity": severity,
                "code": code,
                "diagnostics": diagnostics,
            }
            if details:
                issue_dict["details"] = details
            issues = [issue_dict]

        fhir_issues = [OperationOutcomeIssue(**issue) for issue in issues]
        outcome = OperationOutcome(issue=fhir_issues)
        return outcome.model_dump(exclude_none=True)

    @staticmethod
    def from_exception(
        exc: Exception,
        code: str = "exception",
        severity: str = "fatal",
    ) -> OperationOutcome:
        """
        Build an OperationOutcome from an exception.
        """
        details = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                    "code": "exception",
                    "display": "Exception",
                }
            ],
            "text": f"An unexpected error occurred: {str(exc)}",
        }

        return OperationOutcomeHandler.build(
            diagnostics=str(exc),
            code=code,
            severity=severity,
            details=details,
        )

    @staticmethod
    def from_validation_error(
        e: ValidationError,
    ) -> OperationOutcome:
        details = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                    "code": "invalid",
                    "display": "Invalid Resource",
                }
            ],
            "text": str(e),
        }

        return OperationOutcomeHandler.build(
            diagnostics="Validation failed for resource.",
            code="invalid",
            severity="error",
            details=details,
        )
