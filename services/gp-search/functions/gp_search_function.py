import logging
import os

import boto3
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_xray_sdk.core import patch_all, xray_recorder
from boto3.dynamodb.conditions import Key

# Patch all supported libraries for X-Ray (includes boto3, requests, etc.)
patch_all()

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("DYNAMODB_TABLE_NAME")
table = dynamodb.Table(table_name)


@xray_recorder.capture("lambda_handler")
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info("Received event: %s", event)

    xray_recorder.put_annotation("Operation", "QueryTable")
    xray_recorder.put_metadata("TableName", table_name)

    try:
        with xray_recorder.in_subsegment("DynamoDBScan"):
            response = table.query(
                IndexName = 'ods-code-index',
                KeyConditionExpression = Key('ods-code').eq('P83010')
            )

        logger.info("Fetched %d items from table %s.", len(response.get("Items", [])), table_name)
        return {
            "statusCode": 200,
            "body": response.get("Items", [])
        }
    except Exception as e:
        logging.exception("Failed to gather items from table")
        xray_recorder.put_annotation("Error", str(e))
        return {
            "statusCode": 500,
            "body": str(e)
        }
