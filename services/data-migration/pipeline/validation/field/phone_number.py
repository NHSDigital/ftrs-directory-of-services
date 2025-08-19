import re

from pipeline.validation.field.base import FieldValidationResult, FieldValidator


class PhoneNumberValidator(FieldValidator[str]):
    PHONE_NUMBER_VALID_UPPER_LENGTH = 11
    PHONE_NUMBER_VALID_LOWER_LENGTH = 8
    INVALID_PHONE_NUMBER_LENGTH = 9
    PHONE_NUMBER_REGEX = re.compile(
        r"^(01|02|03|05|07|08|09)\d{9}|01\d{8}|0800\d{6}|0845464\d$"
    )

    ERROR_MESSAGES = {
        "invalid_length": "Phone number length is invalid",
        "invalid_format": "Phone number is invalid",
        "not_string": "Phone number must be a string",
        "empty": "Phone number cannot be empty",
    }

    def validate(self, data: str) -> FieldValidationResult[str]:
        if not data:
            self.add_issue(
                severity="error",
                code="empty",
                diagnostics=self.ERROR_MESSAGES["empty"],
                value=data,
            )
            return FieldValidationResult(
                original=data,
                sanitised=None,
                issues=self.issues,
            )

        if not isinstance(data, str):
            self.add_issue(
                severity="error",
                code="not_string",
                diagnostics=self.ERROR_MESSAGES["not_string"],
                value=data,
            )
            return FieldValidationResult(
                original=data,
                sanitised=None,
                issues=self.issues,
            )

        data = data.strip().replace(" ", "").replace("+44", "0")

        if any(
            [
                len(data) > PhoneNumberValidator.PHONE_NUMBER_VALID_UPPER_LENGTH,
                len(data) < PhoneNumberValidator.PHONE_NUMBER_VALID_LOWER_LENGTH,
                len(data) == PhoneNumberValidator.INVALID_PHONE_NUMBER_LENGTH,
            ]
        ):
            self.add_issue(
                severity="error",
                code="invalid_length",
                diagnostics=self.ERROR_MESSAGES["invalid_length"],
                value=data,
            )

        if not self.PHONE_NUMBER_REGEX.fullmatch(data):
            self.add_issue(
                severity="error",
                code="invalid_format",
                diagnostics=self.ERROR_MESSAGES["invalid_format"],
                value=data,
            )

        return FieldValidationResult(
            original=data,
            sanitised=data if self.is_valid else None,
            issues=self.issues,
        )
