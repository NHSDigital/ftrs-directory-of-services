from unittest.mock import MagicMock


def test_lambda_handler_execution() -> None:
    from organisations.app.handler_organisation import handler

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
