from unittest.mock import MagicMock

from healthcare_service.app.handler_healthcare_service import handler


def test_handler_returns_200_for_valid_get_request():
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
