import json
from typing import Any, Dict, Optional

from ftrs_common.utils.correlation_id import current_correlation_id
from ftrs_common.utils.request_id import current_request_id


def create_message_payload(
    path: str,
    body: Dict[str, Any],
    correlation_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> str:
    """
    Create a standardized message payload for ETL pipeline communication.

    Args:
        path: The resource path/identifier
        body: The message body content
        correlation_id: Optional correlation ID (will use current if not provided)
        request_id: Optional request ID (will use current if not provided)

    Returns:
        JSON string of the formatted message
    """
    if correlation_id is None:
        correlation_id = current_correlation_id.get()

    if request_id is None:
        request_id = current_request_id.get()

    return json.dumps(
        {
            "path": path,
            "body": body,
            "correlation_id": correlation_id,
            "request_id": request_id,
        }
    )
