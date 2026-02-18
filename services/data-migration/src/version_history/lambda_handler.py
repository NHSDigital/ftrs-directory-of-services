"""Lambda handler for version history tracking."""

import os
from typing import Any, Dict, List

from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_resource

from version_history.stream_processor import process_stream_record

LOGGER = Logger.get(service="version-history")


@LOGGER.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for processing DynamoDB stream events and tracking version history.

    Args:
        event: DynamoDB stream event with Records array
        context: Lambda context

    Returns:
        Response with batchItemFailures for partial failure handling
    """
    records = event.get("Records", [])
    LOGGER.info(
        "Processing stream records",
        extra={"record_count": len(records)},
    )

    # Use ENDPOINT_URL from environment if set (for local testing)
    endpoint_url = os.getenv("ENDPOINT_URL")
    dynamodb = get_dynamodb_resource(endpoint_url=endpoint_url)
    # Get DynamoDB resource and version history table
    version_history_table_name = get_table_name("version-history")
    version_history_table = dynamodb.Table(version_history_table_name)

    batch_failures: List[Dict[str, str]] = []

    for record in records:
        try:
            process_stream_record(record, version_history_table)
        except Exception as e:
            # Log error and add to batch failures
            sequence_number = record.get("dynamodb", {}).get("SequenceNumber")
            LOGGER.error(
                "Failed to process record",
                exc_info=True,
                extra={"error": str(e), "sequence_number": sequence_number},
            )
            if sequence_number:
                batch_failures.append({"itemIdentifier": sequence_number})

    LOGGER.info(
        "Completed processing stream records",
        extra={
            "successful_count": len(records) - len(batch_failures),
            "total_count": len(records),
            "failed_count": len(batch_failures),
        },
    )

    return {"batchItemFailures": batch_failures}
