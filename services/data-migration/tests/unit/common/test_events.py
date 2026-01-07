"""Tests for common/events.py module."""

import pytest
from pydantic import ValidationError

from common.events import DMSEvent, ReferenceDataLoadEvent


def test_dms_event_valid_creation() -> None:
    """Test creating a valid DMSEvent."""
    event = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )

    assert event.record_id == 123
    assert event.service_id == 456
    assert event.table_name == "services"
    assert event.method == "insert"


def test_dms_event_valid_methods() -> None:
    """Test that all valid methods are accepted."""
    valid_methods = ["insert", "update", "delete"]

    for method in valid_methods:
        event = DMSEvent(
            record_id=1,
            service_id=1,
            table_name="test_table",
            method=method,
        )
        assert event.method == method


def test_dms_event_method_lowercase_only() -> None:
    """Test that method must be lowercase."""
    event = DMSEvent(
        record_id=1,
        service_id=1,
        table_name="services",
        method="insert",
    )

    assert event.method == "insert"


def test_dms_event_uppercase_method_rejected() -> None:
    """Test that uppercase methods are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DMSEvent(
            record_id=1,
            service_id=1,
            table_name="services",
            method="UPDATE",
        )

    assert "method" in str(exc_info.value)


def test_dms_event_invalid_method() -> None:
    """Test that invalid methods raise validation error."""
    with pytest.raises(ValidationError) as exc_info:
        DMSEvent(
            record_id=1,
            service_id=1,
            table_name="services",
            method="invalid_method",
        )

    assert "method" in str(exc_info.value)


def test_dms_event_missing_required_fields() -> None:
    """Test that missing required fields raise validation error."""
    with pytest.raises(ValidationError) as exc_info:
        DMSEvent(record_id=1, service_id=1)

    assert "table_name" in str(exc_info.value)
    assert "method" in str(exc_info.value)


def test_dms_event_zero_ids() -> None:
    """Test that zero IDs are valid."""
    event = DMSEvent(
        record_id=0,
        service_id=0,
        table_name="services",
        method="insert",
    )

    assert event.record_id == 0
    assert event.service_id == 0


def test_dms_event_negative_ids() -> None:
    """Test that negative IDs are accepted (edge case)."""
    event = DMSEvent(
        record_id=-1,
        service_id=-1,
        table_name="services",
        method="delete",
    )

    assert event.record_id == -1
    assert event.service_id == -1


def test_dms_event_large_ids() -> None:
    """Test that large IDs are handled correctly."""
    large_id = 999999999
    event = DMSEvent(
        record_id=large_id,
        service_id=large_id,
        table_name="services",
        method="update",
    )

    assert event.record_id == large_id
    assert event.service_id == large_id


def test_dms_event_different_table_names() -> None:
    """Test that different table names are accepted."""
    table_names = ["services", "locations", "organisations", "endpoints"]

    for table_name in table_names:
        event = DMSEvent(
            record_id=1,
            service_id=1,
            table_name=table_name,
            method="insert",
        )
        assert event.table_name == table_name


def test_dms_event_model_dump() -> None:
    """Test that DMSEvent can be serialized to dict."""
    event = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )

    data = event.model_dump()

    assert data == {
        "record_id": 123,
        "service_id": 456,
        "table_name": "services",
        "method": "insert",
    }


def test_dms_event_model_dump_json() -> None:
    """Test that DMSEvent can be serialized to JSON."""
    event = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="update",
    )

    json_data = event.model_dump_json()

    assert isinstance(json_data, str)
    assert "123" in json_data
    assert "456" in json_data
    assert "services" in json_data
    assert "update" in json_data


def test_dms_event_from_dict() -> None:
    """Test creating DMSEvent from dictionary."""
    data = {
        "record_id": 789,
        "service_id": 101,
        "table_name": "locations",
        "method": "delete",
    }

    event = DMSEvent(**data)

    assert event.record_id == 789
    assert event.service_id == 101
    assert event.table_name == "locations"
    assert event.method == "delete"


def test_reference_data_load_event_valid_creation() -> None:
    """Test creating a valid ReferenceDataLoadEvent."""
    event = ReferenceDataLoadEvent(type="triagecode")

    assert event.type == "triagecode"


def test_reference_data_load_event_type_literal() -> None:
    """Test that only 'triagecode' type is accepted."""
    event = ReferenceDataLoadEvent(type="triagecode")
    assert event.type == "triagecode"


def test_reference_data_load_event_invalid_type() -> None:
    """Test that invalid types raise validation error."""
    with pytest.raises(ValidationError) as exc_info:
        ReferenceDataLoadEvent(type="invalid_type")

    assert "type" in str(exc_info.value)


def test_reference_data_load_event_missing_type() -> None:
    """Test that missing type field raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        ReferenceDataLoadEvent()

    assert "type" in str(exc_info.value)


def test_reference_data_load_event_model_dump() -> None:
    """Test that ReferenceDataLoadEvent can be serialized to dict."""
    event = ReferenceDataLoadEvent(type="triagecode")

    data = event.model_dump()

    assert data == {"type": "triagecode"}


def test_reference_data_load_event_model_dump_json() -> None:
    """Test that ReferenceDataLoadEvent can be serialized to JSON."""
    event = ReferenceDataLoadEvent(type="triagecode")

    json_data = event.model_dump_json()

    assert isinstance(json_data, str)
    assert "triagecode" in json_data


def test_reference_data_load_event_from_dict() -> None:
    """Test creating ReferenceDataLoadEvent from dictionary."""
    data = {"type": "triagecode"}

    event = ReferenceDataLoadEvent(**data)

    assert event.type == "triagecode"


def test_dms_event_equality() -> None:
    """Test that two identical DMSEvents are equal."""
    event1 = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )
    event2 = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )

    assert event1 == event2


def test_dms_event_inequality() -> None:
    """Test that different DMSEvents are not equal."""
    event1 = DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )
    event2 = DMSEvent(
        record_id=789,
        service_id=456,
        table_name="services",
        method="insert",
    )

    assert event1 != event2


def test_reference_data_load_event_equality() -> None:
    """Test that two identical ReferenceDataLoadEvents are equal."""
    event1 = ReferenceDataLoadEvent(type="triagecode")
    event2 = ReferenceDataLoadEvent(type="triagecode")

    assert event1 == event2
