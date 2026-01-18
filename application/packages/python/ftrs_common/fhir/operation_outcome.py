from fhir.resources.R4B.operationoutcome import OperationOutcome, OperationOutcomeIssue
from pydantic import ValidationError

OPERATION_OUTCOME_SYSTEM = "http://terminology.hl7.org/CodeSystem/operation-outcome"
ERROR_PROCESSING_REQUEST = "Error processing request"

FHIR_OPERATION_OUTCOME_CODES: dict[str, tuple[str, str]] = {
    "invalid": ("MSG_PARAM_INVALID", "Parameter content is invalid"),
    "not-found": ("MSG_NO_EXIST", "Resource does not exist"),
    "exception": ("MSG_ERROR_PARSING", ERROR_PROCESSING_REQUEST),
    "structure": ("MSG_BAD_SYNTAX", "Bad Syntax"),
    "required": ("MSG_RESOURCE_REQUIRED", "A resource is required"),
    "value": ("MSG_PARAM_INVALID", "Parameter content is invalid"),
    "processing": ("MSG_ERROR_PARSING", ERROR_PROCESSING_REQUEST),
    "duplicate": ("MSG_DUPLICATE_ID", "Duplicate Id for resource"),
    "informational": ("MSG_UPDATED", "Existing resource updated"),
    "success": ("MSG_UPDATED", "Existing resource updated"),
}


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
    def _build_details(code: str, text: str) -> dict:
        fhir_code, display = FHIR_OPERATION_OUTCOME_CODES.get(
            code, ("MSG_ERROR_PARSING", ERROR_PROCESSING_REQUEST)
        )
        return {
            "coding": [
                {
                    "system": OPERATION_OUTCOME_SYSTEM,
                    "code": fhir_code,
                    "display": display,
                }
            ],
            "text": text,
        }

    @staticmethod
    def build(  # noqa: PLR0913
        diagnostics: str,
        code: str = "invalid",
        severity: str = "error",
        details_text: str | None = None,
        details: dict | None = None,
        expression: list[str] | None = None,
        issues: list | None = None,
    ) -> dict:
        if issues is None:
            if details is None:
                details = OperationOutcomeHandler._build_details(
                    code, details_text or diagnostics
                )

            issue_dict: dict = {
                "severity": severity,
                "code": code,
                "details": details,
                "diagnostics": diagnostics,
            }

            if expression:
                issue_dict["expression"] = expression

            issues = [issue_dict]

        fhir_issues = [OperationOutcomeIssue(**issue) for issue in issues]
        outcome = OperationOutcome(issue=fhir_issues)
        return outcome.model_dump(exclude_none=True)

    @staticmethod
    def from_exception(
        exc: Exception,
        code: str = "exception",
        severity: str = "fatal",
    ) -> dict:
        """
        Build an OperationOutcome from an exception.
        """
        return OperationOutcomeHandler.build(
            diagnostics=str(exc),
            code=code,
            severity=severity,
            details_text=f"An unexpected error occurred: {exc}",
        )

    @staticmethod
    def from_validation_error(
        e: ValidationError,
    ) -> dict:
        return OperationOutcomeHandler.build(
            diagnostics="Validation failed for resource.",
            code="invalid",
            severity="error",
            details_text=str(e),
        )
