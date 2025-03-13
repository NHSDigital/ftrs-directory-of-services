from aws_lambda_powertools import Tracer
import json

tracer = Tracer()  # Sets service via POWERTOOLS_SERVICE_NAME env var

@tracer.capture_lambda_handler
def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello world')
    }
