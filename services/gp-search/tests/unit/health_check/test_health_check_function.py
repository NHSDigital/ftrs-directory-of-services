from unittest.mock import Mock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from health_check.health_check_function import lambda_handler


@pytest.fixture
def lambda_event():
    return {
        "version": "2.0",
        "rawPath": "/_status",
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
            "stage": "$default",
            "http": {
                "method": "GET",
            },
        },
        "body": None,
    }


@pytest.fixture
def lambda_context():
    return Mock(spec=LambdaContext)


class TestHealthCheckFunction:
    @patch("health_check.health_check_function.get_service_repository")
    def test_lambda_handler_returns_200_when_table_active(
        self, mock_get_repository, lambda_event, lambda_context
    ):
        mock_table = Mock()
        mock_table.table_status = "ACTIVE"
        mock_repository = Mock()
        mock_repository.table = mock_table
        mock_get_repository.return_value = mock_repository

        result = lambda_handler(lambda_event, lambda_context)

        assert result["statusCode"] == 200

    @patch("health_check.health_check_function.get_service_repository")
    def test_lambda_handler_when_get_repository_fails(
        self, mock_get_repository, lambda_event, lambda_context
    ):
        mock_get_repository.side_effect = Exception("Failed to get repository")

        result = lambda_handler(lambda_event, lambda_context)

        assert result["statusCode"] == 500

    @patch("health_check.health_check_function.get_service_repository")
    def test_lambda_handler_when_table_inactive(
        self, mock_get_repository, lambda_event, lambda_context
    ):
        mock_table = Mock()
        mock_table.table_status = "CREATING"
        mock_repository = Mock()
        mock_repository.table = mock_table
        mock_get_repository.return_value = mock_repository

        result = lambda_handler(lambda_event, lambda_context)

        assert result["statusCode"] == 500
