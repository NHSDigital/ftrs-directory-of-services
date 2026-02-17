class PermanentProcessingError(Exception):
    """Exception for permanent failures that should be consumed immediately (no retry, no DLQ).

    Typically indicates expected business logic scenarios or unrecoverable errors:
    - 404 Not Found (resource doesn't exist yet - expected in ETL)
    - 400 Bad Request (malformed payload we're sending - code bug)
    - 401 Unauthorized (authentication config issue)
    - 403 Forbidden (authorization config issue)
    - 405 Method Not Allowed (wrong HTTP method - code bug)
    - 406 Not Acceptable (content negotiation failure - code bug)
    - 422 Unprocessable Entity (data validation failure)
    - Malformed JSON in message body
    """

    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )


class RetryableProcessingError(Exception):
    """Exception for retryable failures that should be retried with backoff.

    Includes:
    - HTTP errors: 408, 409, 410, 412, 429 (rate limit), 500, 502, 503, 504
    - Network timeouts
    - Rate limit exceptions
    """

    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )
