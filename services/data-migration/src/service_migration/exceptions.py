class ServiceMigrationException(Exception):
    """Base exception for service migration errors."""

    def __init__(self, message: str, requeue: bool = True) -> None:
        super().__init__(message)
        self.requeue = requeue
