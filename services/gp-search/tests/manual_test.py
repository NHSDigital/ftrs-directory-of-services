import json
import logging

from ftrs_service import config
from gp_search_function import lambda_handler

logging.basicConfig(level=config.get_config().get("LOG_LEVEL"))
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    test_event = {
        "pathParameters": {"odsCode": "H82028"},
        "queryStringParameters": None,
        "body": None,
    }
    test_context = None

    response = lambda_handler(test_event, test_context)

    print("Response: ", json.dumps(response, indent=4))
    print("Response body: ", json.dumps(json.loads(response["body"]), indent=4))
