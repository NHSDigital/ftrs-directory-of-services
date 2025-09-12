from pytest_bdd import given, parsers, scenarios, then
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from utilities.common.constants import BASE_ODS_API_URL, BASE_ODS_FHIR_API_URL
from utilities.common.context import Context
from utilities.infra.api_util import make_api_request_with_retries
from utilities.infra.lambda_util import *
from loguru import logger
import pytest
from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from utilities.common.resource_name import get_resource_name
import boto3
import pprint
import time


# Load feature file
scenarios("./is_infra_features/etl_ods.feature")
MAX_RETRIES = 10
RETRY_DELAY = 1

@pytest.fixture(scope="module")
def aws_lambda_client():
    """Fixture to initialize AWS Lambda utility"""
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    wrapper = LambdaWrapper(lambda_client, iam_resource)
    return wrapper


def extract_primary_role_display(org_response: dict) -> Optional[str]:
    """
    Extract the primary role display string from OrganizationRole extension.
    """
    logger.debug("Extracting primary role display from org response.")
    extensions = org_response.get("extension", [])
    for ext in extensions:
        if ext.get("url") != "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1":
            continue
        nested_exts = ext.get("extension", [])
        primary_role = any(
            ne.get("url") == "primaryRole" and ne.get("valueBoolean") is True
            for ne in nested_exts
        )
        if primary_role:
            for ne in nested_exts:
                if ne.get("url") == "role":
                    role_display = ne.get("valueCoding", {}).get("display")
                    logger.info(f"Primary role display found: {role_display}")
                    return role_display
    logger.warning("No primary role display found.")
    return None


def get_ods_codes(last_change_date: str, limit: int = 5) -> List[str]:
    """
    Fetch a list of ODS codes from the sync API.
    """
    sync_url = f"{BASE_ODS_API_URL}/sync?LastChangeDate={last_change_date}"
    logger.info(f"Fetching ODS codes from URL: {sync_url}")
    response = make_api_request_with_retries("GET", sync_url)

    ods_codes = []
    for org in response.get("Organisations", []):
        org_link = org.get("OrgLink", "")
        ods_code = org_link.rstrip("/").split("/")[-1]
        ods_codes.append(ods_code)
        if len(ods_codes) >= limit:
            logger.debug(f"Reached ODS code fetch limit: {limit}")
            break

    logger.info(f"Fetched ODS codes: {ods_codes}")
    return ods_codes


def get_ods_details(ods_codes: List[str]) -> List[Dict[str, Optional[str]]]:
    """
    Fetch detailed organisation info for each ODS code.
    """
    logger.info(f"Fetching organisation details for ODS codes: {ods_codes}")
    details = []
    for code in ods_codes:
        org_url = f"{BASE_ODS_FHIR_API_URL}/Organization/{code}"
        logger.debug(f"Fetching organisation data for ODS code: {code}")
        org_response = make_api_request_with_retries("GET", org_url)

        primary_role_display = extract_primary_role_display(org_response)
        status = org_response.get("active")
        name = org_response.get("name")

        phone = next(
            (tel.get("value") for tel in org_response.get("telecom", [])
            if tel.get("system") == "phone"),
            None
        )

        org_detail = {
            "ods_code": code,
            "type": primary_role_display,
            "active": status,
            "name": name,
            "phone": phone,
        }
        details.append(org_detail)

        logger.debug(f"Organisation detail fetched: {org_detail}")

    logger.info("Completed fetching organisation details.")
    logger.info(f"Organisation details:\n{pprint.pformat(details)}")
    return details


def assert_org_details_match(item: DBModel, expected_org: dict) -> None:
    """
    Compare the DynamoDB item with expected organisation details.

    Args:
        item (dict): The organisation data fetched from DynamoDB.
        expected_org (dict): The expected organisation details from context.

    Raises:
        AssertionError: If any field does not match.
    """
    assert item is not None, "No data found in repository"
    assert getattr(item, "identifier_ODS_ODSCode", None) == expected_org["ods_code"], "ODS code mismatch"
    assert getattr(item, "name", None) == expected_org["name"], f"Name mismatch: {item.name} != {expected_org['name']}"
    assert getattr(item, "type", None) == expected_org["type"], f"Type mismatch: {item.type} != {expected_org['type']}"
    assert getattr(item, "active", None) == expected_org["active"], f"Active status mismatch: {item.active} != {expected_org['active']}"
    assert getattr(item, "phone", None) == expected_org["phone"], f"Phone mismatch: {item.phone} != {expected_org['phone']}"
    assert getattr(item, "modifiedBy", None) == "ODS_ETL_PIPELINE"
    logger.info(f"Organisation data matches expected details for ODS code '{expected_org['ods_code']}'.")


@pytest.fixture(scope="session")
def shared_ods_data() -> Dict[str, List[Dict[str, Optional[str]]]]:
    """
    Fetch ODS codes and organisation details once per test session.
    """
    logger.info("Building shared ODS data for session.")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    ods_codes = get_ods_codes(yesterday)
    organisation_details = get_ods_details(ods_codes)
    logger.info(f"Shared ODS data prepared with codes: {ods_codes}")
    logger.info(f"Organisation details:\n{pprint.pformat(organisation_details)}")
    return {
        "ods_codes": ods_codes,
        "organisation_details": organisation_details,
        "date": yesterday
    }


@pytest.fixture
def context(shared_ods_data) -> Context:
    """
    Create a fresh Context object for each test function.
    """
    ctx = Context()
    ctx.ods_codes = shared_ods_data["ods_codes"]
    ctx.organisation_details = shared_ods_data["organisation_details"]
    ctx.extraction_date = shared_ods_data["date"]
    logger.info(f"[SCENARIO] Context created with ODS codes: {ctx.ods_codes}")
    logger.info(f"[SCENARIO] Organisation details:\n{pprint.pformat(ctx.organisation_details)}")
    return ctx


@given("extract ODS organisation records modified since yesterday", target_fixture="context")
def extract_ods_codes(context):
    logger.info(f"[STEP] Extracted ODS Codes: {context.ods_codes}")
    return context


@given("extract detailed organisation information for those ODS codes", target_fixture="context")
def load_organisation_info(context):
    logger.info(f"[STEP] Loaded organisation details:\n{pprint.pformat(context.organisation_details)}")
    return context


@when("I invoke the lambda with the valid date")
def lambda_process(context: Context, project, workspace, env , aws_lambda_client):
    """
    Trigger lambda processing with date and validate response.
    """
    extraction_date = context.extraction_date
    logger.info(f"[STEP] Triggering lambda with extraction date: {extraction_date}")
    lambda_name = get_resource_name(project, workspace, env, "etl-ods-processor", "lambda")
    logger.info(f"[STEP] lambda name: {lambda_name}")
    lambda_exists = aws_lambda_client.check_function_exists(lambda_name)
    assert lambda_exists, f"Lambda function {lambda_name} does not exist"
    lambda_params = create_lambda_params(extraction_date)
    lambda_payload = aws_lambda_client.invoke_function(lambda_name, lambda_params)
    context.lambda_name = lambda_name
    # Validate the lambda response: check status code in payload
    status_code = lambda_payload.get("statusCode")
    assert status_code == 200

@then(parsers.parse('the Lambda extracts, transforms, and publishes the transformed message to SQS'))
def verify_lambda_processes_and_publishes(context: Context, cloudwatch_logs):
    """
    Verify that the Lambda processed and published messages to SQS by checking logs.
    """
    # Wait a bit for logs to propagate to CloudWatch
    time.sleep(5)

    # Look for specific log patterns that indicate successful processing
    extraction_pattern = "Successfully extracted ODS organisation records"
    transformation_pattern = "Successfully transformed data"
    publishing_pattern = "Successfully published to SQS"

    # Check for each pattern in the logs
    extraction_found = cloudwatch_logs.find_log_message(
        context.lambda_name,
        extraction_pattern,
        context.lambda_invocation_time,
        30  # Check logs within 30 seconds of invocation
    )

    transformation_found = cloudwatch_logs.find_log_message(
        context.lambda_name,
        transformation_pattern,
        context.lambda_invocation_time,
        30
    )

    publishing_found = cloudwatch_logs.find_log_message(
        context.lambda_name,
        publishing_pattern,
        context.lambda_invocation_time,
        30
    )

    # Assert that all expected log messages were found
    assert extraction_found, f"Log message not found: {extraction_pattern}"
    assert transformation_found, f"Log message not found: {transformation_pattern}"
    assert publishing_found, f"Log message not found: {publishing_pattern}"


@then(parsers.parse('the organisation data should be updated in DynamoDB for the specified ODS codes'), target_fixture="context")
def check_organisation_in_repo(context: Context, model_repo: AttributeLevelRepository, project, workspace, env) -> Context:
    for ods_code in context.ods_codes:
        logger.info(f"Validating organisation data for ODS code '{ods_code}' in repository")
        item = get_from_repo(model_repo, ods_code)
        if item is None:
            raise AssertionError(f"No record found in repository for ODS code '{ods_code}'")
        # Log the complete retrieved DynamoDB item
        try:
            item_to_log = vars(item) if not isinstance(item, dict) else item
        except Exception:
            item_to_log = item
        logger.info(f"Retrieved DynamoDB item for ODS code '{ods_code}':\n{pprint.pformat(item_to_log)}")
        expected_org = next((org for org in context.organisation_details if org["ods_code"] == ods_code), None)
        assert expected_org is not None, f"No organisation details found in context for ODS code {ods_code}"
        assert_org_details_match(item, expected_org)
    return context

def create_lambda_params(date: str) -> dict:
    """
    Create the parameter dictionary for Lambda invocation.

    Args:
        date (str): The extraction date string.

    Returns:
        dict: Lambda input parameters.
    """
    return {"date": date}
