import pytest
from ftrs_common.utils.title_case_sanitization import (
    PRESERVE_ACRONYMS,
    sanitize_string_field,
    to_title_case_preserving_acronyms,
)


class TestToTitleCasePreservingAcronyms:
    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("hello world", "Hello World"),
            ("HELLO WORLD", "Hello World"),
        ],
    )
    def test_converts_to_title_case(self, input_text: str, expected: str) -> None:
        """Test that text is converted to title case."""
        result = to_title_case_preserving_acronyms(input_text)
        assert result == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("nhs trust", "NHS Trust"),
            ("the nhs foundation", "The NHS Foundation"),
            ("gp practice", "GP Practice"),
            ("local gp surgery", "Local GP Surgery"),
            ("icb board", "ICB Board"),
            ("pcn network", "PCN Network"),
        ],
    )
    def test_preserves_single_acronym(self, input_text: str, expected: str) -> None:
        """Test that individual acronyms are preserved in uppercase."""
        result = to_title_case_preserving_acronyms(input_text)
        assert result == expected

    def test_preserves_multiple_acronyms(self) -> None:
        """Test that multiple acronyms are preserved."""
        result = to_title_case_preserving_acronyms("nhs gp icb pcn")
        assert result == "NHS GP ICB PCN"

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("", ""),
            ("   ", "   "),
        ],
    )
    def test_handles_edge_cases(self, input_text: str, expected: str) -> None:
        """Test that edge cases are handled correctly."""
        result = to_title_case_preserving_acronyms(input_text)
        assert result == expected

    def test_mixed_case_with_acronyms(self) -> None:
        """Test mixed case text with acronyms."""
        result = to_title_case_preserving_acronyms("The NHS GP Practice")
        assert result == "The NHS GP Practice"

    def test_acronyms_case_insensitive(self) -> None:
        """Test that acronym matching is case insensitive."""
        result = to_title_case_preserving_acronyms("Nhs Gp Icb Pcn")
        assert result == "NHS GP ICB PCN"


class TestSanitizeStringField:
    def test_sanitizes_string_value(self) -> None:
        """Test that string values are sanitized."""
        result = sanitize_string_field("nhs trust")
        assert result == "NHS Trust"

    @pytest.mark.parametrize(
        "input_value",
        [123, True, [1, 2, 3]],
    )
    def test_returns_non_string_unchanged(self, input_value: int | bool | list) -> None:
        """Test that non-string values are returned unchanged."""
        assert sanitize_string_field(input_value) == input_value


class TestAcronymConstant:
    def test_contains_required_acronyms(self) -> None:
        required = {"NHS", "GP", "ICB", "PCN"}
        assert required.issubset(PRESERVE_ACRONYMS)

    def test_is_immutable(self) -> None:
        assert isinstance(PRESERVE_ACRONYMS, frozenset)
