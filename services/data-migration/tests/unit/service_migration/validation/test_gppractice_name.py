import pytest
from ftrs_common.logger import Logger

from service_migration.validation.base import FieldValidationResult
from service_migration.validation.service import GPPracticeValidator

"""Unit tests for GP practice name validation in GPPracticeValidator."""


@pytest.fixture
def mock_logger() -> Logger:
    """Provide a mock logger for testing."""
    return Logger.get(service="test-gp-practice-validator")


@pytest.fixture
def validator(mock_logger: Logger) -> GPPracticeValidator:
    """Provide a GPPracticeValidator instance with logger."""
    return GPPracticeValidator(logger=mock_logger)


def assert_valid_name(
    validator: GPPracticeValidator, input_name: str, expected: str
) -> None:
    """Assert that a name is valid and sanitized correctly."""
    result: FieldValidationResult[str] = validator.validate_name(input_name)
    assert result.sanitised == expected
    assert len(result.issues) == 0


def assert_invalid_name(
    validator: GPPracticeValidator, input_name: str, expected_code: str
) -> None:
    """Assert that a name is invalid with expected error code."""
    result: FieldValidationResult[str] = validator.validate_name(input_name)
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == expected_code
    assert result.issues[0].severity == "error"


# Entity Decoding Tests
@pytest.mark.parametrize(
    "input_name,expected",
    [
        (
            "St Peters Health Centre (Dr S D&#39;Souza)",
            "St Peters Health Centre (Dr S D'Souza)",
        ),
        ("O&apos;Brien Medical Practice", "O'Brien Medical Practice"),
        ("Dr O&#x27;Connor Surgery", "Dr O'Connor Surgery"),
        (
            "O&#39;Brien &amp; D&#39;Souza Medical Centre",
            "O'Brien & D'Souza Medical Centre",
        ),
        ("Smith &amp; Jones Surgery", "Smith & Jones Surgery"),
        ("O'Brien Medical Practice", "O'Brien Medical Practice"),
        ("Normal Surgery Name", "Normal Surgery Name"),
    ],
)
def test_valid_entity_decoding(
    validator: GPPracticeValidator, input_name: str, expected: str
) -> None:
    """Test decoding of allowed HTML entities."""
    assert_valid_name(validator, input_name, expected)


# Allowed Characters Tests
@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("St. Mary&#39;s Medical Centre", "St. Mary's Medical Centre"),
        ("Smith, Jones &amp; Partners", "Smith, Jones & Partners"),
        ("Health Centre (Dr O&#39;Brien)", "Health Centre (Dr O'Brien)"),
    ],
)
def test_allowed_special_characters(
    validator: GPPracticeValidator, input_name: str, expected: str
) -> None:
    """Test that periods, commas, and parentheses are allowed."""
    assert_valid_name(validator, input_name, expected)


# Security Tests - Dangerous Patterns
@pytest.mark.parametrize(
    "malicious_input",
    [
        "&quot;The Surgery&quot;",
        "Surgery &lt;script&gt;alert('xss')&lt;/script&gt;",
        "Surgery &lt;Name&gt;",
        "Surgery&#10;Fake Line",
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>",
        "Surgery onclick=alert(1)",
    ],
)
def test_reject_dangerous_patterns(
    validator: GPPracticeValidator, malicious_input: str
) -> None:
    """Test that dangerous patterns are rejected."""
    assert_invalid_name(validator, malicious_input, "publicname_suspicious_encoding")


# Security Tests - Disallowed Entities
@pytest.mark.parametrize(
    "input_name",
    [
        "Test &lt;Surgery&gt;",
        "Practice &nbsp; Name",
        "Surgery &copy; 2024",
        "Test &#60;script&#62;",
    ],
)
def test_reject_disallowed_entities(
    validator: GPPracticeValidator, input_name: str
) -> None:
    """Test that disallowed HTML entities are rejected."""
    assert_invalid_name(validator, input_name, "publicname_suspicious_encoding")


# Security Tests - Nested Encoding
@pytest.mark.parametrize(
    "nested_encoding",
    [
        "O&amp;#39;Brien",
        "O&amp;apos;Brien",
        "O&amp;#x27;Brien",
        "Smith &amp;amp; Jones",
        "&amp;amp;amp;",
        "&amp;amp;amp;amp;",
        "Test &amp;lt;script&amp;gt;",
        "&amp;#60;script&amp;#62;",
    ],
)
def test_reject_nested_encoding(
    validator: GPPracticeValidator, nested_encoding: str
) -> None:
    """Test that any level of nested encoding is rejected."""
    assert_invalid_name(validator, nested_encoding, "publicname_suspicious_encoding")


# Security Tests - Special Symbols
@pytest.mark.parametrize(
    "input_name",
    [
        "Smith @ Medical Centre",
        "Practice #1",
        "Surgery 100%",
        "Clinic*Star",
        "Health+Plus",
        'The "Best" Surgery',
        "Valid Name<script>",
        "O&#39;Brien&#39; OR 1=1",
    ],
)
def test_reject_special_symbols(
    validator: GPPracticeValidator, input_name: str
) -> None:
    """Test that special symbols are rejected."""
    assert_invalid_name(validator, input_name, "publicname_suspicious_characters")


# Ampersand Rules Tests
@pytest.mark.parametrize(
    "input_name,should_pass",
    [
        ("Smith & Jones", True),
        ("Smith& Jones", False),
        ("Smith &Jones", False),
        ("Smith&Jones", False),
    ],
)
def test_ampersand_spacing_rules(
    validator: GPPracticeValidator, input_name: str, should_pass: bool
) -> None:
    """Test that ampersand must be surrounded by spaces."""
    if should_pass:
        assert_valid_name(validator, input_name, input_name)
    else:
        assert_invalid_name(validator, input_name, "publicname_suspicious_characters")


# Whitespace Tests
@pytest.mark.parametrize(
    "input_name,expected,error_code",
    [
        ("  St Peters Surgery  ", "St Peters Surgery", None),
        ("St  Peters  Surgery", "St Peters Surgery", None),
        ("   ", None, "publicname_empty_after_sanitization"),
    ],
)
def test_whitespace_handling(
    validator: GPPracticeValidator,
    input_name: str,
    expected: str | None,
    error_code: str | None,
) -> None:
    """Test whitespace trimming and normalization."""
    if error_code:
        assert_invalid_name(validator, input_name, error_code)
    else:
        assert_valid_name(validator, input_name, expected)


# Empty/None Tests
@pytest.mark.parametrize(
    "input_name,expected_code",
    [
        ("", "publicname_required"),
        (None, "publicname_required"),
    ],
)
def test_empty_or_none_input(
    validator: GPPracticeValidator, input_name: str | None, expected_code: str
) -> None:
    """Test handling of empty or None values."""
    result: FieldValidationResult[str] = validator.validate_name(input_name)
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == expected_code
    assert result.issues[0].severity == "error"


# Length Tests
def test_reject_name_too_long(validator: GPPracticeValidator) -> None:
    """Test that names exceeding maximum length are rejected."""
    long_name: str = "A" * 201
    assert_invalid_name(validator, long_name, "publicname_too_long")


def test_allow_name_at_max_length(validator: GPPracticeValidator) -> None:
    """Test that names at exactly max length are accepted."""
    max_name: str = "A" * 200
    result: FieldValidationResult[str] = validator.validate_name(max_name)
    assert result.sanitised is not None
    assert len(result.issues) == 0


# Hyphen Splitting Tests
@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("Smith Medical Practice", "Smith Medical Practice"),
        ("Abbey-Dale Medical Centre", "Abbey-Dale Medical Centre"),
        ("Lockside Medical Centre - T+G", "Lockside Medical Centre"),
        ("Smith Surgery - Branch 1", "Smith Surgery"),
        ("O&#39;Brien Practice - North", "O'Brien Practice"),
        ("Health Centre - Dr Jones - Room 5", "Health Centre"),
        ("St. Mary&#39;s - West Wing", "St. Mary's"),
        ("Normal Surgery", "Normal Surgery"),
        ("Practice-Name-With-Hyphens", "Practice-Name-With-Hyphens"),
        ("Centre - ", "Centre"),
        (" - Standalone Hyphen", ""),
    ],
)
def test_hyphen_splitting_business_rule(
    validator: GPPracticeValidator, input_name: str, expected: str
) -> None:
    """Test that names are split on ' - ' and only first part is kept."""
    if expected == "":
        assert_invalid_name(
            validator, input_name, "publicname_empty_after_sanitization"
        )
    else:
        assert_valid_name(validator, input_name, expected)


@pytest.mark.parametrize(
    "input_name,expected",
    [
        # SQL injection in suffix (should be discarded)
        ("Valid Practice - '; DROP TABLE--", "Valid Practice"),
        # XSS in suffix (should be discarded)
        ("Valid Practice - <script>alert(1)</script>", "Valid Practice"),
        # Malicious entity in suffix (should be discarded)
        ("Valid Practice - &lt;script&gt;", "Valid Practice"),
        # Multiple hyphens (only first split)
        ("Practice - Bad - Worse", "Practice"),
        # Empty after split (should error)
        (" - <script>alert(1)</script>", ""),
    ],
)
def test_hyphen_splitting_security(
    validator: GPPracticeValidator, input_name: str, expected: str
) -> None:
    """Test that malicious content in suffixes is safely discarded."""
    if expected == "":
        assert_invalid_name(
            validator, input_name, "publicname_empty_after_sanitization"
        )
    else:
        assert_valid_name(validator, input_name, expected)


# Original Value Preservation Test
def test_preserve_original_value(validator: GPPracticeValidator) -> None:
    """Test that original value is preserved in result."""
    original: str = "O&#39;Brien Surgery"
    result: FieldValidationResult[str] = validator.validate_name(original)
    assert result.original == original
    assert result.sanitised != original
    assert result.sanitised == "O'Brien Surgery"


# Character Categorization Test
def test_categorize_multiple_character_types(validator: GPPracticeValidator) -> None:
    """Test that multiple suspicious character types are categorized."""
    result: FieldValidationResult[str] = validator.validate_name("Surgery <script>@#%")
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "publicname_suspicious_characters"
    diagnostics: str = result.issues[0].diagnostics
    assert "angle_brackets" in diagnostics
    assert "special_symbols" in diagnostics
