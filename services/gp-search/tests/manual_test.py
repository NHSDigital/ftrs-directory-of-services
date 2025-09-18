import json
import os

from gp_search_function import lambda_handler

if __name__ == "__main__":
    ods_code = os.environ.get("ODS_CODE")

    test_event = {
        "path": "/org",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }

    # Create mock Lambda context for testing
    class TestContext:
        def __init__(self):
            self.function_name = "test-function"
            self.function_version = "test-version"
            self.invoked_function_arn = "test-arn"
            self.memory_limit_in_mb = 128
            self.aws_request_id = "test-request-id"
            self.log_group_name = "test-log-group"
            self.log_stream_name = "test-log-stream"

    context = TestContext()

    response = lambda_handler(test_event, context)

    print("Response: ", json.dumps(response, indent=4))
    print("Response body: ", json.dumps(json.loads(response["body"]), indent=4))
