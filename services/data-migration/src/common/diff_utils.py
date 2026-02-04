"""Utilities for converting DeepDiff results to DynamoDB update expressions."""

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from boto3.dynamodb.types import TypeSerializer
from deepdiff import DeepDiff
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.auditevent import AuditEvent

# Type alias for DynamoDB-compatible values
DynamoDBValue = str | int | float | bool | list | dict | Decimal | None

# DynamoDB reserved words requiring placeholder names
DYNAMODB_RESERVED_WORDS = frozenset(
    {
        "name",
        "type",
        "status",
        "active",
        "location",
        "address",
        "order",
        "comment",
        "value",
        "date",
        "time",
        "start",
        "end",
        "source",
        "id",
        "count",
        "size",
    }
)
EXCLUDE_PATHS = [
    "root['createdTime']",
    "root['lastUpdated']",
]
EXCLUDE_REGEX_PATHS = [
    r"root\['endpoints'\]\[\d+\]\['createdTime'\]",
    r"root\['endpoints'\]\[\d+\]\['lastUpdated'\]",
    r"root\['endpoints'\]\[\d+\]\['createdBy'\]",
    r"root\['endpoints'\]\[\d+\]\['lastUpdatedBy'\]",
]


@dataclass
class DynamoDBUpdateExpressions:
    """Components needed for a DynamoDB UpdateItem operation."""

    update_expression: str = ""
    expression_attribute_names: dict[str, str] = field(default_factory=dict)
    expression_attribute_values: dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Check if there are no update expressions."""
        return not self.update_expression

    def get_expression_attribute_names_or_none(self) -> dict[str, str] | None:
        """Return attribute names dict, or None if empty (DynamoDB rejects empty dicts)."""
        return self.expression_attribute_names or None

    def get_expression_attribute_values_or_none(self) -> dict[str, Any] | None:
        """Return attribute values dict, or None if empty (DynamoDB rejects empty dicts)."""
        return self.expression_attribute_values or None

    def add_audit_timestamps(
        self,
        timestamp: datetime,
        updated_by: AuditEvent,
        serializer: TypeSerializer,
    ) -> None:
        """Add audit timestamp fields to the update expression.

        Args:
            timestamp: ISO format timestamp datetime.
            updated_by: AuditEvent object with type, value, and display fields.
            serializer: DynamoDB type serializer.

        Raises:
            ValueError: If updated_by is missing required keys or timestamp is invalid.
        """
        self._validate_audit_inputs(timestamp, updated_by)
        self._register_audit_field_names()
        self._serialize_audit_field_values(timestamp, updated_by, serializer)
        self._prepend_audit_clauses_to_expression()

    def _validate_audit_inputs(self, timestamp: str, updated_by: AuditEvent) -> None:
        """Validate audit timestamp inputs."""
        if not timestamp:
            raise ValueError("timestamp cannot be empty")

        if not isinstance(updated_by, AuditEvent):
            raise TypeError("updated_by must be an AuditEvent instance")

    def _register_audit_field_names(self) -> None:
        """Register attribute name placeholders for audit fields."""
        self.expression_attribute_names["#lastUpdated"] = "lastUpdated"
        self.expression_attribute_names["#lastUpdatedBy"] = "lastUpdatedBy"

    def _serialize_audit_field_values(
        self,
        timestamp: str,
        updated_by: AuditEvent,
        serializer: TypeSerializer,
    ) -> None:
        """Serialize and store audit field values."""
        self.expression_attribute_values[":lastUpdated"] = serializer.serialize(
            timestamp
        )
        self.expression_attribute_values[":lastUpdatedBy"] = serializer.serialize(
            updated_by.model_dump()
        )

    def _prepend_audit_clauses_to_expression(self) -> None:
        """Add audit SET clauses to the beginning of the update expression."""
        audit_set_clause = (
            "#lastUpdated = :lastUpdated, #lastUpdatedBy = :lastUpdatedBy"
        )

        if self._has_existing_set_clause():
            self.update_expression = self._insert_after_set_keyword(audit_set_clause)
        else:
            self.update_expression = self._create_new_set_clause(audit_set_clause)

    def _has_existing_set_clause(self) -> bool:
        """Check if the update expression already contains a SET clause."""
        return bool(re.search(r"\bSET\b", self.update_expression))

    def _insert_after_set_keyword(self, audit_clause: str) -> str:
        """Insert audit clause immediately after the SET keyword."""
        pattern = r"(\bSET\s+)"
        replacement = rf"\1{audit_clause}, "
        return re.sub(pattern, replacement, self.update_expression, count=1)

    def _create_new_set_clause(self, audit_clause: str) -> str:
        """Create a new SET clause with audit fields."""
        if not self.update_expression:
            return f"SET {audit_clause}"
        return f"SET {audit_clause} {self.update_expression}"


class DeepDiffToDynamoDBConverter:
    """
    Converts DeepDiff results to DynamoDB UpdateItem expressions.

    Handles all DeepDiff change types: values_changed, type_changes,
    dictionary_item_added/removed, and iterable_item_added/removed.

    When list items are added or removed, the entire list is replaced to avoid
    DynamoDB's overlapping path restrictions.
    """

    def __init__(self, diff: DeepDiff) -> None:
        self._diff = diff
        self._serialiser = TypeSerializer()
        self._set_clauses: list[str] = []
        self._remove_clauses: list[str] = []
        self._attribute_names: dict[str, str] = {}
        self._attribute_values: dict[str, Any] = {}
        self._value_counter = 0
        self._replaced_list_paths: set[str] = set()

    def convert(self) -> DynamoDBUpdateExpressions:
        """Convert the DeepDiff to DynamoDB update expressions."""
        if not self._diff:
            return DynamoDBUpdateExpressions()

        self._identify_replaced_lists()
        self._process_all_changes()
        return self._build_result()

    def _identify_replaced_lists(self) -> None:
        """Find lists that will be fully replaced due to item additions/removals."""
        for change_type in ("iterable_item_added", "iterable_item_removed"):
            for change in self._diff.get(change_type, []):
                parent_path = self._strip_list_index(change.path())
                self._replaced_list_paths.add(self._to_dynamodb_path(parent_path))

    def _process_all_changes(self) -> None:
        """Process all change types from the diff."""
        # Process scalar and dictionary changes (skip if inside a replaced list)
        for change in self._diff.get("values_changed", []):
            self._add_set_clause(change.path(), change.t2)

        for change in self._diff.get("type_changes", []):
            self._add_set_clause(change.path(), change.t2)

        for change in self._diff.get("dictionary_item_added", []):
            self._add_set_clause(change.path(), change.t2)

        for change in self._diff.get("dictionary_item_removed", []):
            self._add_remove_clause(change.path())

        # Process list changes (replace entire list)
        self._process_list_changes("iterable_item_added")
        self._process_list_changes("iterable_item_removed")

    def _process_list_changes(self, change_type: str) -> None:
        """Replace entire lists when items are added or removed."""
        processed_paths: set[str] = set()

        for change in self._diff.get(change_type, []):
            parent_path = self._strip_list_index(change.path())
            ddb_path = self._to_dynamodb_path(parent_path)

            if ddb_path in processed_paths:
                continue

            processed_paths.add(ddb_path)
            new_list = change.up.t2  # Get the complete new list from parent
            if isinstance(new_list, list):
                self._add_set_clause_direct(ddb_path, new_list)

    def _add_set_clause(self, path: str, value: Any) -> None:  # noqa: ANN401
        """Add a SET clause, skipping paths inside replaced lists."""
        ddb_path = self._to_dynamodb_path(path)
        if self._is_inside_replaced_list(ddb_path):
            return
        self._add_set_clause_direct(ddb_path, value)

    def _add_set_clause_direct(self, ddb_path: str, value: Any) -> None:  # noqa: ANN401
        """Add a SET clause without checking for replaced lists."""
        value_placeholder = self._register_value(value)
        self._set_clauses.append(f"{ddb_path} = {value_placeholder}")

    def _add_remove_clause(self, path: str) -> None:
        """Add a REMOVE clause, skipping paths inside replaced lists."""
        ddb_path = self._to_dynamodb_path(path)
        if self._is_inside_replaced_list(ddb_path):
            return
        self._remove_clauses.append(ddb_path)

    def _is_inside_replaced_list(self, path: str) -> bool:
        """Check if path is nested within a list being fully replaced."""
        return any(path.startswith(f"{lp}[") for lp in self._replaced_list_paths)

    def _to_dynamodb_path(self, path: str) -> str:
        """
        Convert DeepDiff path to DynamoDB expression path.

        Example: root['endpoints'][0]['status'] -> #endpoints[0].#attr_status
        """
        path = path.removeprefix("root")
        if not path:
            return ""

        parts = self._parse_path_components(path)
        ddb_parts: list[str] = []

        for part in parts:
            if isinstance(part, int):
                # Append array index to previous part
                if ddb_parts:
                    ddb_parts[-1] = f"{ddb_parts[-1]}[{part}]"
                else:
                    ddb_parts.append(f"[{part}]")
            else:
                ddb_parts.append(self._register_attribute_name(part))

        return ".".join(ddb_parts)

    def _parse_path_components(self, path: str) -> list[str | int]:
        """Parse path string into components (strings for keys, ints for indices)."""
        parts: list[str | int] = []
        i = 0

        while i < len(path):
            if path[i] != "[":
                i += 1
                continue

            j = path.index("]", i)
            content = path[i + 1 : j]

            if content.startswith("'") and content.endswith("'"):
                parts.append(content[1:-1])  # String key
            else:
                parts.append(int(content))  # Numeric index

            i = j + 1

        return parts

    def _strip_list_index(self, path: str) -> str:
        """Remove the trailing list index from a path: root['x'][0] -> root['x']"""
        match = re.search(r"\[\d+\]$", path)
        return path[: match.start()] if match else path

    def _register_attribute_name(self, name: str) -> str:
        """Register an attribute name and return its placeholder."""
        # Return existing placeholder if already registered
        for placeholder, attr_name in self._attribute_names.items():
            if attr_name == name:
                return placeholder

        # Create new placeholder (prefix reserved words to avoid conflicts)
        if name in DYNAMODB_RESERVED_WORDS:
            placeholder = f"#attr_{name}"
        else:
            placeholder = f"#{name}"

        self._attribute_names[placeholder] = name
        return placeholder

    def _register_value(self, value: Any) -> str:  # noqa: ANN401
        """Register a value and return its placeholder."""
        placeholder = f":val_{self._value_counter}"
        self._value_counter += 1

        prepared = self._prepare_for_dynamodb(value)
        self._attribute_values[placeholder] = self._serialiser.serialize(prepared)
        return placeholder

    def _prepare_for_dynamodb(  # noqa: PLR0911
        self,
        value: DynamoDBValue | UUID | time | datetime | date | Enum,
    ) -> DynamoDBValue:
        """Convert value to a DynamoDB-serializable type."""
        if value is None:
            return None
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, list):
            return [self._prepare_for_dynamodb(item) for item in value]
        if isinstance(value, dict):
            return {k: self._prepare_for_dynamodb(v) for k, v in value.items()}
        return value

    def _build_result(self) -> DynamoDBUpdateExpressions:
        """Build the final update expressions, removing unused placeholders."""
        parts = []
        if self._set_clauses:
            parts.append("SET " + ", ".join(self._set_clauses))
        if self._remove_clauses:
            parts.append("REMOVE " + ", ".join(self._remove_clauses))

        expression = " ".join(parts)

        # Filter to only include placeholders actually used in the expression
        used_names = {k: v for k, v in self._attribute_names.items() if k in expression}
        used_values = {
            k: v for k, v in self._attribute_values.items() if k in expression
        }

        return DynamoDBUpdateExpressions(
            update_expression=expression,
            expression_attribute_names=used_names,
            expression_attribute_values=used_values,
        )


def deepdiff_to_dynamodb_expressions(diff: DeepDiff) -> DynamoDBUpdateExpressions:
    """Convert a DeepDiff result to DynamoDB update expressions."""
    return DeepDiffToDynamoDBConverter(diff).convert()


def get_organisation_diff(previous: Organisation, current: Organisation) -> DeepDiff:
    """Get differences between two Organisation records, excluding timestamps."""
    return DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        exclude_paths=EXCLUDE_PATHS,
        exclude_regex_paths=EXCLUDE_REGEX_PATHS,
        view="tree",
        threshold_to_diff_deeper=0,
        ignore_order=True,
    )


def get_location_diff(previous: Location, current: Location) -> DeepDiff:
    """Get differences between two Location records, excluding timestamps."""
    return DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        exclude_paths=EXCLUDE_PATHS,
        view="tree",
        threshold_to_diff_deeper=0,
        ignore_order=True,
    )


def get_healthcare_service_diff(
    previous: HealthcareService,
    current: HealthcareService,
) -> DeepDiff:
    """Get differences between two HealthcareService records, excluding timestamps."""
    return DeepDiff(
        previous.model_dump(),
        current.model_dump(),
        exclude_paths=EXCLUDE_PATHS,
        view="tree",
        threshold_to_diff_deeper=0,
        ignore_order=True,
    )
