from uuid import UUID, uuid5

MIGRATION_UUID_NS = UUID("fa3aaa15-9f83-4f4a-8f86-fd1315248bcb")


def generate_uuid(service_id: int, namespace: str) -> UUID:
    """
    Generate a namespaced UUID for the service using the service ID and namespace.
    """
    return uuid5(MIGRATION_UUID_NS, f"{namespace}-{service_id}")
