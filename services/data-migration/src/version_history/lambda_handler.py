"""Lambda handler for version history tracking."""

import os
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger

from version_history.stream_processor import process_stream_records

LOGGER = Logger.get(service="version-history")


@LOGGER.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for processing DynamoDB stream events.

    Processes change events from Organisation, Location, and HealthcareService
    tables, detects field differences, and writes version history records.

    Args:
        event: DynamoDB stream event with Records array
        context: Lambda context

    Returns:
        Response with batchItemFailures for partial failure handling
    """
    endpoint_url = os.getenv("ENDPOINT_URL")

    try:
        records = event.get("Records", [])
        LOGGER.log("VH_LAMBDA_001", record_count=len(records))

        if not records:
            LOGGER.log("VH_LAMBDA_002")
            return {"batchItemFailures": []}

        # Process stream records and get failed sequence numbers
        failed_sequence_numbers = process_stream_records(records, endpoint_url)

        # Build batch item failures response
        batch_item_failures = [
            {"itemIdentifier": seq_num} for seq_num in failed_sequence_numbers
        ]

        if batch_item_failures:
            LOGGER.log("VH_LAMBDA_003", failure_count=len(batch_item_failures))
        else:
            LOGGER.log("VH_LAMBDA_004", success_count=len(records))

        return {"batchItemFailures": batch_item_failures}

    except Exception as e:
        LOGGER.error(
            f"Critical error in version history lambda handler: {e}",
            exc_info=True,
        )
        # Return empty failures to avoid Lambda retry storm on systemic issues
        return {"batchItemFailures": []}
