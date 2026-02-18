"""Gherkin table parsing utilities."""

from typing import Any, Dict, List


def parse_gherkin_table(datatable: List[List[str]]) -> Dict[str, Any]:
    """
    Parse Gherkin datatable into dictionary with type conversion.

    Converts string values to appropriate Python types:
    - "true"/"false" → bool
    - numeric strings → int
    - everything else → str

    Args:
        datatable: Gherkin table as list of lists (first row is header)

    Returns:
        Dictionary of parsed attributes
    """
    attributes = {}

    for row in datatable[1:]:  # Skip header row
        key, value = row[0], row[1]

        # Type conversion
        if value.lower() in ("true", "false"):
            attributes[key] = value.lower() == "true"
        elif value.isdigit():
            attributes[key] = int(value)
        else:
            attributes[key] = value

    return attributes


def unescape_pipe_in_value(value: str) -> str:
    """
    Unescape pipe characters from Gherkin table values.

    When reading expected values from feature files that contain pipes,
    they appear as \\| and need to be unescaped for comparison with
    actual values from the database.

    Args:
        value: String with escaped pipes (\\|)

    Returns:
        String with actual pipe characters
    """
    return value.replace("\\|", "|")
