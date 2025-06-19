from unittest.mock import Mock

from aws_lambda_powertools.utilities.typing import LambdaContext

from health_check.health_check_function import lambda_handler


def test_health_check_returns_200():
    """Test that the health check function returns status code 200"""
    mock_context = Mock(spec=LambdaContext)

    result = lambda_handler({}, mock_context)

    assert result["statusCode"] == 200
