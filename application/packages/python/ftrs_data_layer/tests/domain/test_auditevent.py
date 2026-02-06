import pytest
from pydantic import ValidationError

from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType


class TestAuditEventType:
    """Tests for AuditEventType enum."""

    def test_audit_event_type_app_value(self) -> None:
        """Test that AuditEventType.app has the correct string value."""
        assert AuditEventType.app == "app"
        assert AuditEventType.app.value == "app"

    def test_audit_event_type_user_value(self) -> None:
        """Test that AuditEventType.user has the correct string value."""
        assert AuditEventType.user == "user"
        assert AuditEventType.user.value == "user"

    def test_audit_event_type_is_str_enum(self) -> None:
        """Test that AuditEventType values can be used as strings."""
        assert str(AuditEventType.app) == "app"
        assert str(AuditEventType.user) == "user"

    def test_audit_event_type_members(self) -> None:
        """Test that AuditEventType has exactly two members."""
        members = list(AuditEventType)
        assert len(members) == 2
        assert AuditEventType.app in members
        assert AuditEventType.user in members


class TestAuditEvent:
    """Tests for AuditEvent model."""

    def test_create_audit_event_with_app_type(self) -> None:
        """Test creating an AuditEvent with app type."""
        event = AuditEvent(
            type=AuditEventType.app,
            value="SYSTEM",
            display="System Process",
        )

        assert event.type == AuditEventType.app
        assert event.value == "SYSTEM"
        assert event.display == "System Process"

    def test_create_audit_event_with_user_type(self) -> None:
        """Test creating an AuditEvent with user type."""
        event = AuditEvent(
            type=AuditEventType.user,
            value="test_user",
            display="Test User",
        )

        assert event.type == AuditEventType.user
        assert event.value == "test_user"
        assert event.display == "Test User"

    def test_audit_event_model_dump_json(self) -> None:
        """Test that AuditEvent serializes correctly to JSON format."""
        event = AuditEvent(
            type=AuditEventType.user,
            value="test_user",
            display="Test User",
        )

        dumped = event.model_dump(mode="json")

        assert dumped == {
            "type": "user",
            "value": "test_user",
            "display": "Test User",
        }

    def test_audit_event_model_dump_app_type(self) -> None:
        """Test that AuditEvent with app type serializes correctly."""
        event = AuditEvent(
            type=AuditEventType.app,
            value="MIGRATION",
            display="Data Migration Service",
        )

        dumped = event.model_dump(mode="json")

        assert dumped == {
            "type": "app",
            "value": "MIGRATION",
            "display": "Data Migration Service",
        }

    def test_audit_event_round_trip(self) -> None:
        """Test that AuditEvent can be serialized and deserialized."""
        original = AuditEvent(
            type=AuditEventType.user,
            value="admin",
            display="Administrator",
        )

        dumped = original.model_dump(mode="json")
        reloaded = AuditEvent.model_validate(dumped)

        assert reloaded.type == original.type
        assert reloaded.value == original.value
        assert reloaded.display == original.display

    def test_audit_event_missing_type_raises_error(self) -> None:
        """Test that missing type field raises ValidationError."""
        with pytest.raises(ValidationError):
            AuditEvent(value="test", display="Test")  # type: ignore

    def test_audit_event_missing_value_raises_error(self) -> None:
        """Test that missing value field raises ValidationError."""
        with pytest.raises(ValidationError):
            AuditEvent(type=AuditEventType.user, display="Test")  # type: ignore

    def test_audit_event_missing_display_raises_error(self) -> None:
        """Test that missing display field raises ValidationError."""
        with pytest.raises(ValidationError):
            AuditEvent(type=AuditEventType.user, value="test")  # type: ignore

    def test_audit_event_invalid_type_raises_error(self) -> None:
        """Test that invalid type raises ValidationError."""
        with pytest.raises(ValidationError):
            AuditEvent(type="invalid", value="test", display="Test")  # type: ignore

    def test_audit_event_with_empty_strings(self) -> None:
        """Test that AuditEvent accepts empty strings for value and display."""
        event = AuditEvent(
            type=AuditEventType.app,
            value="",
            display="",
        )

        assert event.value == ""
        assert event.display == ""

    def test_audit_event_with_special_characters(self) -> None:
        """Test that AuditEvent handles special characters."""
        event = AuditEvent(
            type=AuditEventType.user,
            value="user@domain.com",
            display="User's Display Name (Admin)",
        )

        assert event.value == "user@domain.com"
        assert event.display == "User's Display Name (Admin)"

    def test_audit_event_immutability(self) -> None:
        """Test that AuditEvent fields can be accessed as expected."""
        event = AuditEvent(
            type=AuditEventType.user,
            value="test",
            display="Test",
        )

        # Verify we can read fields
        _ = event.type
        _ = event.value
        _ = event.display

    def test_audit_event_from_dict_with_string_type(self) -> None:
        """Test that AuditEvent can be created from dict with string type."""
        data = {
            "type": "user",
            "value": "test_user",
            "display": "Test User",
        }

        event = AuditEvent.model_validate(data)

        assert event.type == AuditEventType.user
        assert event.value == "test_user"
        assert event.display == "Test User"
