import re


class PhoneNumberValidator:
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

    @staticmethod
    def is_valid(phone_number: str) -> tuple[bool, str | None]:
        """
        Validates if the provided phone number is valid.

        Args:
            phone_number (str): The phone number to validate.

        Returns:
            bool: True if the phone number is valid, False otherwise.
        """
        if not phone_number:
            return False, PhoneNumberValidator.ERROR_MESSAGES["empty"]
        if not isinstance(phone_number, str):
            return False, PhoneNumberValidator.ERROR_MESSAGES["not_string"]

        phone_number = phone_number.strip().replace(" ", "").replace("+44", "0")

        if (
            not phone_number
            or len(phone_number) > PhoneNumberValidator.PHONE_NUMBER_VALID_UPPER_LENGTH
            or len(phone_number) < PhoneNumberValidator.PHONE_NUMBER_VALID_LOWER_LENGTH
            or len(phone_number) == PhoneNumberValidator.INVALID_PHONE_NUMBER_LENGTH
        ):
            return False, "Phone number length is invalid"
        if PhoneNumberValidator.PHONE_NUMBER_REGEX.fullmatch(phone_number) is not None:
            return True, None
        return False, "Phone number is invalid"
