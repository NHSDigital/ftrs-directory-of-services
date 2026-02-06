"""Local ETL ODS test steps using testcontainers.

This module provides BDD step definitions for running ETL ODS tests locally
using LocalStack and mock servers, without requiring AWS deployment.
"""

import uuid

import pytest
from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.common.context import Context
from utilities.local.etl_ods_invoker import ETLOdsPipelineInvoker
from utilities.testcontainers.fixtures import is_local_test_mode

# Load feature file - tests will skip at runtime if not in local mode
scenarios("etl_ods_features/etl_ods_local.feature")


@pytest.fixture
def etl_ods_context() -> Context:
    """Create a fresh context for ETL ODS local tests."""
    return Context()


@given("the ETL ODS local test environment is configured")
def configure_local_environment(
    etl_ods_context: Context,
    etl_ods_test_environment: dict,
    etl_ods_pipeline_invoker: ETLOdsPipelineInvoker,
):
    """Configure the local test environment for ETL ODS tests.

    Args:
        etl_ods_context: Test context
        etl_ods_test_environment: Environment configuration fixture
        etl_ods_pipeline_invoker: Pipeline invoker fixture
    """
    if not is_local_test_mode():
        pytest.skip("Local tests require USE_LOCALSTACK=true")

    etl_ods_context.other["environment"] = etl_ods_test_environment
    etl_ods_context.other["pipeline_invoker"] = etl_ods_pipeline_invoker

    logger.info(
        f"Local ETL ODS environment configured: {etl_ods_test_environment.get('endpoint_url')}"
    )


@given(parsers.parse("I have the ODS mock server running"))
def ods_mock_running(
    etl_ods_context: Context,
    local_ods_mock_server: dict,
):
    """Verify the ODS mock server is running.

    Args:
        etl_ods_context: Test context
        local_ods_mock_server: ODS mock server fixture
    """
    if not is_local_test_mode():
        pytest.skip("Local tests require USE_LOCALSTACK=true")

    if local_ods_mock_server.get("mode") == "error":
        pytest.fail(
            f"ODS mock server failed to start: {local_ods_mock_server.get('error')}"
        )

    etl_ods_context.other["ods_mock_url"] = local_ods_mock_server.get("ods_api_url")
    logger.info(f"ODS mock server running at: {local_ods_mock_server.get('base_url')}")


@when(parsers.parse('I run the ETL ODS extractor for date "{date}"'))
def run_extractor(
    etl_ods_context: Context,
    date: str,
):
    """Run the ETL ODS extractor for a specific date.

    Args:
        etl_ods_context: Test context
        date: Date to process (YYYY-MM-DD format)
    """
    pipeline_invoker: ETLOdsPipelineInvoker = etl_ods_context.other.get(
        "pipeline_invoker"
    )
    if not pipeline_invoker:
        pytest.fail("Pipeline invoker not configured")

    etl_ods_context.correlation_id = str(uuid.uuid4())
    etl_ods_context.other["extraction_date"] = date

    logger.info(
        f"Running extractor for date: {date}, correlation_id: {etl_ods_context.correlation_id}"
    )

    result = pipeline_invoker.run_extractor_only(
        date=date,
        correlation_id=etl_ods_context.correlation_id,
    )

    etl_ods_context.lambda_response = result
    logger.info(f"Extractor result: {result}")


@when(parsers.parse('I run the full ETL ODS pipeline for date "{date}"'))
def run_full_pipeline(
    etl_ods_context: Context,
    date: str,
):
    """Run the complete ETL ODS pipeline for a specific date.

    Args:
        etl_ods_context: Test context
        date: Date to process (YYYY-MM-DD format)
    """
    pipeline_invoker: ETLOdsPipelineInvoker = etl_ods_context.other.get(
        "pipeline_invoker"
    )
    if not pipeline_invoker:
        pytest.fail("Pipeline invoker not configured")

    etl_ods_context.correlation_id = str(uuid.uuid4())
    etl_ods_context.other["extraction_date"] = date

    logger.info(
        f"Running full pipeline for date: {date}, correlation_id: {etl_ods_context.correlation_id}"
    )

    result = pipeline_invoker.run_full_pipeline(
        date=date,
        correlation_id=etl_ods_context.correlation_id,
    )

    etl_ods_context.other["pipeline_result"] = result
    etl_ods_context.lambda_response = result.extractor_result
    logger.info(
        f"Pipeline result: messages_processed={result.messages_processed}, errors={result.errors}"
    )


@when("I run the ETL ODS extractor for happy path scenario")
def run_extractor_happy_path(
    etl_ods_context: Context,
    ods_happy_path_scenario: str,
):
    """Run the extractor with the happy path scenario date.

    Args:
        etl_ods_context: Test context
        ods_happy_path_scenario: Date for happy path scenario
    """
    pipeline_invoker: ETLOdsPipelineInvoker = etl_ods_context.other.get(
        "pipeline_invoker"
    )
    if not pipeline_invoker:
        pytest.fail("Pipeline invoker not configured")

    etl_ods_context.correlation_id = str(uuid.uuid4())
    etl_ods_context.other["extraction_date"] = ods_happy_path_scenario

    result = pipeline_invoker.run_extractor_only(
        date=ods_happy_path_scenario,
        correlation_id=etl_ods_context.correlation_id,
    )

    etl_ods_context.lambda_response = result


@when("I run the ETL ODS extractor for empty payload scenario")
def run_extractor_empty_payload(
    etl_ods_context: Context,
    ods_empty_payload_scenario: str,
):
    """Run the extractor with the empty payload scenario date.

    Args:
        etl_ods_context: Test context
        ods_empty_payload_scenario: Date for empty payload scenario
    """
    pipeline_invoker: ETLOdsPipelineInvoker = etl_ods_context.other.get(
        "pipeline_invoker"
    )
    if not pipeline_invoker:
        pytest.fail("Pipeline invoker not configured")

    etl_ods_context.correlation_id = str(uuid.uuid4())
    etl_ods_context.other["extraction_date"] = ods_empty_payload_scenario

    result = pipeline_invoker.run_extractor_only(
        date=ods_empty_payload_scenario,
        correlation_id=etl_ods_context.correlation_id,
    )

    etl_ods_context.lambda_response = result


@then(parsers.parse("the extractor should return status code {status_code:d}"))
def verify_extractor_status(
    etl_ods_context: Context,
    status_code: int,
):
    """Verify the extractor returned the expected status code.

    Args:
        etl_ods_context: Test context
        status_code: Expected HTTP status code
    """
    actual_status = etl_ods_context.lambda_response.get("statusCode")
    assert actual_status == status_code, (
        f"Expected status code {status_code}, got {actual_status}. "
        f"Response: {etl_ods_context.lambda_response}"
    )


@then("the extractor should successfully process organizations")
def verify_extractor_success(etl_ods_context: Context):
    """Verify the extractor processed organizations successfully.

    Args:
        etl_ods_context: Test context
    """
    response = etl_ods_context.lambda_response
    assert response.get("statusCode") == 200, f"Expected 200, got: {response}"
    assert "Successfully processed" in response.get("message", ""), (
        f"Expected success message, got: {response}"
    )


@then("the pipeline should complete without errors")
def verify_pipeline_success(etl_ods_context: Context):
    """Verify the full pipeline completed without errors.

    Args:
        etl_ods_context: Test context
    """
    pipeline_result = etl_ods_context.other.get("pipeline_result")
    if not pipeline_result:
        pytest.fail("No pipeline result available")

    assert len(pipeline_result.errors) == 0, (
        f"Pipeline had errors: {pipeline_result.errors}"
    )
    logger.info(
        f"Pipeline completed successfully: {pipeline_result.messages_processed} messages processed"
    )


@then(parsers.parse("the pipeline should process {count:d} organizations"))
def verify_messages_processed(
    etl_ods_context: Context,
    count: int,
):
    """Verify the pipeline processed the expected number of organizations.

    Args:
        etl_ods_context: Test context
        count: Expected number of organizations processed
    """
    pipeline_result = etl_ods_context.other.get("pipeline_result")
    if not pipeline_result:
        pytest.fail("No pipeline result available")

    assert pipeline_result.messages_processed == count, (
        f"Expected {count} messages, got {pipeline_result.messages_processed}"
    )


@then("the extractor should return an empty result")
def verify_empty_result(etl_ods_context: Context):
    """Verify the extractor returned with no organizations to process.

    Args:
        etl_ods_context: Test context
    """
    response = etl_ods_context.lambda_response
    # Empty result still returns 200 status
    assert response.get("statusCode") == 200, f"Expected 200, got: {response}"
