import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

from health_check.config import GpHealthCheckSettings


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    table_active = _is_table_active()

    return {"statusCode": 200 if table_active else 500}


def _is_table_active() -> bool:
    try:
        dynamodb = boto3.client("dynamodb")
        table_name = GpHealthCheckSettings().dynamodb_table_name

        response = dynamodb.describe_table(TableName=table_name)

        table_active = response.get("Table", {}).get("TableStatus", None) == "ACTIVE"

    except Exception:
        return False

    return table_active
