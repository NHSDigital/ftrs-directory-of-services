import json

from application.handler import lambda_handler

# add main for local running
if __name__ == "__main__":
    # Example event for local testing
    test_event = {
        "pathParameters": {"odsCode": "H82028"},
        "queryStringParameters": None,
        "body": None,
    }
    test_context = None  # Mock context if needed

    # Call the handler function
    response = lambda_handler(test_event, test_context)
    # pretty print the response as json
    print("Response: ", json.dumps(response, indent=4))

    # pretty print the response body as json if it exists
    if response.get("body"):
        try:
            body = json.loads(response["body"])
            print("Response body: ", json.dumps(body, indent=2))
        except json.JSONDecodeError:
            print("Response body is not valid JSON")
