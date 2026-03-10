from unittest.mock import Mock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from src.common.logbase import DosSearchHealthLogBase
from src.health_check.handler import lambda_handler


@pytest.fixture
def lambda_event():
    return {
        "path": "/_status",
        "httpMethod": "GET",
    }


@pytest.fixture
def lambda_context():
    return Mock(spec=LambdaContext)


class TestHealthCheckLambdaHandler:
    @patch("src.health_check.handler.get_service_repository")
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

    @patch("src.health_check.handler.logger")
    @patch("src.health_check.handler.get_service_repository")
    def test_lambda_handler_when_get_repository_fails(
        self, mock_get_repository, mock_logger, lambda_event, lambda_context
    ):
        mock_get_repository.side_effect = Exception("Failed to get repository")

        result = lambda_handler(lambda_event, lambda_context)

        assert result["statusCode"] == 500
        mock_logger.log.assert_called_once_with(
            DosSearchHealthLogBase.DOS_SEARCH_HEALTH_001,
        )

    @patch("src.health_check.handler.get_service_repository")
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
