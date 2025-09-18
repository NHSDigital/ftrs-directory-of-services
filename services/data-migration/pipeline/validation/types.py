from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

TypeToValidate = TypeVar("TypeToValidate")
ValidationIssueSeverity = Literal["fatal", "error", "warning", "information", "success"]


class ValidationIssue(BaseModel):
    value: Any | None = None
    severity: ValidationIssueSeverity
    code: str
    diagnostics: str
    expression: list[str] | None = None


class ValidationResult(BaseModel, Generic[TypeToValidate]):
    origin_record_id: int
    issues: list[ValidationIssue]
    sanitised: TypeToValidate

    @property
    def is_valid(self) -> bool:
        return not any([issue.severity in ["fatal", "error"] for issue in self.issues])

    @property
    def should_continue(self) -> bool:
        return not any(issue.severity == "fatal" for issue in self.issues)
