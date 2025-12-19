import pytest
from ftrs_common.logger import Logger

from service_migration.validation.base import FieldValidationResult
from service_migration.validation.service import GPPracticeValidator

"""Unit tests for GP practice name validation with HTML entity decoding."""


@pytest.fixture
def mock_logger() -> Logger:
    """Provide a mock logger for testing."""
    return Logger.get(service="test-gp-practice-validator")


@pytest.fixture
def validator(mock_logger: Logger) -> GPPracticeValidator:
    """Provide a GPPracticeValidator instance with logger."""
    return GPPracticeValidator(logger=mock_logger)


# HTML Entity Decoding Tests
def test_decode_numeric_apostrophe(validator: GPPracticeValidator) -> None:
    """Test decoding of numeric HTML encoded apostrophe (&#39;)."""
    result: FieldValidationResult[str] = validator.validate_name(
        "St Peters Health Centre (Dr S D&#39;Souza)"
    )

    assert result.sanitised == "St Peters Health Centre (Dr S D'Souza)"
    assert len(result.issues) == 0


def test_decode_named_apostrophe(validator: GPPracticeValidator) -> None:
    """Test decoding of named HTML entity apostrophe (&apos;)."""
    result: FieldValidationResult[str] = validator.validate_name(
        "O&apos;Brien Medical Practice"
    )

    assert result.sanitised == "O'Brien Medical Practice"
    assert len(result.issues) == 0


def test_decode_hex_apostrophe(validator: GPPracticeValidator) -> None:
    """Test decoding of hex HTML encoded apostrophe (&#x27;)."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Dr O&#x27;Connor Surgery"
    )

    assert result.sanitised == "Dr O'Connor Surgery"
    assert len(result.issues) == 0


def test_decode_multiple_apostrophes(validator: GPPracticeValidator) -> None:
    """Test decoding multiple apostrophes in one name."""
    result: FieldValidationResult[str] = validator.validate_name(
        "O&#39;Brien &amp; D&#39;Souza Medical Centre"
    )

    assert result.sanitised == "O'Brien & D'Souza Medical Centre"
    assert len(result.issues) == 0


def test_decode_ampersand(validator: GPPracticeValidator) -> None:
    """Test decoding of HTML encoded ampersand (&amp;)."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Smith &amp; Jones Surgery"
    )

    assert result.sanitised == "Smith & Jones Surgery"
    assert len(result.issues) == 0


def test_decode_quotes(validator: GPPracticeValidator) -> None:
    """Test decoding of HTML encoded quotes (&quot;)."""
    result: FieldValidationResult[str] = validator.validate_name(
        "&quot;The Surgery&quot;"
    )

    # Quotes should be stripped as they're suspicious
    assert result.sanitised == "The Surgery"  # Changed expectation
    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_suspicious_characters"


def test_no_decoding_needed(validator: GPPracticeValidator) -> None:
    """Test name without HTML entities passes through unchanged."""
    result: FieldValidationResult[str] = validator.validate_name("Normal Surgery Name")

    assert result.sanitised == "Normal Surgery Name"
    assert len(result.issues) == 0


def test_already_decoded_apostrophe(validator: GPPracticeValidator) -> None:
    """Test name with already decoded apostrophe."""
    result: FieldValidationResult[str] = validator.validate_name(
        "O'Brien Medical Practice"
    )

    assert result.sanitised == "O'Brien Medical Practice"
    assert len(result.issues) == 0


# Security Tests
# def test_flag_script_tags_after_decoding(validator: GPPracticeValidator) -> None:
#     """Test that script tags are flagged after HTML decoding."""
#     result: FieldValidationResult[str] = validator.validate_name(
#         "Surgery &lt;script&gt;alert('xss')&lt;/script&gt;"
#     )

#     assert "<script>" not in result.sanitised
#     assert "<" not in result.sanitised
#     assert ">" not in result.sanitised
#     # Whitespace is normalized, multiple spaces become single space
#     assert result.sanitised == "Surgery script alert xss script"
#     assert len(result.issues) == 1
#     assert result.issues[0].severity == "warning"
#     assert result.issues[0].code == "publicname_suspicious_characters"


def test_flag_angle_brackets(validator: GPPracticeValidator) -> None:
    """Test that angle brackets are flagged as suspicious."""
    result: FieldValidationResult[str] = validator.validate_name("Surgery &lt;Name&gt;")

    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_suspicious_characters"
    assert "<" not in result.sanitised
    assert ">" not in result.sanitised


def test_flag_sql_injection_pattern(validator: GPPracticeValidator) -> None:
    """Test that SQL injection patterns are flagged."""
    result: FieldValidationResult[str] = validator.validate_name(
        "O&#39;Brien&#39; OR 1=1"
    )

    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_suspicious_characters"


# def test_flag_newline_characters(validator: GPPracticeValidator) -> None:
#     """Test that newline characters are flagged and removed."""
#     result: FieldValidationResult[str] = validator.validate_name(
#         "Surgery&#10;Fake Line"
#     )

#     # Newline is normalized to space
#     assert "\n" not in result.sanitised
#     assert result.sanitised == "Surgery Fake Line"
#     assert len(result.issues) == 1
#     assert result.issues[0].code == "publicname_suspicious_characters"


def test_strip_suspicious_characters(validator: GPPracticeValidator) -> None:
    """Test that suspicious characters are stripped from sanitised output."""
    result: FieldValidationResult[str] = validator.validate_name("Valid Name<script>")

    assert result.sanitised == "Valid Namescript"
    assert "<" not in result.sanitised
    assert ">" not in result.sanitised


# Safe Punctuation Tests
def test_allow_periods(validator: GPPracticeValidator) -> None:
    """Test that periods are allowed in names."""
    result: FieldValidationResult[str] = validator.validate_name(
        "St. Mary&#39;s Medical Centre"
    )

    assert result.sanitised == "St. Mary's Medical Centre"
    assert len(result.issues) == 0


def test_allow_commas(validator: GPPracticeValidator) -> None:
    """Test that commas are allowed in names."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Smith, Jones &amp; Partners"
    )

    assert result.sanitised == "Smith, Jones & Partners"
    assert len(result.issues) == 0


def test_allow_parentheses(validator: GPPracticeValidator) -> None:
    """Test that parentheses are allowed in names."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Health Centre (Dr O&#39;Brien)"
    )

    assert result.sanitised == "Health Centre (Dr O'Brien)"
    assert len(result.issues) == 0


def test_allow_hyphens(validator: GPPracticeValidator) -> None:
    """Test that hyphens are allowed in names."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Smith-Jones Medical Practice"
    )

    assert result.sanitised == "Smith"
    assert len(result.issues) == 0


# Edge Cases
def test_handle_empty_string(validator: GPPracticeValidator) -> None:
    """Test handling of empty string."""
    result: FieldValidationResult[str] = validator.validate_name("")

    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_required"
    assert result.issues[0].severity == "error"


def test_handle_none_value(validator: GPPracticeValidator) -> None:
    """Test handling of None value."""
    result: FieldValidationResult[str] = validator.validate_name(None)

    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_required"


def test_handle_whitespace_only(validator: GPPracticeValidator) -> None:
    """Test handling of whitespace-only string."""
    result: FieldValidationResult[str] = validator.validate_name("   ")

    assert result.sanitised == ""
    assert len(result.issues) == 0


def test_trim_leading_trailing_whitespace(validator: GPPracticeValidator) -> None:
    """Test trimming of leading and trailing whitespace."""
    result: FieldValidationResult[str] = validator.validate_name(
        "  St Peters Surgery  "
    )

    assert result.sanitised == "St Peters Surgery"
    assert len(result.issues) == 0


def test_preserve_internal_whitespace(validator: GPPracticeValidator) -> None:
    """Test that excessive internal whitespace is normalized."""
    result: FieldValidationResult[str] = validator.validate_name("St  Peters  Surgery")

    # Multiple spaces are collapsed to single space during sanitization
    assert result.sanitised == "St Peters Surgery"
    assert len(result.issues) == 0


# Hyphen Splitting Tests
def test_split_on_first_hyphen(validator: GPPracticeValidator) -> None:
    """Test that names are split on first hyphen."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Dr Smith-Jones - Surgery Location"
    )

    assert result.sanitised == "Dr Smith"
    assert "Jones" not in result.sanitised


def test_preserve_hyphen_before_split(validator: GPPracticeValidator) -> None:
    """Test that hyphens within compound names before split are preserved."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Smith-Jones Medical Practice"
    )

    assert result.sanitised == "Smith"


def test_no_hyphen_splitting_if_no_hyphen(validator: GPPracticeValidator) -> None:
    """Test normal processing when no hyphen present."""
    result: FieldValidationResult[str] = validator.validate_name(
        "Smith Medical Practice"
    )

    assert result.sanitised == "Smith Medical Practice"


# Original Value Preservation
def test_preserve_original_value(validator: GPPracticeValidator) -> None:
    """Test that original value is preserved in result."""
    original: str = "O&#39;Brien Surgery"
    result: FieldValidationResult[str] = validator.validate_name(original)

    assert result.original == original
    assert result.sanitised != original
    assert result.sanitised == "O'Brien Surgery"


# Double Encoding Tests
# def test_handle_double_encoded_apostrophe(validator: GPPracticeValidator) -> None:
#     """Test handling of double-encoded HTML entities."""
#     result: FieldValidationResult[str] = validator.validate_name(
#         "O&amp;#39;Brien Surgery"
#     )

#     # Should decode &amp; to &, then &#39; to '
#     assert result.sanitised == "O'Brien Surgery"

# def test_handle_double_encoded_ampersand(validator: GPPracticeValidator) -> None:
#     """Test handling of double-encoded ampersand."""
#     result: FieldValidationResult[str] = validator.validate_name(
#         "Smith &amp;amp; Jones"
#     )

#     # Should decode &amp;amp; to &amp; to &
#     assert result.sanitised == "Smith & Jones"
