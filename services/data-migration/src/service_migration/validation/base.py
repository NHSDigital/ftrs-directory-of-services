from abc import ABC, abstractmethod
from typing import Generic

import deepdiff

from common.logbase import ServiceMigrationLogBase
from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.validation.field import (
    EmailValidator,
    FieldValidationResult,
    PhoneNumberValidator,
)
from service_migration.validation.types import TypeToValidate, ValidationResult


class Validator(ABC, Generic[TypeToValidate]):
    def __init__(self, deps: ServiceMigrationDependencies) -> None:
        self.deps = deps

    @abstractmethod
    def validate(self, data: TypeToValidate) -> ValidationResult:
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def validate_email(
        cls,
        email: str,
        expression: str = "email",
    ) -> FieldValidationResult[str]:
        """
        Run the email validator field validator over an email
        """
        return EmailValidator(expression).validate(email)

    @classmethod
    def validate_phone_number(
        cls,
        phone_number: str,
        expression: str = "publicphone",
    ) -> FieldValidationResult[str]:
        """
        Run the phone number field validator over a phone number value
        """
        return PhoneNumberValidator(expression).validate(phone_number)

    def log_sanitisations(
        self,
        original: TypeToValidate,
        sanitised: TypeToValidate,
    ) -> None:
        """
        Log any sanitisations that were made during validation
        """
        diff = deepdiff.DeepDiff(
            original.model_dump(mode="json"),
            sanitised.model_dump(mode="json"),
            ignore_order=True,
            threshold_to_diff_deeper=0,
        )

        if not diff:
            return

        self.deps.logger.log(
            ServiceMigrationLogBase.SM_VAL_003,
            validator_name=self.__class__.__name__,
            changes=diff.pretty().splitlines(),
        )
