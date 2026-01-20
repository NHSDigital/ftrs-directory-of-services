"""Exception classes for ETL ODS pipeline."""


class RateLimitError(Exception):
    """Exception for rate limit failures that should be retried."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        self.message = message
        super().__init__(self.message)


class PermanentProcessingError(Exception):
    """Exception for permanent failures that should be consumed immediately (no retry, no DLQ).

    Typically indicates expected business logic scenarios:
    - 404 Not Found (resource doesn't exist yet - expected in ETL)
    """

    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )


class UnrecoverableError(Exception):
    """Exception for unrecoverable failures that should go to DLQ immediately (no retry).

    Typically indicates bugs in our code or configuration issues:
    - 400 Bad Request (malformed payload we're sending)
    - 401 Unauthorized (authentication config issue)
    - 403 Forbidden (authorization config issue)
    - 405 Method Not Allowed (wrong HTTP method - code bug)
    - 406 Not Acceptable (content negotiation failure - code bug)
    - 422 Unprocessable Entity (data validation failure)
    - Malformed JSON in message body
    """

    def __init__(self, message_id: str, error_type: str, details: str) -> None:
        self.message_id = message_id
        self.error_type = error_type
        self.details = details
        super().__init__(
            f"Message id: {message_id}, Error Type: {error_type}, Details: {details}"
        )


class RetryableProcessingError(Exception):
    """Exception for retryable failures that should be retried (e.g., 408, 500, 502, 503, 504)."""

    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )
