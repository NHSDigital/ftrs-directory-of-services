import re


class EmailValidator:
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

    @staticmethod
    def is_valid_length(email: str) -> tuple[bool, str | None]:
        """
        Validates if the provided email is within the valid length.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email length is valid, False otherwise.
        """
        if not isinstance(email, str):
            return False, EmailValidator.ERROR_MESSAGES["email_not_string"]
        if not email or len(email) > EmailValidator.VALID_EMAIL_ADDRESS_LENGTH:
            return False, EmailValidator.ERROR_MESSAGES["invalid_length"]
        return True, None

    @staticmethod
    def is_valid(email: str) -> bool:
        """
        Validates if the provided email is in a legitimate format.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        if not isinstance(email, str):
            return False, EmailValidator.ERROR_MESSAGES["email_not_string"]
        email_parts = email.split("@")
        if len(email_parts) != EmailValidator.VALID_EMAIL_PARTS_COUNT:
            return False, EmailValidator.ERROR_MESSAGES["invalid_format"]
        match_local = EmailValidator.VALID_EMAIL_LOCAL_REGEX.fullmatch(email_parts[0])
        match_domain = EmailValidator.VALID_EMAIL_DOMAIN_REGEX.fullmatch(
            email_parts[-1]
        )
        if match_local is not None and match_domain is not None:
            return True, None
        return False, EmailValidator.ERROR_MESSAGES["invalid_format"]

    @staticmethod
    def is_nhs_email(email: str) -> tuple[bool, str | None]:
        """
        Validates if the provided email is a valid NHS email.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is a valid NHS email, False otherwise.
        """
        if not isinstance(email, str):
            return False, EmailValidator.ERROR_MESSAGES["email_not_string"]
        email_parts = email.split("@")
        if len(email_parts) != EmailValidator.VALID_EMAIL_PARTS_COUNT:
            return False, EmailValidator.ERROR_MESSAGES["invalid_format"]
        match = EmailValidator.NHS_EMAIL_REGEX.fullmatch(email_parts[-1])
        if match is not None:
            return True, None
        return False, EmailValidator.ERROR_MESSAGES["not_nhs_email"]
