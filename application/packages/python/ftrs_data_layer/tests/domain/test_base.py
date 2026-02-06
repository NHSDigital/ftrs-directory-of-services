from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.domain.base import DBModel, audit_default_value


class TestAuditDefaultValue:
    """Tests for the audit_default_value constant."""

    def test_audit_default_value_type(self) -> None:
        """Test that audit_default_value has app type."""
        assert audit_default_value.type == AuditEventType.app

    def test_audit_default_value_value(self) -> None:
        """Test that audit_default_value has SYSTEM value."""
        assert audit_default_value.value == "SYSTEM"

    def test_audit_default_value_display(self) -> None:
        """Test that audit_default_value has SYSTEM display."""
        assert audit_default_value.display == "SYSTEM"


class TestDBModel:
    """Tests for DBModel base class."""

    def test_create_db_model_with_defaults(self) -> None:
        """Test creating DBModel with all default values."""
        model = DBModel()

        assert isinstance(model.id, UUID)
        assert isinstance(model.createdTime, datetime)
        assert isinstance(model.lastUpdated, datetime)
        assert isinstance(model.createdBy, AuditEvent)
        assert isinstance(model.lastUpdatedBy, AuditEvent)

    def test_db_model_id_is_uuid(self) -> None:
        """Test that DBModel id is a valid UUID."""
        model = DBModel()
        # Verify it can be converted to string and back to UUID
        uuid_str = str(model.id)
        UUID(uuid_str)  # Should not raise

    def test_db_model_generates_unique_ids(self) -> None:
        """Test that each DBModel instance gets a unique id."""
        model1 = DBModel()
        model2 = DBModel()

        assert model1.id != model2.id

    def test_db_model_with_custom_id(self) -> None:
        """Test creating DBModel with custom id."""
        custom_id = uuid4()
        model = DBModel(id=custom_id)

        assert model.id == custom_id

    def test_db_model_created_time_is_utc(self) -> None:
        """Test that createdTime has UTC timezone."""
        before = datetime.now(UTC)
        model = DBModel()
        after = datetime.now(UTC)

        assert model.createdTime >= before
        assert model.createdTime <= after

    def test_db_model_last_updated_is_utc(self) -> None:
        """Test that lastUpdated has UTC timezone."""
        before = datetime.now(UTC)
        model = DBModel()
        after = datetime.now(UTC)

        assert model.lastUpdated >= before
        assert model.lastUpdated <= after

    def test_db_model_with_custom_audit_events(self) -> None:
        """Test creating DBModel with custom audit events."""
        custom_created_by = AuditEvent(
            type=AuditEventType.user,
            value="admin",
            display="Administrator",
        )
        custom_last_updated_by = AuditEvent(
            type=AuditEventType.user,
            value="editor",
            display="Editor",
        )

        model = DBModel(
            createdBy=custom_created_by,
            lastUpdatedBy=custom_last_updated_by,
        )

        assert model.createdBy.type == AuditEventType.user
        assert model.createdBy.value == "admin"
        assert model.lastUpdatedBy.type == AuditEventType.user
        assert model.lastUpdatedBy.value == "editor"

    def test_db_model_with_custom_times(self) -> None:
        """Test creating DBModel with custom times."""
        custom_created_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
        custom_last_updated = datetime(2023, 6, 15, 14, 30, 0, tzinfo=UTC)

        model = DBModel(
            createdTime=custom_created_time,
            lastUpdated=custom_last_updated,
        )

        assert model.createdTime == custom_created_time
        assert model.lastUpdated == custom_last_updated

    def test_db_model_model_dump_json(self) -> None:
        """Test DBModel serialization to JSON."""
        custom_id = uuid4()
        model = DBModel(id=custom_id)

        dumped = model.model_dump(mode="json")

        assert dumped["id"] == str(custom_id)
        assert "createdTime" in dumped
        assert "lastUpdated" in dumped
        assert isinstance(dumped["createdBy"], dict)
        assert isinstance(dumped["lastUpdatedBy"], dict)

    def test_db_model_createdBy_default_in_json(self) -> None:
        """Test that default createdBy is serialized correctly."""
        model = DBModel()
        dumped = model.model_dump(mode="json")

        assert dumped["createdBy"]["type"] == "app"
        assert dumped["createdBy"]["value"] == "SYSTEM"
        assert dumped["createdBy"]["display"] == "SYSTEM"

    def test_db_model_lastUpdatedBy_default_in_json(self) -> None:
        """Test that default lastUpdatedBy is serialized correctly."""
        model = DBModel()
        dumped = model.model_dump(mode="json")

        assert dumped["lastUpdatedBy"]["type"] == "app"
        assert dumped["lastUpdatedBy"]["value"] == "SYSTEM"
        assert dumped["lastUpdatedBy"]["display"] == "SYSTEM"

    def test_db_model_round_trip(self) -> None:
        """Test DBModel serialization and deserialization."""
        original = DBModel()

        dumped = original.model_dump(mode="json")
        reloaded = DBModel.model_validate(dumped)

        assert reloaded.id == original.id
        assert reloaded.createdBy.type == original.createdBy.type
        assert reloaded.createdBy.value == original.createdBy.value
        assert reloaded.lastUpdatedBy.type == original.lastUpdatedBy.type

    def test_db_model_round_trip_with_custom_values(self) -> None:
        """Test DBModel round trip with custom values."""
        custom_audit = AuditEvent(
            type=AuditEventType.user,
            value="test_user",
            display="Test User",
        )

        original = DBModel(
            createdBy=custom_audit,
            lastUpdatedBy=custom_audit,
        )

        dumped = original.model_dump(mode="json")
        reloaded = DBModel.model_validate(dumped)

        assert reloaded.createdBy.type == AuditEventType.user
        assert reloaded.createdBy.value == "test_user"
        assert reloaded.createdBy.display == "Test User"

    def test_db_model_with_all_custom_fields(self) -> None:
        """Test creating DBModel with all fields customized."""
        custom_id = uuid4()
        custom_time = datetime(2024, 3, 15, 10, 30, 0, tzinfo=UTC)
        custom_audit = AuditEvent(
            type=AuditEventType.app,
            value="MIGRATION",
            display="Migration Service",
        )

        model = DBModel(
            id=custom_id,
            createdTime=custom_time,
            lastUpdated=custom_time,
            createdBy=custom_audit,
            lastUpdatedBy=custom_audit,
        )

        assert model.id == custom_id
        assert model.createdTime == custom_time
        assert model.lastUpdated == custom_time
        assert model.createdBy.value == "MIGRATION"
        assert model.lastUpdatedBy.value == "MIGRATION"

    def test_db_model_invalid_id_raises_error(self) -> None:
        """Test that invalid UUID raises ValidationError."""
        with pytest.raises(ValidationError):
            DBModel(id="not-a-uuid")  # type: ignore

    def test_db_model_invalid_audit_event_raises_error(self) -> None:
        """Test that invalid audit event raises ValidationError."""
        with pytest.raises(ValidationError):
            DBModel(createdBy="not-an-audit-event")  # type: ignore
