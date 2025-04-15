import json
import logging
import os

import boto3
import psycopg2
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_xray_sdk.core import patch_all

# X-Ray patching
patch_all()

# Environment variable
NAMESPACE = os.environ["NAMESPACE"]
SECRET_NAMES = os.environ["DB_SECRET_NAME"].split(",")
REGION_NAME = os.environ.get("AWS_REGION", "eu-west-2")

# Powertools setup
logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace=NAMESPACE)


@tracer.capture_method
def get_db_credentials() -> json:
    client = boto3.client("secretsmanager", region_name=REGION_NAME)
    secret_value = client.get_secret_value(SecretId=SECRET_NAMES)
    return json.loads(secret_value["SecretString"])


@tracer.capture_method
def test_db_connection(secret: json) -> None:
    conn = psycopg2.connect(
        host=secret["host"],
        port=secret["port"],
        user=secret["username"],
        password=secret["password"],
        dbname=secret["dbname"],
    )
    conn.close()  # If no exception, connection worked


@tracer.capture_lambda_handler
@logger.inject_lambda_context
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info("Retrieving DB credentials")
        secret = get_db_credentials()

        logger.info("Testing DB connection")
        test_db_connection(secret)

        metrics.add_metric(name="ConnectionSuccess", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Database connection successful"}),
        }

    except Exception as e:
        logging.exception("Connection failed")
        metrics.add_metric(name="ConnectionFailure", unit=MetricUnit.Count, value=1)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
