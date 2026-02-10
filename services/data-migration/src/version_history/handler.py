"""Lambda handler for version history tracking."""

import os
import uuid
from datetime import datetime
from typing import Any, Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_data_layer.client import get_dynamodb_resource

LOGGER = Logger.get(service="version-history")

# Initialize DynamoDB resource
version_history_table_name = os.environ.get("VERSION_HISTORY_TABLE_NAME", "")


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for writing test data to version history table.

    Args:
        event: DynamoDB stream event with Records array
        context: Lambda context

    Returns:
        Response with batchItemFailures for partial failure handling
    """
    LOGGER.info("Version history lambda invoked - writing test data")

    if not version_history_table_name:
        LOGGER.error("VERSION_HISTORY_TABLE_NAME environment variable not set")
        return {"batchItemFailures": []}

    try:
        # Get DynamoDB resource
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(version_history_table_name)

        # Create test data
        test_item = {
            "entity_id": f"test-table|{uuid.uuid4()}|test-field",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "change_type": "TEST",
            "changed_fields": {"test_field": {"old": "old_value", "new": "new_value"}},
            "changed_by": {
                "display": "Test Lambda",
                "type": "system",
                "value": "version-history-lambda",
            },
        }

        # Write to version history table
        table.put_item(Item=test_item)
        LOGGER.info(f"Test data written successfully: {test_item['entity_id']}")

    except Exception as e:
        LOGGER.error(f"Failed to write test data: {str(e)}", exc_info=True)
        return {"batchItemFailures": []}
