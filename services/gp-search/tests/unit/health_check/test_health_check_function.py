from unittest.mock import Mock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

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
    with patch("health_check.health_check_function.get_config") as mock:
        mock.return_value = {
            "DYNAMODB_TABLE_NAME": "test-table",
        }
        yield mock


class TestHealthCheckFunction:
    def test_lambda_handler_dynamodb_client_error(
        self,
        lambda_event,
        lambda_context,
        mock_dynamodb,
        mock_config,
        mock_boto3_client,
    ):
        """
        Test the lambda_handler function when the DynamoDB client raises a ClientError.
        This is a negative test case to verify the behavior when the DynamoDB service is unavailable or returns an error.
        """
        # Simulate a ClientError from DynamoDB
        mock_dynamodb.describe_table.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Table not found",
                }
            },
            "DescribeTable",
        )

        # We expect the ClientError to be propagated
        with pytest.raises(ClientError):
            lambda_handler(lambda_event, lambda_context)

    def test_lambda_handler_table_active(
        self,
        lambda_event,
        lambda_context,
        mock_dynamodb,
        mock_config,
        mock_boto3_client,
    ):
        """
        Test that lambda_handler returns correct response when DynamoDB table is active.
        """
        mock_dynamodb.describe_table.return_value = {"Table": {"TableStatus": "ACTIVE"}}

        result = lambda_handler(lambda_event, lambda_context)

        assert result == {"tableActive": True}

    def test_lambda_handler_table_not_active(
        self,
        lambda_event,
        lambda_context,
        mock_dynamodb,
        mock_config,
        mock_boto3_client,
    ):
        """
        Test the lambda_handler function when the DynamoDB table is not in ACTIVE state.
        This is a negative test case to verify the behavior when the table exists but is not ready.
        """
        # Simulate a response where the table is in CREATING state
        mock_dynamodb.describe_table.return_value = {
            "Table": {"TableStatus": "CREATING"}
        }

        result = lambda_handler(lambda_event, lambda_context)

        # Verify that the function returns False for tableActive
        assert result == {"tableActive": False}
