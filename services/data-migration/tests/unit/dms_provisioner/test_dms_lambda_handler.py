from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from sqlalchemy.exc import SQLAlchemyError

from dms_provisioner.lambda_handler import lambda_handler


@pytest.fixture
def mock_lambda_context() -> MagicMock:
    """Mock Lambda context with required attributes."""
    context = MagicMock()
    context.function_name = "test-function"
    context.memory_limit_in_mb = 128
    context.invoked_function_arn = (
        "arn:aws:lambda:eu-west-2:123456789012:function:test-function"
    )
    context.aws_request_id = "test-request-id"
    return context


@pytest.fixture
def mock_session() -> MagicMock:
    """Mock boto3 session."""
    with patch("boto3.session.Session") as mock:
        mock_instance = MagicMock()
        mock_instance.region_name = "eu-west-2"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_dms_config() -> MagicMock:
    """Mock DMS database configuration."""
    with patch("dms_provisioner.lambda_handler.DmsDatabaseConfig") as mock_class:
        mock_config = MagicMock()
        mock_config.get_target_rds_config.return_value = MagicMock()
        mock_config.get_dms_user_details.return_value = ("dms_user", "password123")
        mock_config.trigger_lambda_arn = (
            "arn:aws:lambda:eu-west-2:123456789012:function:migration-trigger"
        )
        mock_class.return_value = mock_config
        yield mock_config


@pytest.fixture
def mock_engine() -> MagicMock:
    """Mock SQLAlchemy engine."""
    with patch(
        "dms_provisioner.lambda_handler.get_sqlalchemy_engine_from_config"
    ) as mock_get_engine:
        mock_engine_obj = MagicMock()
        mock_get_engine.return_value = mock_engine_obj
        yield mock_engine_obj


@pytest.fixture
def mock_create_dms_user() -> MagicMock:
    """Mock create_dms_user function."""
    with patch("dms_provisioner.lambda_handler.create_dms_user") as mock:
        yield mock


@pytest.fixture
def mock_create_rds_triggers() -> MagicMock:
    """Mock create_rds_triggers function."""
    with patch("dms_provisioner.lambda_handler.create_rds_triggers") as mock:
        yield mock


@pytest.fixture
def setup_all_mocks(
    mock_session: MagicMock,
    mock_dms_config: MagicMock,
    mock_engine: MagicMock,
    mock_create_dms_user: MagicMock,
    mock_create_rds_triggers: MagicMock,
) -> dict[str, MagicMock]:
    """Set up all mocks together and return them in a dictionary."""
    yield {
        "session": mock_session,
        "dms_config": mock_dms_config,
        "engine": mock_engine,
        "create_dms_user": mock_create_dms_user,
        "create_rds_triggers": mock_create_rds_triggers,
    }


def test_lambda_handler_successfully_creates_user_and_triggers(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    """Test that the lambda handler successfully creates a DMS user and triggers."""
    event = {}

    lambda_handler(event, mock_lambda_context)

    mock_engine = setup_all_mocks["engine"]
    mock_dms_config = setup_all_mocks["dms_config"]
    mock_create_dms_user = setup_all_mocks["create_dms_user"]
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    mock_create_dms_user.assert_called_once_with(mock_engine, "dms_user", "password123")
    mock_create_rds_triggers.assert_called_once_with(
        mock_engine,
        lambda_arn=mock_dms_config.trigger_lambda_arn,
        aws_region="eu-west-2",
    )


def test_lambda_handler_handles_client_error_when_fetching_secrets(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    """Test that the lambda handler handles client errors when fetching secrets."""
    mock_dms_config = setup_all_mocks["dms_config"]
    mock_create_dms_user = setup_all_mocks["create_dms_user"]
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    event = {}
    mock_dms_config.get_target_rds_config.side_effect = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}},
        "GetSecretValue",
    )

    with pytest.raises(ClientError):
        lambda_handler(event, mock_lambda_context)

    mock_create_dms_user.assert_not_called()
    mock_create_rds_triggers.assert_not_called()


def test_lambda_handler_handles_exception_during_user_creation(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    """Test that the lambda handler handles exceptions during user creation."""
    mock_create_dms_user = setup_all_mocks["create_dms_user"]
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    event = {}
    mock_create_dms_user.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(SQLAlchemyError):
        lambda_handler(event, mock_lambda_context)

    mock_create_dms_user.assert_called_once()
    mock_create_rds_triggers.assert_not_called()


def test_lambda_handler_handles_exception_during_trigger_creation(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    """Test that the lambda handler handles exceptions during trigger creation."""
    mock_create_dms_user = setup_all_mocks["create_dms_user"]
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    event = {}
    mock_create_rds_triggers.side_effect = SQLAlchemyError("Trigger creation failed")

    with pytest.raises(SQLAlchemyError):
        lambda_handler(event, mock_lambda_context)

    mock_create_dms_user.assert_called_once()
    mock_create_rds_triggers.assert_called_once()


def test_lambda_handler_raises_exception_on_unexpected_error(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    """Test that the lambda handler raises exception on unexpected error."""
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    event = {}
    mock_create_rds_triggers.side_effect = Exception("Unexpected error")

    with pytest.raises(Exception):
        lambda_handler(event, mock_lambda_context)


def test_lambda_handler_works_with_various_event_inputs(
    setup_all_mocks: dict,
    mock_lambda_context: MagicMock,
) -> None:
    mock_create_dms_user = setup_all_mocks["create_dms_user"]
    mock_create_rds_triggers = setup_all_mocks["create_rds_triggers"]

    complex_event = {
        "source": "aws.events",
        "detail-type": "Scheduled Event",
        "resources": ["arn:aws:events:eu-west-2:123456789012:rule/hourly-trigger"],
        "detail": {},
    }

    lambda_handler(complex_event, mock_lambda_context)

    mock_create_dms_user.assert_called_once()
    mock_create_rds_triggers.assert_called_once()
