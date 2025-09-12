import pytest

from pipeline.utils.transformer_utils import (
    extract_organisation_public_name,
)


def test_clean_name_with_hyphen() -> None:
    """
    Test that clean_name extracts the part before the first hyphen.
    """
    assert extract_organisation_public_name("GP - Name") == "GP"


def test_clean_name_without_hyphen() -> None:
    """
    Test that clean_name returns the full string if no hyphen is present.
    """
    assert extract_organisation_public_name("GP Name") == "GP Name"


def test_clean_name_with_multiple_hyphens() -> None:
    """
    Test that clean_name extracts the part before the first hyphen, ignoring subsequent hyphens.
    """
    assert extract_organisation_public_name("GP Name - Place") == "GP Name"


def test_clean_name_with_hyphen_at_start() -> None:
    """
    Test that clean_name returns an empty string if the hyphen is at the start.
    """
    assert extract_organisation_public_name("-GP") == ""


def test_clean_name_with_trailing_spaces() -> None:
    """
    Test that clean_name trims trailing spaces before extracting the part before the hyphen.
    """
    assert extract_organisation_public_name("GP Name   - Detail") == "GP Name"


def test_clean_name_empty_string() -> None:
    """
    Test that clean_name raises a ValueError for an empty string.
    """
    with pytest.raises(ValueError, match="publicname is not set"):
        extract_organisation_public_name("")


def test_clean_name_none() -> None:
    """
    Test that clean_name raises a ValueError for a None value.
    """
    with pytest.raises(ValueError, match="publicname is not set"):
        extract_organisation_public_name(None)
