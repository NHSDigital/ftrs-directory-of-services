import json

from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import fetch_or_set_correlation_id
from ftrs_common.utils.request_id import fetch_or_set_request_id


def extract_correlation_id_from_sqs_records(records: list[dict]) -> str | None:
    if not records:
        return None

    try:
        record = records[0]
        body = record.get("body", "")

        if isinstance(body, str):
            body_content = json.loads(body)
            return body_content.get("correlation_id")

        # Handle direct dict body (for testing or different message formats)
        return body.get("correlation_id") if isinstance(body, dict) else None
    except Exception:
        return None


def setup_request_context(
    correlation_id: str | None, context: any, logger: Logger
) -> None:
    correlation_id = fetch_or_set_correlation_id(correlation_id)
    request_id = fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=None,  # SQS events don't have headers
    )

    logger.append_keys(correlation_id=correlation_id, request_id=request_id)
