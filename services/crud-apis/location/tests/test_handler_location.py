from unittest.mock import MagicMock

from location.app.handler_location import handler


def test_handler_returns_response() -> None:
    mock_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": "GET",
            "requestId": "test-request-id",
            "apiId": "test-api-id",
        },
        "resource": "/",
    }
    mock_context = MagicMock()
    response = handler(mock_event, mock_context)

    assert "statusCode" in response
    assert "headers" in response
    assert "body" in response
