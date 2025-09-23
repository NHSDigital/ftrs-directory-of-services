import os
import json
import logging

logger = logging.getLogger(__name__)

def read_json_file(relative_path):
    """
    Reads a JSON file from a relative path (relative to this script).

    Args:
        relative_path (str): Path to the JSON file relative to this file.

    Returns:
        dict or list: Parsed JSON content.
    """
    base_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(base_dir, relative_path))

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {file_path}: {e}")
        raise

def write_json_file(data, relative_path):
    """
    Writes Python data as JSON to a file at a relative path.

    Args:
        data (dict or list): Data to write.
        relative_path (str): Path to write JSON file relative to this file.
    """
    base_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(base_dir, relative_path))

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)  # Pretty print with indentation
    except Exception as e:
        logger.error(f"Failed to write JSON to {file_path}: {e}")
        raise

