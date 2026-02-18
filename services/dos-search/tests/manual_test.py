import json
import os

from functions.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from functions.dos_search_ods_code_function import lambda_handler

if __name__ == "__main__":
    ods_code = os.environ.get("ODS_CODE")

    test_event = {
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}",
            "_revinclude": REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
        },
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "headers": {
            "Accept": "application/fhir+json",
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
            "Version": "1",
            "NHSD-Request-ID": "test-request-id",
            "NHSD-Correlation-ID": "test-correlation-id",
            "X-Correlation-ID": "test-x-correlation-id",
            "X-Request-ID": "test-x-request-id",
            "End-User-Role": "test-role",
            "Application-ID": "test-app-id",
            "Application-Name": "test-app-name",
            "Request-Start-Time": "2023-01-01T00:00:00Z",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "User-Agent": "test-user-agent",
            "Host": "test-host",
            "X-Amzn-Trace-Id": "test-trace-id",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
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
