from unittest.mock import Mock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from health_check.health_check_function import lambda_handler


@pytest.fixture
def lambda_event():
    return {}


@pytest.fixture
def lambda_context():
    return Mock(spec=LambdaContext)


@pytest.fixture
def mock_dynamodb():
    return Mock()


@pytest.fixture
def mock_boto3_client(mock_dynamodb):
    with patch("boto3.client", return_value=mock_dynamodb) as mock:
        yield mock


@pytest.fixture
def mock_config():
    with patch("health_check.health_check_function.GpHealthCheckSettings") as mock:
        mock.return_value.dynamodb_table_name = "test-table"
        yield mock


class TestHealthCheckFunction:
    def test_lambda_handler_returns_200_when_table_active(
        self,
        lambda_event,
        lambda_context,
        mock_boto3_client,
        mock_dynamodb,
        mock_config,
    ):
        mock_dynamodb.describe_table.return_value = {"Table": {"TableStatus": "ACTIVE"}}

        result = lambda_handler(lambda_event, lambda_context)

        assert result == {"statusCode": 200}
        mock_dynamodb.describe_table.assert_called_once_with(TableName="test-table")

    def test_lambda_handler_when_describe_table_fails(
        self, lambda_event, lambda_context, mock_boto3_client, mock_config
    ):
        mock_boto3_client.return_value.describe_table.side_effect = Exception(
            "Failed to describe table"
        )

        result = lambda_handler(lambda_event, lambda_context)

        assert result == {"statusCode": 500}

    def test_lambda_handler_when_table_inactive(
        self, lambda_event, lambda_context, mock_boto3_client, mock_config
    ):
        mock_boto3_client.return_value.describe_table.return_value = {
            "Table": {"TableStatus": "CREATING"}
        }

        result = lambda_handler(lambda_event, lambda_context)

        assert result == {"statusCode": 500}
