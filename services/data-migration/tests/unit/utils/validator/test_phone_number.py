# import pytest

# from pipeline.utils.validators.phone_number import PhoneNumberValidator


# @pytest.mark.parametrize(
#     "number, expected",
#     [
#         ("07911123456", (True, None)),
#         ("02079460056", (True, None)),
#         ("020 7946 0056", (True, None)),
#         ("01632 960123", (True, None)),
#         ("0800 123 4567", (True, None)),
#         ("0300 123 4567", (True, None)),
#         (
#             "079111234567",
#             (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_length"]),
#         ),
#         ("0791112345", (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"])),
#         ("1234567890", (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"])),
#         ("07a9111234", (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"])),
#         ("07-911-1234", (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"])),
#         ("+447911123456", (True, None)),
#         ("+442079460056", (True, None)),
#         ("+4420 7946 0056", (True, None)),
#         ("+441632 960123", (True, None)),
#         ("+44800 123 4567", (True, None)),
#         ("+44300 123 4567", (True, None)),
#         (
#             "+4479111234567",
#             (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_length"]),
#         ),
#         (
#             "+44791112345",
#             (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             "+447a9111234",
#             (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             "+447-911-1234",
#             (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         ("7911123456", (False, PhoneNumberValidator.ERROR_MESSAGES["invalid_format"])),
#         ("", (False, PhoneNumberValidator.ERROR_MESSAGES["empty"])),
#         (None, (False, PhoneNumberValidator.ERROR_MESSAGES["empty"])),
#         (123, (False, PhoneNumberValidator.ERROR_MESSAGES["not_string"])),
#     ],
# )
# def test_phone_number_validator(number: str, expected: bool) -> None:
#     """
#     Test that phone number validation works correctly.
#     """
#     assert PhoneNumberValidator.is_valid(number) == expected
