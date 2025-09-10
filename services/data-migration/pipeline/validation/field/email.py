import re

from pipeline.validation.field.base import (
    FieldValidationResult,
    FieldValidator,
)


class EmailValidator(FieldValidator[str]):
    VALID_EMAIL_ADDRESS_LENGTH = 254
    VALID_EMAIL_PARTS_COUNT = 2

    VALID_EMAIL_LOCAL_REGEX = re.compile(
        r"^(?!\.)(\"([a-zA-Z0-9.!#$%&'*+/=?^_`{|}~\-\s](?!\.\.))+\"|[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~\-](?!\.\.))+(?<!\.)$"
    )
    VALID_EMAIL_DOMAIN_REGEX = re.compile(
        r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$"
    )
    NHS_EMAIL_REGEX = re.compile(
        r"^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)*(nhs.net|nhs.uk)$"
    )
    ERROR_MESSAGES = {
        "email_not_string": "Email must be a string",
        "invalid_length": "Email length is too long",
        "invalid_format": "Email address is invalid",
        "not_nhs_email": "Email address is not a valid NHS email address",
    }

    def validate(self, data: str) -> FieldValidationResult[str]:
        """
        Run validation over a specific email field
        """
        validation_functions = [
            self.is_valid_type,
            self.is_valid_length,
            self.is_valid_format,
            self.is_nhs_email,
        ]

        for func in validation_functions:
            is_valid = func(data)
            if not is_valid:
                break

        return FieldValidationResult(
            original=data,
            sanitised=data if self.is_valid else None,
            issues=self.issues,
        )

    def is_valid_type(self, email: str) -> bool:
        """
        Validates if the provided email is a string.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is a string, False otherwise.
        """
        if not email or not isinstance(email, str):
            self.add_issue(
                severity="error",
                code="email_not_string",
                diagnostics=self.ERROR_MESSAGES["email_not_string"],
                value=email,
            )
            return False

        return True

    def is_valid_length(self, email: str) -> bool:
        """
        Validates if the provided email is within the valid length.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email length is valid, False otherwise.
        """
        if len(email) > self.VALID_EMAIL_ADDRESS_LENGTH:
            self.add_issue(
                severity="error",
                code="invalid_length",
                diagnostics=self.ERROR_MESSAGES["invalid_length"],
                value=email,
            )
            return False

        return True

    def is_valid_format(self, email: str) -> bool:
        """
        Validates if the provided email is in a legitimate format.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        email_parts = email.split("@")
        if len(email_parts) != self.VALID_EMAIL_PARTS_COUNT:
            self.add_issue(
                severity="error",
                code="invalid_format",
                diagnostics=self.ERROR_MESSAGES["invalid_format"],
                value=email,
            )
            return False

        match_local = self.VALID_EMAIL_LOCAL_REGEX.fullmatch(email_parts[0])
        match_domain = self.VALID_EMAIL_DOMAIN_REGEX.fullmatch(email_parts[-1])

        if match_local is not None and match_domain is not None:
            return True

        self.add_issue(
            severity="error",
            code="invalid_format",
            diagnostics=self.ERROR_MESSAGES["invalid_format"],
            value=email,
        )
        return False

    def is_nhs_email(self, email: str) -> bool:
        """
        Validates if the provided email is a valid NHS email.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is a valid NHS email, False otherwise.
        """
        email_parts = email.split("@")

        match = self.NHS_EMAIL_REGEX.fullmatch(email_parts[-1])
        if match is None:
            self.add_issue(
                severity="error",
                code="not_nhs_email",
                diagnostics=self.ERROR_MESSAGES["not_nhs_email"],
                value=email,
            )
            return False

        return True
