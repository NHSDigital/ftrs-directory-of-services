"""Tests for common/uuid_utils.py module."""

from uuid import UUID

from common.uuid_utils import MIGRATION_UUID_NS, generate_uuid


def test_migration_uuid_namespace_is_valid() -> None:
    """Test that the migration UUID namespace is a valid UUID."""
    assert isinstance(MIGRATION_UUID_NS, UUID)
    assert str(MIGRATION_UUID_NS) == "fa3aaa15-9f83-4f4a-8f86-fd1315248bcb"


def test_generate_uuid_returns_uuid() -> None:
    """Test that generate_uuid returns a UUID instance."""
    result = generate_uuid(service_id=123, namespace="organisation")

    assert isinstance(result, UUID)


def test_generate_uuid_is_deterministic() -> None:
    """Test that generate_uuid produces the same UUID for the same inputs."""
    service_id = 123
    namespace = "organisation"

    uuid1 = generate_uuid(service_id=service_id, namespace=namespace)
    uuid2 = generate_uuid(service_id=service_id, namespace=namespace)

    assert uuid1 == uuid2, "UUIDs should be deterministic for same inputs"


def test_generate_uuid_different_service_ids() -> None:
    """Test that different service IDs produce different UUIDs."""
    namespace = "organisation"

    uuid1 = generate_uuid(service_id=1, namespace=namespace)
    uuid2 = generate_uuid(service_id=2, namespace=namespace)

    assert uuid1 != uuid2, "Different service IDs should produce different UUIDs"


def test_generate_uuid_different_namespaces() -> None:
    """Test that different namespaces produce different UUIDs."""
    service_id = 123

    uuid_org = generate_uuid(service_id=service_id, namespace="organisation")
    uuid_loc = generate_uuid(service_id=service_id, namespace="location")
    uuid_svc = generate_uuid(service_id=service_id, namespace="healthcare-service")

    assert uuid_org != uuid_loc, "Different namespaces should produce different UUIDs"
    assert uuid_org != uuid_svc, "Different namespaces should produce different UUIDs"
    assert uuid_loc != uuid_svc, "Different namespaces should produce different UUIDs"


def test_generate_uuid_with_large_service_id() -> None:
    """Test that large service IDs are handled correctly."""
    large_id = 999999999
    namespace = "organisation"

    uuid = generate_uuid(service_id=large_id, namespace=namespace)

    assert isinstance(uuid, UUID)


def test_generate_uuid_with_zero_service_id() -> None:
    """Test that zero service ID is handled correctly."""
    uuid = generate_uuid(service_id=0, namespace="organisation")

    assert isinstance(uuid, UUID)


def test_generate_uuid_with_negative_service_id() -> None:
    """Test that negative service IDs are handled (edge case)."""
    uuid = generate_uuid(service_id=-1, namespace="organisation")

    assert isinstance(uuid, UUID)


def test_generate_uuid_version() -> None:
    """Test that generated UUIDs are version 5 (namespaced)."""
    uuid = generate_uuid(service_id=123, namespace="organisation")

    # UUID version 5 should have version field set to 5
    assert uuid.version == 5


def test_generate_uuid_known_values() -> None:
    """Test specific known UUID values for regression testing."""
    # These known values ensure the UUID generation hasn't changed
    uuid1 = generate_uuid(service_id=1, namespace="organisation")
    uuid2 = generate_uuid(service_id=1, namespace="location")
    uuid3 = generate_uuid(service_id=1, namespace="healthcare-service")

    # Store expected UUIDs (generated once and kept as regression tests)
    assert str(uuid1) == "4539600c-e04e-5b35-a582-9fb36858d0e0"
    assert str(uuid2) == "6ef3317e-c6dc-5e27-b36d-577c375eb060"
    assert str(uuid3) == "8f724993-6964-5748-b0e5-609dc75b9381"


def test_generate_uuid_collision_resistance() -> None:
    """Test that many different inputs produce unique UUIDs."""
    uuids = set()
    namespaces = ["organisation", "location", "healthcare-service"]

    for service_id in range(100):
        for namespace in namespaces:
            uuid = generate_uuid(service_id=service_id, namespace=namespace)
            uuids.add(uuid)

    # Should have 300 unique UUIDs
    assert len(uuids) == 300, "All UUIDs should be unique"


def test_generate_uuid_with_special_characters_in_namespace() -> None:
    """Test UUID generation with special characters in namespace."""
    service_id = 123
    namespace_with_special = "test-namespace_123"

    uuid = generate_uuid(service_id=service_id, namespace=namespace_with_special)

    assert isinstance(uuid, UUID)
