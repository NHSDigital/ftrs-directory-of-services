from pytest_bdd import given, parsers, scenarios, then
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
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
import re
from datetime import datetime, timedelta
from playwright.sync_api import APIRequestContext, sync_playwright


# Load feature file
scenarios("./is_infra_features/etl_ods.feature")


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
        if (
            ext.get("url")
            != "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"
        ):
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


def get_ods_codes(
    request_context: APIRequestContext, last_change_date: str, limit: int = 10
) -> List[str]:
    """
    Fetch a list of valid ODS codes from the ODS API.
    Only codes matching ^[A-Za-z0-9]{5,12}$ are returned.
    """
    sync_url = f"{BASE_ODS_API_URL}/sync?LastChangeDate={last_change_date}"
    logger.info(f"Fetching ODS codes from URL: {sync_url}")

    response = make_api_request_with_retries(
        request_context=request_context, method="GET", url=sync_url
    )

    ods_codes = []
    pattern = re.compile(r"^[A-Za-z0-9]{5,12}$")
    for org in response.get("Organisations", []):
        org_link = org.get("OrgLink", "")
        ods_code = org_link.rstrip("/").split("/")[-1]
        if pattern.match(ods_code):
            ods_codes.append(ods_code)
            logger.debug(f"Accepted ODS code: {ods_code}")
        else:
            logger.warning(f"Rejected invalid ODS code: {ods_code}")
        if len(ods_codes) >= limit:
            logger.debug(f"Reached ODS code fetch limit: {limit}")
            break
    if not ods_codes:
        logger.error("No valid ODS codes found matching regex ^[A-Za-z0-9]{5,12}$")
    else:
        logger.info(f"Fetched valid ODS codes: {ods_codes}")
    return ods_codes


def get_ods_details(
    request_context: APIRequestContext, ods_codes: List[str]
) -> List[Dict[str, Optional[str]]]:
    """
    Fetch detailed organisation info for each ODS code.
    """
    logger.info(f"Fetching organisation details for ODS codes: {ods_codes}")
    details = []
    for code in ods_codes:
        org_url = f"{BASE_ODS_FHIR_API_URL}/Organization/{code}"
        logger.debug(f"Fetching organisation data for ODS code: {code}")

        org_response = make_api_request_with_retries(
            request_context=request_context, method="GET", url=org_url
        )

        primary_role_display = extract_primary_role_display(org_response)
        status = org_response.get("active")
        name = org_response.get("name")

        phone = next(
            (
                tel.get("value")
                for tel in org_response.get("telecom", [])
                if tel.get("system") == "phone"
            ),
            None,
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
    assert getattr(item, "identifier_ODS_ODSCode", None) == expected_org["ods_code"], (
        "ODS code mismatch"
    )
    assert getattr(item, "name", None) == expected_org["name"], (
        f"Name mismatch: {item.name} != {expected_org['name']}"
    )
    assert getattr(item, "type", None) == expected_org["type"], (
        f"Type mismatch: {item.type} != {expected_org['type']}"
    )
    assert getattr(item, "active", None) == expected_org["active"], (
        f"Active status mismatch: {item.active} != {expected_org['active']}"
    )
    assert getattr(item, "phone", None) == expected_org["phone"], (
        f"Phone mismatch: {item.phone} != {expected_org['phone']}"
    )
    assert getattr(item, "modifiedBy", None) == "ODS_ETL_PIPELINE"
    logger.info(
        f"Organisation data matches expected details for ODS code '{expected_org['ods_code']}'."
    )


def verify_organisation_in_repo(
    model_repo: AttributeLevelRepository, ods_codes: list, organisation_details: list
):
    """
    Verify that DynamoDB records for the given ODS codes match expected organisation details.
    """
    if not ods_codes:
        raise ValueError("No ODS codes provided for verification")
    if isinstance(ods_codes, str):
        ods_codes = [ods_codes]
    for ods_code in ods_codes:
        logger.info(
            f"Validating organisation data for ODS code '{ods_code}' in repository"
        )
        item = get_from_repo(model_repo, ods_code)
        if item is None:
            raise AssertionError(
                f"No record found in repository for ODS code '{ods_code}'"
            )
        try:
            item_to_log = vars(item) if not isinstance(item, dict) else item
        except Exception:
            item_to_log = item
        logger.info(
            f"Retrieved DynamoDB item for ODS code '{ods_code}':\n{pprint.pformat(item_to_log)}"
        )
        expected_org = next(
            (org for org in organisation_details if org["ods_code"] == ods_code), None
        )
        assert expected_org is not None, (
            f"No organisation details found for ODS code {ods_code}"
        )
        assert_org_details_match(item, expected_org)


def validate_lambda_logs_for_ods_codes(
    context: Context, cloudwatch_logs, ods_codes: list
):
    """Verify that the Lambda processed and published messages to SQS for each ODS code."""
    time.sleep(30)  # Wait for logs to propagate

    for ods_code in ods_codes:
        logger.info(f"Validating Lambda logs for ODS code '{ods_code}'")

        all_logs = cloudwatch_logs.get_lambda_logs(context.lambda_name)

        if not all_logs:
            logger.error(f"No logs found at all for Lambda {context.lambda_name}!")
            logger.info(f"Lambda invocation time: {context.lambda_invocation_time}")
        else:
            logger.info(f"Found {len(all_logs)} total logs for Lambda")
            if all_logs:
                logger.info(f"Sample log: {all_logs[0].get('message', '')}")

        extraction_pattern = f'"Fetching organisation data for code: {ods_code}."'
        transformation_pattern = (
            f'"Successfully transformed data for ods_code: {ods_code}"'
        )
        publishing_pattern = "Succeeded to send"

        extraction_found = cloudwatch_logs.find_log_message(
            context.lambda_name, extraction_pattern
        )

        transformation_found = cloudwatch_logs.find_log_message(
            context.lambda_name, transformation_pattern
        )

        publishing_found = cloudwatch_logs.find_log_message(
            context.lambda_name, publishing_pattern
        )

        assert extraction_found, f"Extraction log not found for ODS code {ods_code}"
        assert transformation_found, (
            f"Transformation log not found for ODS code {ods_code}"
        )
        assert publishing_found, f"Publishing log not found for ODS code {ods_code}"

        logger.info(f"All logs validated successfully for ODS code '{ods_code}'")


@pytest.fixture(scope="session")
def shared_ods_data() -> Dict[str, List[Dict[str, Optional[str]]]]:
    logger.info("Building shared ODS data for session.")
    today = datetime.utcnow().date()
    ods_codes, organisation_details, chosen_date = None, None, None

    with sync_playwright() as p:
        request_context = p.request.new_context()

        for days_back in range(1, 8):
            candidate = today - timedelta(days=days_back)
            date_str = candidate.strftime("%Y-%m-%d")
            logger.info(f"Trying ODS extraction date: {date_str}")

            ods_codes = get_ods_codes(request_context, date_str)
            if ods_codes:
                organisation_details = get_ods_details(request_context, ods_codes)
                chosen_date = date_str
                break

    if not ods_codes:
        pytest.fail("No valid ODS codes found in the last 7 days.")

    logger.info(f"Shared ODS data prepared with codes: {ods_codes}")
    logger.info(f"Organisation details:\n{pprint.pformat(organisation_details)}")

    return {
        "ods_codes": ods_codes,
        "organisation_details": organisation_details,
        "date": chosen_date,
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
    logger.info(
        f"[SCENARIO] Organisation details:\n{pprint.pformat(ctx.organisation_details)}"
    )
    return ctx


@given(
    "extract ODS organisation records modified since yesterday",
    target_fixture="context",
)
def extract_ods_codes(context):
    logger.info(f"[STEP] Extracted ODS Codes: {context.ods_codes}")
    return context


@given(
    "extract detailed organisation information for those ODS codes",
    target_fixture="context",
)
def load_organisation_info(context):
    logger.info(
        f"[STEP] Loaded organisation details:\n{pprint.pformat(context.organisation_details)}"
    )
    return context


@when("I invoke the lambda with the valid date")
def lambda_process(context: Context, project, workspace, env, aws_lambda_client):
    """
    Trigger lambda processing with date and validate response.
    """
    extraction_date = context.extraction_date
    logger.info(f"[STEP] Triggering lambda with extraction date: {extraction_date}")
    lambda_name = get_resource_name(
        project, workspace, env, "etl-ods-processor", "lambda"
    )
    logger.info(f"[STEP] lambda name: {lambda_name}")
    lambda_exists = aws_lambda_client.check_function_exists(lambda_name)
    assert lambda_exists, f"Lambda function {lambda_name} does not exist"
    lambda_params = create_lambda_params(extraction_date)
    lambda_payload = aws_lambda_client.invoke_function(lambda_name, lambda_params)
    from datetime import timezone

    context.lambda_invocation_time = int(datetime.now(timezone.utc).timestamp())
    context.lambda_name = lambda_name
    # Validate the lambda response: check status code in payload
    status_code = lambda_payload.get("statusCode")
    assert status_code == 200


@then(
    parsers.parse(
        'the Lambda extracts, transforms, and publishes the transformed message to SQS for "{ods_type}" ODS codes'
    )
)
def verify_lambda_logs(context: Context, cloudwatch_logs, ods_type: str):
    """
    Validate Lambda logs for either a single ODS or all ODS codes.
    ods_type: "single" or "all"
    """
    if not context.ods_codes:
        raise ValueError("No ODS codes in context to validate")
    if ods_type.lower() == "single":
        ods_codes = [context.ods_codes[0]]
    elif ods_type.lower() == "all":
        ods_codes = context.ods_codes
    else:
        raise ValueError(f"Invalid ods_type '{ods_type}'. Use 'single' or 'all'.")
    validate_lambda_logs_for_ods_codes(context, cloudwatch_logs, ods_codes)


@then(
    parsers.parse(
        'the organisation data should be updated in DynamoDB for "{ods_type}" ODS codes'
    )
)
def verify_dynamodb_records(
    context: Context, model_repo: AttributeLevelRepository, ods_type: str
):
    """
    Validate DynamoDB records for either a single ODS or all ODS codes.
    """
    if not context.ods_codes:
        raise ValueError("No ODS codes in context to validate")
    if ods_type.lower() == "single":
        ods_codes = [context.ods_codes[0]]
    elif ods_type.lower() == "all":
        ods_codes = context.ods_codes
    else:
        raise ValueError(f"Invalid ods_type '{ods_type}'. Use 'single' or 'all'.")
    verify_organisation_in_repo(model_repo, ods_codes, context.organisation_details)


def create_lambda_params(date: str) -> dict:
    """
    Create the parameter dictionary for Lambda invocation.

    Args:
        date (str): The extraction date string.

    Returns:
        dict: Lambda input parameters.
    """
    return {"date": date}
