"""Unit tests for change detection."""

from version_history.change_detector import detect_changes, extract_changed_by


class TestDetectChanges:
    """Test suite for detect_changes function."""

    def test_simple_field_changes(self) -> None:
        """Test detection of simple field changes."""
        old_doc = {
            "name": "Old Name",
            "email": "old@example.com",
            "age": 30,
            "active": False,
        }
        new_doc = {
            "name": "New Name",
            "email": "new@example.com",
            "age": 31,
            "active": True,
        }

        changes = detect_changes(old_doc, new_doc)

        assert len(changes) == 4
        assert changes["name"]["old"] == "Old Name"
        assert changes["name"]["new"] == "New Name"
        assert changes["email"]["old"] == "old@example.com"
        assert changes["email"]["new"] == "new@example.com"
        assert changes["age"]["old"] == 30
        assert changes["age"]["new"] == 31
        assert changes["active"]["old"] is False
        assert changes["active"]["new"] is True

    def test_nested_object_changes(self) -> None:
        """Test detection of nested object changes."""
        old_doc = {
            "contact": {"email": "old@example.com", "phone": "123-456-7890"},
            "address": {"city": "London", "postcode": "SW1A 1AA"},
        }
        new_doc = {
            "contact": {"email": "new@example.com", "phone": "123-456-7890"},
            "address": {"city": "London", "postcode": "SW1A 2BB"},
        }

        changes = detect_changes(old_doc, new_doc)

        assert "contact.email" in changes
        assert changes["contact.email"]["old"] == "old@example.com"
        assert changes["contact.email"]["new"] == "new@example.com"
        assert "address.postcode" in changes
        assert changes["address.postcode"]["old"] == "SW1A 1AA"
        assert changes["address.postcode"]["new"] == "SW1A 2BB"

    def test_list_item_modified(self) -> None:
        """Test detection when list items are modified."""
        old_doc = {
            "endpoints": [
                {"url": "http://old.example.com", "status": "active"},
                {"url": "http://other.example.com", "status": "active"},
            ]
        }
        new_doc = {
            "endpoints": [
                {"url": "http://new.example.com", "status": "active"},
                {"url": "http://other.example.com", "status": "active"},
            ]
        }

        changes = detect_changes(old_doc, new_doc)

        # Should detect the change in the first endpoint's URL
        assert len(changes) > 0
        # The exact key depends on how DeepDiff reports it
        assert any("endpoints" in key for key in changes.keys())

    def test_list_item_added(self) -> None:
        """Test detection when items are added to a list."""
        old_doc = {"endpoints": [{"url": "http://example.com", "status": "active"}]}
        new_doc = {
            "endpoints": [
                {"url": "http://example.com", "status": "active"},
                {"url": "http://new.example.com", "status": "active"},
            ]
        }

        changes = detect_changes(old_doc, new_doc)

        # Should detect that the entire list changed
        assert "endpoints" in changes
        assert len(changes["endpoints"]["old"]) == 1
        assert len(changes["endpoints"]["new"]) == 2

    def test_list_item_removed(self) -> None:
        """Test detection when items are removed from a list."""
        old_doc = {
            "endpoints": [
                {"url": "http://example.com", "status": "active"},
                {"url": "http://removed.example.com", "status": "active"},
            ]
        }
        new_doc = {"endpoints": [{"url": "http://example.com", "status": "active"}]}

        changes = detect_changes(old_doc, new_doc)

        # Should detect that the entire list changed
        assert "endpoints" in changes
        assert len(changes["endpoints"]["old"]) == 2
        assert len(changes["endpoints"]["new"]) == 1

    def test_no_changes(self) -> None:
        """Test when documents are identical."""
        doc = {
            "name": "Test",
            "email": "test@example.com",
            "nested": {"field": "value"},
        }

        changes = detect_changes(doc, doc)

        assert len(changes) == 0

    def test_excluded_fields_ignored(self) -> None:
        """Test that createdTime and lastUpdated are excluded."""
        old_doc = {
            "name": "Test",
            "createdTime": "2024-01-01T00:00:00Z",
            "lastUpdated": "2024-01-01T00:00:00Z",
        }
        new_doc = {
            "name": "Test",
            "createdTime": "2024-01-01T00:00:00Z",
            "lastUpdated": "2024-01-02T00:00:00Z",  # Changed but should be ignored
        }

        changes = detect_changes(old_doc, new_doc)

        # lastUpdated change should be ignored
        assert len(changes) == 0

    def test_type_changes(self) -> None:
        """Test detection of type changes."""
        old_doc = {"count": "10", "active": "true"}
        new_doc = {"count": 10, "active": True}

        changes = detect_changes(old_doc, new_doc)

        assert len(changes) == 2
        assert changes["count"]["old"] == "10"
        assert changes["count"]["new"] == 10
        assert changes["active"]["old"] == "true"
        assert changes["active"]["new"] is True

    def test_field_added(self) -> None:
        """Test detection when a field is added."""
        old_doc = {"name": "Test"}
        new_doc = {"name": "Test", "email": "test@example.com"}

        changes = detect_changes(old_doc, new_doc)

        assert "email" in changes
        assert changes["email"]["old"] is None
        assert changes["email"]["new"] == "test@example.com"

    def test_field_removed(self) -> None:
        """Test detection when a field is removed."""
        old_doc = {"name": "Test", "email": "test@example.com"}
        new_doc = {"name": "Test"}

        changes = detect_changes(old_doc, new_doc)

        assert "email" in changes
        assert changes["email"]["old"] == "test@example.com"
        assert changes["email"]["new"] is None

    def test_empty_documents(self) -> None:
        """Test handling of empty documents."""
        changes = detect_changes({}, {})
        assert len(changes) == 0

        changes = detect_changes(None, {"name": "Test"})
        assert len(changes) == 0

        changes = detect_changes({"name": "Test"}, None)
        assert len(changes) == 0


class TestExtractChangedBy:
    """Test suite for extract_changed_by function."""

    def test_valid_audit_event(self) -> None:
        """Test extraction of valid audit event."""
        document = {
            "name": "Test",
            "lastUpdatedBy": {
                "display": "Test User",
                "type": "user",
                "value": "user-123",
            },
        }

        changed_by = extract_changed_by(document)

        assert changed_by["display"] == "Test User"
        assert changed_by["type"] == "user"
        assert changed_by["value"] == "user-123"

    def test_missing_last_updated_by(self) -> None:
        """Test default values when lastUpdatedBy is missing."""
        document = {"name": "Test"}

        changed_by = extract_changed_by(document)

        assert changed_by["display"] == "Unknown"
        assert changed_by["type"] == "system"
        assert changed_by["value"] == "unknown"

    def test_malformed_audit_event(self) -> None:
        """Test handling of malformed audit event."""
        document = {"name": "Test", "lastUpdatedBy": "invalid"}

        changed_by = extract_changed_by(document)

        assert changed_by["display"] == "Unknown"
        assert changed_by["type"] == "system"
        assert changed_by["value"] == "unknown"

    def test_partial_audit_event(self) -> None:
        """Test handling when audit event has missing fields."""
        document = {"name": "Test", "lastUpdatedBy": {"display": "Test User"}}

        changed_by = extract_changed_by(document)

        assert changed_by["display"] == "Test User"
        assert changed_by["type"] == "system"
        assert changed_by["value"] == "unknown"

    def test_none_document(self) -> None:
        """Test handling of None document."""
        changed_by = extract_changed_by(None)

        assert changed_by["display"] == "Unknown"
        assert changed_by["type"] == "system"
        assert changed_by["value"] == "unknown"

    def test_empty_document(self) -> None:
        """Test handling of empty document."""
        changed_by = extract_changed_by({})

        assert changed_by["display"] == "Unknown"
        assert changed_by["type"] == "system"
        assert changed_by["value"] == "unknown"
