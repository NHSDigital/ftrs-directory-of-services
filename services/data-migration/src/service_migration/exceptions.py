from service_migration.validation.types import ValidationIssue


class ServiceMigrationException(Exception):
    """Base exception for service migration errors."""

    def __init__(self, message: str, should_requeue: bool = True) -> None:
        super().__init__(message)
        self.should_requeue = should_requeue


class ServiceNotSupportedException(ServiceMigrationException):
    """Exception raised when a service is not supported for migration."""

    def __init__(self, message: str = "Service not supported for migration") -> None:
        super().__init__(message, should_requeue=False)


class ServiceSkippedException(ServiceMigrationException):
    """Exception raised when a service is skipped during migration."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            f"Service skipped during migration: {reason}",
            should_requeue=False,
        )


class FatalValidationException(ServiceMigrationException):
    """Exception raised for fatal validation errors."""

    def __init__(self, service_id: int, issues: list[ValidationIssue]) -> None:
        super().__init__(
            f"Fatal validation error for service {service_id}",
            should_requeue=False,
        )
        self.service_id = service_id
        self.issues = issues
