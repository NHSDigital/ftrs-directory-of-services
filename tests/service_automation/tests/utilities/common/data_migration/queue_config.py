"""Queue configuration for data migration tests."""

# SQS Queue names for LocalStack testing
MIGRATION_QUEUE_NAME = "ftrs-dos-dev-data-migration-queue-ftrs-276"
DLQ_QUEUE_NAME = "ftrs-dos-dev-data-migration-dlq-ftrs-276"


def get_migration_queue_name() -> str:
    """Get the migration queue name for testing.

    Returns:
        str: Migration queue name
    """
    return MIGRATION_QUEUE_NAME


def get_dlq_queue_name() -> str:
    """Get the DLQ queue name for testing.

    Returns:
        str: DLQ queue name
    """
    return DLQ_QUEUE_NAME
