# import pytest

# from pipeline.utils.validators.email import EmailValidator


# @pytest.mark.parametrize(
#     "email,expected",
#     [
#         ("test@nhs.uk", (True, None)),
#         ("test@nhs.net", (True, None)),
#         ("a" * 240 + "@example.com", (True, None)),
#         ("b" * 241 + "@example.com", (True, None)),
#         ("c" * 242 + "@example.com", (True, None)),
#         (
#             "d" * 243 + "@example.com",
#             (False, EmailValidator.ERROR_MESSAGES["invalid_length"]),
#         ),
#         (
#             "e" * 244 + "@example.com",
#             (False, EmailValidator.ERROR_MESSAGES["invalid_length"]),
#         ),
#         (
#             "f" * 255 + "@example.com",
#             (False, EmailValidator.ERROR_MESSAGES["invalid_length"]),
#         ),
#     ],
# )
# def test_email_validator_valid_length(
#     email: str, expected: tuple[bool, str | None]
# ) -> None:
#     """
#     Test that email length validation works correctly.
#     """
#     assert EmailValidator.is_valid_length(email) == expected


# @pytest.mark.parametrize(
#     "email,expected",
#     [
#         ("test@nhs.uk", (True, None)),
#         ("test@nhs.net", (True, None)),
#         ("test@email.com", (True, None)),
#         ("invalid-email", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         ("", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         ("test@.com", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         ("simple@example.com", (True, None)),
#         ("very.common@example.com", (True, None)),
#         ("disposable.style.email.with+symbol@example.com", (True, None)),
#         ("other.email-with-hyphen@example.com", (True, None)),
#         ("fully-qualified-domain@example.com", (True, None)),
#         ("user.name+tag+sorting@example.com", (True, None)),
#         ("example-indeed@strange-example.com", (True, None)),
#         ("admin@mailserver1", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         ('"much.more unusual"@example.com', (True, None)),
#         (
#             '"very.unusual.@.unusual.com"@example.com',
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             '"very.(),:;<>[]\\".VERY.\\"very@\\\\ \\"very\\".unusual"@strange.example.com',
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             'very.(),:;<>[]\\.VERY.\\"very@\\\\ \\"very\\".unusual"@strange.example.com',
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             '"very.(),:;<>[]\\".VERY.\\very@\\\\ \\very\\".unusual"@strange.example.com',
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             '"very.(),:;<>[]\\".VERY.\\"very@\\\\ \\"very\\.unusual@strange.example.com',
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         (
#             "user@[192.168.1.1]",
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         ("user@sub.domain.co.uk", (True, None)),
#         ('email"{}23|"@domain.com', (True, None)),
#         (
#             "space in email@domain.com",
#             (False, EmailValidator.ERROR_MESSAGES["invalid_format"]),
#         ),
#         ('"space in email"@domain.com', (True, None)),
#         ("nhs.uk", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         (None, (False, EmailValidator.ERROR_MESSAGES["email_not_string"])),
#     ],
# )
# def test_email_validator_invalid_email(email: str, expected: bool) -> None:
#     """
#     Test that invalid email addresses are correctly identified.
#     """
#     assert EmailValidator.is_valid(email) == expected


# @pytest.mark.parametrize(
#     "email,expected",
#     [
#         ("test@nhs.uk", (True, None)),
#         ("test@organisation.nhs.uk", (True, None)),
#         ("test@nhs.net", (True, None)),
#         ("test@organisation.nhs.net", (True, None)),
#         ("test@email.com", (False, EmailValidator.ERROR_MESSAGES["not_nhs_email"])),
#         ("test@nhs.com", (False, EmailValidator.ERROR_MESSAGES["not_nhs_email"])),
#         ("test@organisation.nhs.uk", (True, None)),
#         ("test@organisation.suborg.nhs.uk", (True, None)),
#         ("test@organisation.nhs.net", (True, None)),
#         ("test@organisation.suborg.nhs.net", (True, None)),
#         ("test@orga-nisation.nhs.net", (True, None)),
#         (
#             "test@organisation.suborg.nh-s.net",
#             (False, EmailValidator.ERROR_MESSAGES["not_nhs_email"]),
#         ),
#         (
#             "test@organisation.suborg.nhs.net.no",
#             (False, EmailValidator.ERROR_MESSAGES["not_nhs_email"]),
#         ),
#         (
#             "test@organisation.suborg.nhs.uk.no",
#             (False, EmailValidator.ERROR_MESSAGES["not_nhs_email"]),
#         ),
#         ("nhs.uk", (False, EmailValidator.ERROR_MESSAGES["invalid_format"])),
#         (None, (False, EmailValidator.ERROR_MESSAGES["email_not_string"])),
#     ],
# )
# def test_email_validator_nhs_email(email: str, expected: bool) -> None:
#     """
#     Test that NHS email addresses are correctly identified.
#     """
#     assert EmailValidator.is_nhs_email(email) == expected
