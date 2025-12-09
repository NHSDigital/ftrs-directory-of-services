import unittest
from unittest.mock import MagicMock, patch

from service_migration.formatting.address_formatter import (
    _norm,
    format_address,
)


class TestAddressFormatter(unittest.TestCase):
    def test_verify_address_formatting_with_multiple_segments(self) -> None:
        """Test address with standard 3-segment format."""
        result = format_address(
            "123 Main St$Springfield$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_town_in_segments(self) -> None:
        """Test that town is removed from segments when it matches town parameter."""
        result = format_address(
            "123 Main St$Springfield$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")

    def test_verify_address_formatting_with_duplicate_segments(self) -> None:
        """Test that duplicate segments are removed after normalization."""
        result = format_address(
            "123 Main St$123 main st$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.county, "Hampshire")

    def test_verify_address_formatting_with_empty_input(self) -> None:
        """Test handling of completely empty input."""
        result = format_address("", "", "")

        self.assertEqual(result, None)

    def test_verify_address_formatting_with_case_differences(self) -> None:
        """Test case-insensitive town matching with case preservation."""
        result = format_address(
            "123 Main St$springfield$Hampshire", "SPRINGFIELD", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.town, "SPRINGFIELD")

    def test_verify_address_formatting_with_multiple_lines(self) -> None:
        """Test address with 4 segments mapping to line1, line2, and county."""
        result = format_address(
            "123 Main St$Apt 4B$Town Center$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, "Apt 4B")
        self.assertEqual(result.county, "Hampshire")

    @patch("service_migration.formatting.address_formatter.pycountry")
    def test_verify_county_detection_with_pycountry(
        self, mock_pycountry: MagicMock
    ) -> None:
        """Test county detection using pycountry subdivisions."""
        mock_subdivision = MagicMock()
        mock_subdivision.country_code = "GB"
        mock_subdivision.name = "West Yorkshire"
        mock_pycountry.subdivisions.search_fuzzy.return_value = [mock_subdivision]

        result = format_address("123 Main St$Leeds$West Yorkshire", "Leeds", "LS1 1AB")

        self.assertEqual(result.county, "West Yorkshire")
        mock_pycountry.subdivisions.search_fuzzy.assert_called_once()

    @patch("service_migration.formatting.address_formatter.pycountry")
    def test_verify_county_detection_fallback_to_uk_counties(
        self, mock_pycountry: MagicMock
    ) -> None:
        """Test fallback to UK_COUNTIES list when pycountry returns empty."""
        mock_pycountry.subdivisions.search_fuzzy.return_value = []

        with patch(
            "service_migration.formatting.address_formatter.UK_COUNTIES", ["Hampshire"]
        ):
            result = format_address("123 Main St$Hampshire", "Springfield", "SP1 2AB")

            self.assertEqual(result.county, "Hampshire")

    @patch("service_migration.formatting.address_formatter.pycountry")
    def test_verify_county_detection_with_exception(
        self, mock_pycountry: MagicMock
    ) -> None:
        """Test graceful handling when pycountry raises exception."""
        mock_pycountry.subdivisions.search_fuzzy.side_effect = Exception(
            "Search failed"
        )

        with patch(
            "service_migration.formatting.address_formatter.UK_COUNTIES", ["Hampshire"]
        ):
            result = format_address("123 Main St$Hampshire", "Springfield", "SP1 2AB")

            self.assertEqual(result.county, "Hampshire")

    def test_verify_text_normalization(self) -> None:
        """Test text normalization function."""
        self.assertEqual(_norm(None), "")
        self.assertEqual(_norm(""), "")
        self.assertEqual(_norm("  Test  String  "), "test string")
        self.assertEqual(_norm("TEST"), "test")

    def test_verify_address_formatting_with_county_at_end(self) -> None:
        """Test county detection when in last segment."""
        result = format_address(
            "123 Main St$Building A$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, "Building A")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_county_at_start(self) -> None:
        """Test county detection when in first segment."""
        result = format_address(
            "Hampshire$123 Main St$Building A", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, "Building A")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_county_in_middle(self) -> None:
        """Test county detection when in middle segment."""
        result = format_address(
            "123 Main St$Hampshire$Building A", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, "Building A")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_no_county_found(self) -> None:
        """Test when no county is present in any segment."""
        result = format_address(
            "123 Main St$Building A$Floor 2", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, "Building A")
        self.assertIsNone(result.county)
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_single_segment_county(self) -> None:
        """Test single segment containing recognized county."""
        result = format_address("Hampshire", "Springfield", "SP1 2AB")

        self.assertIsNone(result.line1)
        self.assertIsNone(result.line2)
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_single_segment_no_county(self) -> None:
        """Test single segment not containing recognized county."""
        result = format_address("123 Main St", "Springfield", "SP1 2AB")

        self.assertEqual(result.line1, "123 Main St")
        self.assertIsNone(result.line2)
        self.assertIsNone(result.county)
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_multiple_counties_takes_last_found(
        self,
    ) -> None:
        """Test when multiple counties present, takes last found (from last to first check)."""
        result = format_address(
            "Hampshire$123 Main St$Greater London", "Springfield", "SP1 2AB"
        )

        # Should find Greater London first (checking from last to first)
        self.assertEqual(result.line1, "Hampshire")
        self.assertEqual(result.line2, "123 Main St")
        self.assertEqual(result.county, "Greater London")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_county_with_whitespace(self) -> None:
        """Test county detection with extra whitespace."""
        result = format_address("123 Main St$  Hampshire  ", "Springfield", "SP1 2AB")

        self.assertEqual(result.line1, "123 Main St")
        self.assertIsNone(result.line2)
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_county_case_insensitive(self) -> None:
        """Test county detection is case insensitive."""
        result = format_address("123 Main St$hampshire", "Springfield", "SP1 2AB")

        self.assertEqual(result.line1, "123 Main St")
        self.assertIsNone(result.line2)
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_preserves_segment_order(self) -> None:
        """Test that segment order is preserved after county removal."""
        result = format_address(
            "First$Second$Hampshire$Third$Fourth", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "First")
        self.assertEqual(result.line2, "Second")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_all_segments_are_counties(self) -> None:
        """Test when all segments are recognized counties."""
        result = format_address(
            "Hampshire$Greater London$West Yorkshire", "Springfield", "SP1 2AB"
        )

        # Should find West Yorkshire (last segment checked first)
        self.assertEqual(result.line1, "Hampshire")
        self.assertEqual(result.line2, "Greater London")
        self.assertEqual(result.county, "West Yorkshire")
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_five_segments(self) -> None:
        """Test address with 5 segments - county should be detected if present."""
        result = format_address(
            "Zain Medical Centre$Edgware Community Hospital$Outpatient D$Burnt Oak Broadway$Edgware",
            "Edgware",
            "HA8 0AD",
        )

        # Verify correct mapping
        self.assertEqual(result.line1, "Zain Medical Centre")
        self.assertEqual(result.line2, "Edgware Community Hospital")
        self.assertEqual(result.postcode, "HA8 0AD")

        # County should be None as no segment is recognized as county
        self.assertIsNone(result.county)

    def test_verify_address_formatting_with_many_segments_no_county(self) -> None:
        """Test address with many segments but no valid county."""
        result = format_address(
            "Line 1$Line 2$Line 3$Line 4$Line 5$Line 6",
            "Unknown",
            "XX1 1XX",
        )

        # Should populate line1 and line2
        self.assertEqual(result.line1, "Line 1")
        self.assertEqual(result.line2, "Line 2")

        # County should be None (no valid county found)
        self.assertIsNone(result.county)

    def test_verify_address_formatting_with_not_available_literal(self) -> None:
        """Test that 'Not Available' string is handled gracefully without errors."""
        result = format_address("Not Available", "Unknown", "")

        # Should treat as empty address
        self.assertIsNone(result)

    def test_verify_address_formatting_with_not_available_variations(self) -> None:
        """Test various 'Not Available' and null-like string formats."""
        invalid_address_values = [
            "Not Available",
            "Not available",
        ]

        for address_value in invalid_address_values:
            with self.subTest(address=address_value):
                result = format_address(address_value, "", "")

                # Should handle gracefully without throwing errors
                # All address lines should be None
                self.assertIsNone(result)

    # =========================================================================
    # Edge Cases

    def test_verify_address_formatting_with_only_separators(self) -> None:
        """Test address containing only '$' separators."""
        result = format_address("$$$", "Town", "POST")

        # Should handle gracefully
        self.assertIsNone(result.line1)
        self.assertIsNone(result.line2)
        self.assertIsNone(result.county)

    def test_verify_address_formatting_with_trailing_separators(self) -> None:
        """Test address with trailing separators."""
        result = format_address("123 Main St$Hampshire$$", "Town", "POST")

        # Should ignore empty segments from trailing separators
        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.county, "Hampshire")

    def test_verify_address_formatting_with_leading_separators(self) -> None:
        """Test address with leading separators."""
        result = format_address("$$123 Main St$Hampshire", "Town", "POST")

        # Should ignore empty segments from leading separators
        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.county, "Hampshire")

    def test_verify_address_formatting_with_special_characters(self) -> None:
        """Test address containing special characters."""
        result = format_address(
            "123 O'Reilly St$Apt #5B$St. Mary's$Hampshire",
            "Springfield",
            "SP1 2AB",
        )

        # Special characters should be preserved
        self.assertEqual(result.line1, "123 O'Reilly St")
        self.assertEqual(result.line2, "Apt #5B")
        self.assertEqual(result.county, "Hampshire")
