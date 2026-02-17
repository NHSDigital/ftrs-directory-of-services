import json
import pytest


def try_parse_json(docstring: str) -> dict:
    try:
        return json.loads(docstring)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON: {e}")
