"""Parse and extract data from CloudWatch alarm messages."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def flatten_dict(
    data: dict[str, Any], parent_key: str = "", sep: str = "_"
) -> dict[str, Any]:
    """
    Flatten nested dictionary to single level.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Dict: Flattened dictionary
    """
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))

    return dict(items)


def parse_cloudwatch_alarm(message: str) -> dict[str, Any]:
    """
    Parse CloudWatch alarm SNS message.

    Args:
        message: SNS message body

    Returns:
        Dict: Parsed alarm data
    """
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        logger.exception("Failed to parse alarm message")
        return {"raw_message": message}
