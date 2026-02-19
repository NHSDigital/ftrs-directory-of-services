"""Lambda handler for version history tracking."""

import os
from typing import Any, Dict, List

from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBStreamEvent,
)
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_table_name
from ftrs_data_layer.client import get_dynamodb_resource
from ftrs_data_layer.logbase import VersionHistoryLogBase

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
    stream_event = DynamoDBStreamEvent(event)
    records = list(stream_event.records)
    LOGGER.log(VersionHistoryLogBase.VH_HANDLER_001, record_count=len(records))

    # Use ENDPOINT_URL from environment if set (for local testing)
    endpoint_url = os.getenv("ENDPOINT_URL")
    dynamodb = get_dynamodb_resource(endpoint_url=endpoint_url)

    version_history_table_name = get_table_name("version-history")
    version_history_table = dynamodb.Table(version_history_table_name)

    batch_failures: List[Dict[str, str]] = []

    for record in records:
        try:
            process_stream_record(record, version_history_table)
        except Exception as e:
            sequence_number = record.dynamodb.sequence_number
            LOGGER.log(
                VersionHistoryLogBase.VH_HANDLER_002,
                sequence_number=sequence_number,
                error=str(e),
                exc_info=True,
            )
            if sequence_number:
                batch_failures.append({"itemIdentifier": sequence_number})

    LOGGER.log(
        VersionHistoryLogBase.VH_HANDLER_003,
        successful_count=len(records) - len(batch_failures),
        total_count=len(records),
        failed_count=len(batch_failures),
    )

    return {"batchItemFailures": batch_failures}
