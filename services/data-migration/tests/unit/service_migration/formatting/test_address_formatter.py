import unittest
from unittest.mock import MagicMock, patch

from service_migration.formatting.address_formatter import (
    _norm,
    format_address,
)


class TestAddressFormatter(unittest.TestCase):
    def test_verify_address_formatting_with_multiple_segments(self) -> None:
        # Input address with multiple segments
        result = format_address(
            "123 Main St$Springfield$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.town, "Springfield")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.postcode, "SP1 2AB")

    def test_verify_address_formatting_with_town_in_segments(self) -> None:
        # Address contains town in the segments, should be removed
        result = format_address(
            "123 Main St$Springfield$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.county, "Hampshire")
        self.assertEqual(result.town, "Springfield")

    def test_verify_address_formatting_with_duplicate_segments(self) -> None:
        # Address contains duplicate segment after normalization
        result = format_address(
            "123 Main St$123 main st$Hampshire", "Springfield", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.county, "Hampshire")

    def test_verify_address_formatting_with_empty_input(self) -> None:
        # Empty input
        result = format_address("", "", "")

        self.assertEqual(result.line1, None)
        self.assertEqual(result.line2, None)
        self.assertEqual(result.county, None)
        self.assertEqual(result.town, "")
        self.assertEqual(result.postcode, "")

    def test_verify_address_formatting_with_case_differences(self) -> None:
        # Town with a different case in segments
        result = format_address(
            "123 Main St$springfield$Hampshire", "SPRINGFIELD", "SP1 2AB"
        )

        self.assertEqual(result.line1, "123 Main St")
        self.assertEqual(result.line2, None)
        self.assertEqual(result.town, "SPRINGFIELD")

    def test_verify_address_formatting_with_multiple_lines(self) -> None:
        # Address with enough segments for line1 and line2
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
        # Setup mock pycountry response
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
        # Setup mock pycountry to return empty
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
        # Setup mock pycountry to raise exception
        mock_pycountry.subdivisions.search_fuzzy.side_effect = Exception(
            "Search failed"
        )

        with patch(
            "service_migration.formatting.address_formatter.UK_COUNTIES", ["Hampshire"]
        ):
            result = format_address("123 Main St$Hampshire", "Springfield", "SP1 2AB")

            self.assertEqual(result.county, "Hampshire")

    def test_verify_text_normalization(self) -> None:
        self.assertEqual(_norm(None), "")
        self.assertEqual(_norm(""), "")
        self.assertEqual(_norm("  Test  String  "), "test string")
        self.assertEqual(_norm("TEST"), "test")
