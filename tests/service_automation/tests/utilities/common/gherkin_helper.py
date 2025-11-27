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
