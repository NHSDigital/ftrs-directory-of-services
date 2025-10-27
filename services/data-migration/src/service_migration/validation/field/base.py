from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from service_migration.validation.types import (
    ValidationIssue,
    ValidationIssueSeverity,
)

FieldType = TypeVar("FieldType")


class FieldValidationResult(BaseModel, Generic[FieldType]):
    original: FieldType
    sanitised: FieldType
    issues: list[ValidationIssue]


class FieldValidator(ABC, Generic[FieldType]):
    issues: list[ValidationIssue]

    def __init__(self, expression: str | None = None) -> None:
        self.issues = []
        self.expression = expression

    @abstractmethod
    def validate(self, data: FieldType) -> FieldValidationResult[FieldType]:
        """
        Run validation over a specific field type
        """
        raise NotImplementedError("Subclasses must implement this method")

    def add_issue(
        self,
        severity: ValidationIssueSeverity,
        code: str,
        diagnostics: str,
        value: FieldType | None = None,
        expression: str | None = None,
    ) -> None:
        """
        Add an issue to the validation result
        """
        expression = expression or self.expression

        self.issues.append(
            ValidationIssue(
                value=value,
                severity=severity,
                code=code,
                diagnostics=diagnostics,
                expression=[expression] if expression else None,
            )
        )

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity in ["error", "fatal"] for issue in self.issues)
