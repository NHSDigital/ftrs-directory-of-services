import boto3
import pytest
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.infra.sqs_util import purge_queue

from .ods_data_utils import OdsDateSelector, extract_org_details


@pytest.fixture(scope="module")
def aws_lambda_client():
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    return LambdaWrapper(lambda_client, iam_resource)


@pytest.fixture
def cloudwatch_logs():
    """Create CloudWatch logs wrapper for log verification."""
    return CloudWatchLogsWrapper()


@pytest.fixture
def model_repo(project: str, workspace: str, env: str) -> AttributeLevelRepository:
    """Provide AttributeLevelRepository for testing."""
    table_name = get_resource_name(project, workspace, env, "organisation", "table")
    return AttributeLevelRepository(table_name=table_name, model_cls=Organisation)


@pytest.fixture(scope="module")
def shared_ods_data(api_request_context_ods_terminology):
    """Fetch and prepare ODS organization data for testing."""
    selector = OdsDateSelector(
        request_context=api_request_context_ods_terminology,
        lookback_days=7,
        min_codes=10,
    )
    chosen_date, org_resources = selector.find_valid_date()
    organisation_details = extract_org_details(org_resources)

    ods_codes = [org["ods_code"] for org in organisation_details]

    return {
        "ods_codes": ods_codes,
        "organisation_details": organisation_details,
        "date": chosen_date,
    }


@pytest.fixture(scope="module")
def cleanup_queues():
    """Module-scoped fixture to purge all queues once after all tests complete."""
    # Store queue configs that need cleanup (will be populated by context fixture)
    queue_configs_to_clean = {}

    yield queue_configs_to_clean  # Run all tests first

    # After all tests in module complete, purge queues
    if queue_configs_to_clean:
        for config in queue_configs_to_clean.values():
            purge_queue(config["queue_url"], timeout=60)
            purge_queue(config["dlq_url"], timeout=60)


@pytest.fixture
def context(shared_ods_data) -> Context:
    ctx = Context()
    ctx.ods_codes = shared_ods_data["ods_codes"]
    ctx.organisation_details = shared_ods_data["organisation_details"]
    ctx.extraction_date = shared_ods_data["date"]
    return ctx
