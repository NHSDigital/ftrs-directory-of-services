"""Change detection utilities for version history."""

import re
from typing import Any

from deepdiff import DeepDiff

# Fields to exclude from change detection (metadata fields)
EXCLUDE_PATHS = [
    "root['createdTime']",
    "root['lastUpdated']",
]


def detect_changes(
    old_document: dict[str, Any], new_document: dict[str, Any]
) -> dict[str, dict[str, Any]]:  # noqa: PLR0912
    """
    Detect changes between old and new document versions.

    Uses DeepDiff to identify all field changes, excluding metadata fields
    like createdTime and lastUpdated.

    Args:
        old_document: The previous version of the document
        new_document: The current version of the document

    Returns:
        Dictionary mapping field names to old/new value pairs.
        Format: {"field_name": {"old": old_value, "new": new_value}}
        Returns empty dict if no business-relevant changes detected.
    """
    if not old_document or not new_document:
        return {}

    # Perform deep diff, excluding metadata fields
    diff = DeepDiff(
        old_document,
        new_document,
        ignore_order=False,
        report_repetition=True,
        exclude_paths=EXCLUDE_PATHS,
        view="tree",
    )

    changed_fields: dict[str, dict[str, Any]] = {}

    # Process values that changed
    if "values_changed" in diff:
        for change in diff["values_changed"]:
            field_path = _extract_field_path(change.path())
            changed_fields[field_path] = {
                "old": change.t1,
                "new": change.t2,
            }

    # Process type changes (e.g., string to int)
    if "type_changes" in diff:
        for change in diff["type_changes"]:
            field_path = _extract_field_path(change.path())
            changed_fields[field_path] = {
                "old": change.t1,
                "new": change.t2,
            }

    # Process added items
    if "dictionary_item_added" in diff:
        for change in diff["dictionary_item_added"]:
            field_path = _extract_field_path(change.path())
            changed_fields[field_path] = {
                "old": None,
                "new": change.t2,
            }

    # Process removed items
    if "dictionary_item_removed" in diff:
        for change in diff["dictionary_item_removed"]:
            field_path = _extract_field_path(change.path())
            changed_fields[field_path] = {
                "old": change.t1,
                "new": None,
            }

    # Process list changes (items added/removed/modified)
    if "iterable_item_added" in diff:
        for change in diff["iterable_item_added"]:
            field_path = _extract_field_path(change.path())
            # For list changes, capture the entire list
            parent_path = _get_parent_path(change.path())
            if parent_path:
                old_list = _get_nested_value(old_document, parent_path)
                new_list = _get_nested_value(new_document, parent_path)
                changed_fields[parent_path] = {
                    "old": old_list,
                    "new": new_list,
                }

    if "iterable_item_removed" in diff:
        for change in diff["iterable_item_removed"]:
            field_path = _extract_field_path(change.path())
            parent_path = _get_parent_path(change.path())
            if parent_path and parent_path not in changed_fields:
                old_list = _get_nested_value(old_document, parent_path)
                new_list = _get_nested_value(new_document, parent_path)
                changed_fields[parent_path] = {
                    "old": old_list,
                    "new": new_list,
                }

    return changed_fields


def extract_changed_by(document: dict[str, Any]) -> dict[str, str]:
    """
    Extract the lastUpdatedBy audit event from a document.

    Args:
        document: The document containing audit information

    Returns:
        Dictionary with display, type, and value fields from lastUpdatedBy.
        Returns default values if lastUpdatedBy is missing or malformed.
    """
    default_audit = {
        "display": "Unknown",
        "type": "system",
        "value": "unknown",
    }

    if not document:
        return default_audit

    last_updated_by = document.get("lastUpdatedBy")
    if not last_updated_by or not isinstance(last_updated_by, dict):
        return default_audit

    # Validate required fields
    try:
        return {
            "display": str(last_updated_by.get("display", "Unknown")),
            "type": str(last_updated_by.get("type", "system")),
            "value": str(last_updated_by.get("value", "unknown")),
        }
    except (AttributeError, TypeError):
        return default_audit


def _extract_field_path(path: str) -> str:
    """
    Extract a clean field path from a DeepDiff path.

    Converts paths like:
    - root['field'] -> field
    - root['nested']['field'] -> nested.field
    - root['items'][0]['name'] -> items[0].name

    Args:
        path: DeepDiff path string

    Returns:
        Cleaned field path with dot notation
    """
    # Remove 'root' prefix
    path = path.replace("root", "")

    # Replace ['key'] with .key or key
    parts = []
    current = ""
    in_bracket = False
    in_quote = False

    for char in path:
        if char == "[":
            in_bracket = True
            if current:
                parts.append(current)
                current = ""
        elif char == "]":
            in_bracket = False
            if current and not current.isdigit():
                # It's a key, not an index
                current = current.strip("'\"")
                parts.append(current)
                current = ""
            elif current.isdigit():
                # It's an array index
                parts[-1] = f"{parts[-1]}[{current}]" if parts else f"[{current}]"
                current = ""
        elif char in {"'", '"'}:
            in_quote = not in_quote
        elif not in_bracket:
            current += char
        else:
            current += char

    if current:
        parts.append(current.strip("'\""))

    return ".".join(parts).strip(".")


def _get_parent_path(path: str) -> str | None:
    """
    Get the parent path from a DeepDiff path (removes array index).

    Args:
        path: DeepDiff path string

    Returns:
        Parent path or None if no parent
    """
    # Remove array index at the end: root['items'][0] -> root['items']

    match = re.search(r"\[\d+\]$", path)
    if match:
        parent = path[: match.start()]
        return _extract_field_path(parent)
    return None


def _get_nested_value(obj: dict[str, Any], path: str) -> Any:  # noqa: ANN401
    """
    Get a nested value from an object using dot notation path.

    Args:
        obj: The object to traverse
        path: Dot notation path (e.g., "nested.field")

    Returns:
        The value at the path, or None if not found
    """
    parts = path.split(".")
    current = obj

    for part in parts:
        # Handle array indices in the part (e.g., "items[0]")
        if "[" in part and "]" in part:
            key = part[: part.index("[")]
            index_str = part[part.index("[") + 1 : part.index("]")]
            index = int(index_str)
            if key:
                current = current.get(key)
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None

        if current is None:
            return None

    return current
