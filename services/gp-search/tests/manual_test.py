import json
import os

from gp_search_function import lambda_handler

if __name__ == "__main__":
    test_event = {
        "odsCode": os.environ.get("ODS_CODE"),
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
