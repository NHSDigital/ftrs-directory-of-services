from typing import Optional

import pycountry
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import Address
from ftrs_data_layer.logbase import UtilsLogBase

from service_migration.constants import UK_COUNTIES

address_formatter_logger = Logger.get(service="address_formatter")

INVALID_ADDRESS_INDICATORS = {
    "not available",
}


def _norm(text: Optional[str]) -> str:
    """
    Normalize text for comparison:
    - Treat None as empty
    - Trim surrounding whitespace
    - Collapse internal whitespace
    - Lowercase
    """
    if not text:
        return ""
    return " ".join(text.strip().lower().split())


def _is_invalid_address(address: str) -> bool:
    if not address:
        return True

    normalized = _norm(address)

    if normalized in INVALID_ADDRESS_INDICATORS:
        return True

    return False


def _pycountry_county_name_gb(segment: str) -> str | None:
    """
    Use pycountry to recognize GB county-like subdivisions from a free-text segment.
    Returns the canonical subdivision name if recognized, else None.
    """
    if not pycountry:
        return None

    q = (segment or "").strip()
    if not q:
        return None

    # First, check our custom mapping
    try:
        address_formatter_logger.log(
            UtilsLogBase.UTILS_ADDRESS_FORMATTER_001, county_name=q
        )
        matches = pycountry.subdivisions.search_fuzzy(q)
    except Exception as e:
        address_formatter_logger.log(
            UtilsLogBase.UTILS_ADDRESS_FORMATTER_002, error=str(e), county_name=q
        )
        matches = []
    for sub in matches:
        # Only consider Great Britain (United Kingdom) subdivisions
        if getattr(sub, "country_code", None) != "GB":
            continue
        address_formatter_logger.log(
            UtilsLogBase.UTILS_ADDRESS_FORMATTER_003, county_name=sub.name
        )
        return sub.name
    if matches is None or len(matches) == 0:
        address_formatter_logger.log(
            UtilsLogBase.UTILS_ADDRESS_FORMATTER_004, county_name=q
        )
        # Fallback: check against our predefined list of UK counties
        q_norm = _norm(q)
        for county in UK_COUNTIES:
            if _norm(county) == q_norm:
                return county
    address_formatter_logger.log(
        UtilsLogBase.UTILS_ADDRESS_FORMATTER_005, county_name=q
    )
    return None


def _extract_county_from_segments(segments: list[str]) -> tuple[str | None, list[str]]:
    """
    Extract county from any segment in the list.
    Checks all segments from last to first.
    Returns tuple (county_name, remaining_segments_without_county)
    """
    # Check all segments from last to first
    for i in range(len(segments) - 1, -1, -1):
        county_name = _pycountry_county_name_gb(segments[i])
        if county_name:
            # Remove this segment from the list
            remaining = segments[:i] + segments[i + 1 :]
            return (county_name, remaining)

    # No county found
    return (None, segments)


def format_address(address: str, town: str, postcode: str) -> Address | None:
    address_formatter_logger.log(
        UtilsLogBase.UTILS_ADDRESS_FORMATTER_000,
        address=address,
        town=town,
        postcode=postcode,
    )

    address_is_invalid = _is_invalid_address(address)

    if address_is_invalid:
        return None

    # Split address into segments by '$', trim whitespace, drop empties
    segments = [part.strip() for part in (address or "").split("$")]
    segments = [s for s in segments if s]  # drop empty after trimming

    town_norm = _norm(town)
    filtered: list[str] = []
    for seg in segments:
        if town_norm and _norm(seg) == town_norm:
            continue  # ignore the town appearing in the string
        # avoid immediate duplicates after normalization
        if filtered and _norm(seg) == _norm(filtered[-1]):
            continue
        filtered.append(seg)

    # Extract county from any segment (checks all segments and parts)
    county_name, filtered = _extract_county_from_segments(filtered)
    county = county_name.title() if county_name else None

    line1 = filtered[0] if filtered else None
    line2 = filtered[1] if len(filtered) > 1 else None
    return Address(
        line1=line1, line2=line2, county=county, town=town, postcode=postcode
    )
