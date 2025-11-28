from abc import ABC, abstractmethod
from typing import Generic

from ftrs_common.logger import Logger

from pipeline.validation.field import (
    EmailValidator,
    FieldValidationResult,
    PhoneNumberValidator,
)
from pipeline.validation.types import TypeToValidate, ValidationResult


class Validator(ABC, Generic[TypeToValidate]):
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

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
