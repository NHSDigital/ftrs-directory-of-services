import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext

from utils.config import get_config


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    dynamodb = boto3.client("dynamodb")
    table_name = get_config().get("DYNAMODB_TABLE_NAME")

    response = dynamodb.describe_table(TableName=table_name)

    table_active = response.get("Table", {}).get("TableStatus", None) == "ACTIVE"

    return {"tableActive": table_active}
