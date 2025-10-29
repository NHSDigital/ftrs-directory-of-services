from decimal import Decimal


def clean_decimal(value: Decimal) -> Decimal:
    """
    Clean a Decimal value for DynamoDB storage by ensuring:
    * normalised representation to remove scientific notation
    * at most 2 decimal places.

    The ROUND_HALF_UP strategy used to ensures consistent handling of decimal values
    * important when comparing values against the fixed tolerance of 1 day for range comparisons
    * ensure that ranges like 364.25 and 365.25 are correctly identified as consecutive
    """
    if value == 0:
        return Decimal(0)

    rounded_value = value.quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")

    clean_str = str(rounded_value.normalize())

    if "." in clean_str:
        clean_str = clean_str.rstrip("0").rstrip(".")

    return Decimal(clean_str)
