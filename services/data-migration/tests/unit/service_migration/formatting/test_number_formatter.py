from decimal import Decimal

import pytest

from service_migration.formatting.number_formatter import clean_decimal


class TestCleanDecimal:
    def test_zero(self) -> None:
        """Test that zero is properly handled."""
        result = clean_decimal(Decimal("0"))
        assert result == Decimal("0")

    def test_zero_scientific(self) -> None:
        """Test that zero in scientific notation is properly handled."""
        result = clean_decimal(Decimal("0E-10"))
        assert result == Decimal("0")

    def test_integer(self) -> None:
        """Test that integer values are properly handled."""
        result = clean_decimal(Decimal("42"))
        assert result == Decimal("42")

    def test_decimal_no_trailing_zeros(self) -> None:
        """Test decimal value with no trailing zeros."""
        result = clean_decimal(Decimal("42.42"))
        assert result == Decimal("42.42")

    def test_decimal_trailing_zeros(self) -> None:
        """Test decimal value with trailing zeros."""
        result = clean_decimal(Decimal("42.4200"))
        assert result == Decimal("42.42")

    def test_decimal_many_decimal_places(self) -> None:
        """Test decimal value with many decimal places gets rounded."""
        result = clean_decimal(Decimal("42.426789"))
        assert result == Decimal("42.43")  # Rounded up

    def test_scientific_notation(self) -> None:
        """Test scientific notation is normalized."""
        result = clean_decimal(Decimal("4.2E+1"))
        assert result == Decimal("42")

    def test_very_small_value(self) -> None:
        """Test very small value gets properly formatted."""
        result = clean_decimal(Decimal("0.000001"))
        assert result == Decimal("0")  # Rounded to 0 with 2 decimal places

    def test_value_at_rounding_threshold(self) -> None:
        """Test value at rounding threshold."""
        result = clean_decimal(Decimal("0.005"))
        assert result == Decimal("0.01")  # Round up

    def test_negative_value(self) -> None:
        """Test negative values are properly handled."""
        result = clean_decimal(Decimal("-42.426"))
        assert result == Decimal("-42.43")  # Rounded

    def test_exactly_point_5(self) -> None:
        """Test values ending with .5 are rounded correctly (ROUND_HALF_UP)."""
        result = clean_decimal(Decimal("42.425"))
        assert result == Decimal("42.43")  # Should round up

    def test_fractional_value_without_leading_zero(self) -> None:
        """Test fractional value without leading zero."""
        result = clean_decimal(Decimal(".42"))
        assert result == Decimal("0.42")

    def test_large_value(self) -> None:
        """Test large values are properly handled."""
        result = clean_decimal(Decimal("12345678901234567890.123456789"))
        assert result == Decimal("12345678901234567890.12")

    @pytest.mark.parametrize(
        "input_value,expected_result",
        [
            (Decimal("0"), Decimal("0")),
            (Decimal("1"), Decimal("1")),
            (Decimal("1.0"), Decimal("1")),
            (Decimal("1.00"), Decimal("1")),
            (Decimal("1.234"), Decimal("1.23")),
            (Decimal("1.235"), Decimal("1.24")),  # Test rounding up
            (Decimal("0.005"), Decimal("0.01")),  # Test small value rounding
            (Decimal("-1.235"), Decimal("-1.24")),  # Test negative rounding
            (Decimal("1E+2"), Decimal("100")),  # Test scientific notation
            (Decimal("0.00001"), Decimal("0")),  # Test very small value
            (Decimal("47481.5000000000"), Decimal("47481.5")),  # Test trailing zeros
        ],
    )
    def test_parameterized_values(
        self, input_value: Decimal, expected_result: Decimal
    ) -> None:
        """Parameterized test for various input values."""
        result = clean_decimal(input_value)
        assert result == expected_result
