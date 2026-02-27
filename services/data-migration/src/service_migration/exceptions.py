class ServiceMigrationException(Exception):
    """Base exception for service migration errors."""

    def __init__(self, message: str, requeue: bool = True) -> None:
        super().__init__(message)
        self.requeue = requeue


class ParentPharmacyNotFoundError(ServiceMigrationException):
    """Raised when no parent pharmacy record exists for a linked pharmacy service."""

    def __init__(self, record_id: int, ods_code: str) -> None:
        super().__init__(
            f"No parent pharmacy record found for service {record_id} with base ODS code {ods_code}",
            requeue=False,
        )
        self.record_id = record_id
        self.ods_code = ods_code
