from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from typing import Optional, List, Dict, Tuple
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
import time
import re
from datetime import datetime, timedelta, timezone
from playwright.sync_api import APIRequestContext

# Load feature file
scenarios(
    "./etl_ods_features/etl_ods_happy.feature",
    "./etl_ods_features/etl_ods_unhappy.feature",
)


class OdsDateSelector:
    """
    Selects a date with at least a minimum number of valid ODS codes.
    Looks back a configurable number of days.
    """

    def __init__(
        self,
        request_context: APIRequestContext,
        lookback_days: int = 7,
        min_codes: int = 10,
    ):
        self.request_context = request_context
        self.lookback_days = lookback_days
        self.min_codes = min_codes

    def find_valid_date(self) -> Tuple[str, List[str]]:
        today = datetime.utcnow().date()
        for days_back in range(1, self.lookback_days + 1):
            candidate = today - timedelta(days=days_back)
            date_str = candidate.strftime("%Y-%m-%d")
            logger.info(f"Trying ODS extraction date: {date_str}")

            ods_codes = get_ods_codes(self.request_context, date_str)
            if ods_codes and len(ods_codes) >= self.min_codes:
                ods_codes = ods_codes[: self.min_codes]
                logger.info(
                    f"Selected date {date_str} with {len(ods_codes)} valid ODS codes."
                )
                return date_str, ods_codes

        pytest.fail(
            f"No date found in last {self.lookback_days} days with at least {self.min_codes} valid ODS codes."
        )


def extract_primary_role_display(org_response: dict) -> Optional[str]:
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
                    return ne.get("valueCoding", {}).get("display")
    return None


def get_ods_codes(
    request_context: APIRequestContext, last_change_date: str, limit: int = 50
) -> List[str]:
    sync_url = f"{BASE_ODS_API_URL}/sync?LastChangeDate={last_change_date}"
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
        if len(ods_codes) >= limit:
            break
    return ods_codes


def get_ods_details(
    request_context: APIRequestContext, ods_codes: List[str]
) -> List[Dict[str, Optional[str]]]:
    details = []
    for code in ods_codes:
        org_url = f"{BASE_ODS_FHIR_API_URL}/Organization/{code}"
        org_response = make_api_request_with_retries(
            request_context=request_context, method="GET", url=org_url
        )
        details.append(
            {
                "ods_code": code,
                "type": extract_primary_role_display(org_response),
                "active": org_response.get("active"),
                "name": org_response.get("name"),
                "phone": next(
                    (
                        tel.get("value")
                        for tel in org_response.get("telecom", [])
                        if tel.get("system") == "phone"
                    ),
                    None,
                ),
            }
        )
    return details


def assert_org_details_match(item: DBModel, expected_org: dict) -> None:
    assert item is not None, "No data found in repository"
    assert getattr(item, "identifier_ODS_ODSCode", None) == expected_org["ods_code"]
    assert getattr(item, "name", None) == expected_org["name"]
    assert getattr(item, "type", None) == expected_org["type"]
    assert getattr(item, "active", None) == expected_org["active"]
    assert getattr(item, "telecom", None) == expected_org["phone"]
    assert getattr(item, "modifiedBy", None) == "ODS_ETL_PIPELINE"


def verify_organisation_in_repo(
    model_repo: AttributeLevelRepository, ods_codes: list, organisation_details: list
):
    if not ods_codes:
        raise ValueError("No ODS codes provided for verification")
    if isinstance(ods_codes, str):
        ods_codes = [ods_codes]

    retries, delay = 5, 15
    for attempt in range(1, retries + 1):
        try:
            for ods_code in ods_codes:
                item = get_from_repo(model_repo, ods_code)
                if item is None:
                    raise AssertionError(
                        f"No record found in repository for {ods_code}"
                    )

                expected_org = next(
                    org for org in organisation_details if org["ods_code"] == ods_code
                )
                assert_org_details_match(item, expected_org)
            return
        except AssertionError as e:
            if attempt < retries:
                logger.warning(f"Retry {attempt}/{retries} after failure: {e}")
                time.sleep(delay)
            else:
                raise


def validate_lambda_logs_for_ods_codes(
    context: Context, cloudwatch_logs, ods_codes: list
):
    time.sleep(30)  # Central wait_for_logs()
    for ods_code in ods_codes:
        extraction_pattern = f'"Fetching organisation data for code: {ods_code}."'
        transformation_pattern = (
            f'"Successfully transformed data for ods_code: {ods_code}"'
        )
        publishing_pattern = "Succeeded to send"

        assert cloudwatch_logs.find_log_message(context.lambda_name, extraction_pattern)
        assert cloudwatch_logs.find_log_message(
            context.lambda_name, transformation_pattern
        )
        assert cloudwatch_logs.find_log_message(context.lambda_name, publishing_pattern)


@pytest.fixture(scope="module")
def aws_lambda_client():
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    return LambdaWrapper(lambda_client, iam_resource)


@pytest.fixture(scope="module")
def shared_ods_data(playwright) -> Dict[str, List[Dict[str, Optional[str]]]]:
    logger.info("Building shared ODS data for session.")
    request_context = playwright.request.new_context()
    try:
        selector = OdsDateSelector(
            request_context=request_context, lookback_days=7, min_codes=10
        )
        chosen_date, ods_codes = selector.find_valid_date()
        organisation_details = get_ods_details(request_context, ods_codes)
        yield {
            "ods_codes": ods_codes,
            "organisation_details": organisation_details,
            "date": chosen_date,
        }
    finally:
        request_context.dispose()


def invoke_lambda_generic(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client,  # type: LambdaWrapper
    date_param: Optional[str] = None,
) -> Context:
    """
    Invokes the 'etl-ods-processor' lambda with optional date parameter.
    Stores the response in context.lambda_response and sets context.lambda_name.
    """
    lambda_name = get_resource_name(
        project, workspace, env, "etl-ods-processor", "lambda"
    )

    context.lambda_name = lambda_name

    payload = {"date": date_param} if date_param else {}
    logger.info(
        f"[STEP] Invoking Lambda '{lambda_name}'"
        + (f" with date: {date_param}" if date_param else " without parameters")
    )

    try:
        response = aws_lambda_client.invoke_function(lambda_name, payload)
        logger.info(f"[INFO] Lambda response received: {response}")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to invoke Lambda: {e}")
        raise

    context.lambda_response = response
    return context


@pytest.fixture
def context(shared_ods_data) -> Context:
    ctx = Context()
    ctx.ods_codes = shared_ods_data["ods_codes"]
    ctx.organisation_details = shared_ods_data["organisation_details"]
    ctx.extraction_date = shared_ods_data["date"]
    return ctx


@given(
    "extract ODS organisation records modified since yesterday",
    target_fixture="context",
)
def extract_ods_codes(context):
    return context


@given(
    "extract detailed organisation information for those ODS codes",
    target_fixture="context",
)
def load_organisation_info(context):
    return context


@given(
    parsers.parse('I invoke the lambda with invalid date "{invalid_date}"'),
    target_fixture="context",
)
def step_invoke_invalid_date(
    context: Context, invalid_date, project, workspace, env, aws_lambda_client
):
    return invoke_lambda_generic(
        context, project, workspace, env, aws_lambda_client, date_param=invalid_date
    )


@given("I invoke the lambda without required parameters", target_fixture="context")
def step_invoke_missing_params(
    context: Context, project, workspace, env, aws_lambda_client
):
    return invoke_lambda_generic(context, project, workspace, env, aws_lambda_client)


@given(
    parsers.parse('I invoke the lambda with a long past date "{past_date}"'),
    target_fixture="context",
)
def step_invoke_long_past_date(
    context: Context, past_date, project, workspace, env, aws_lambda_client
):
    return invoke_lambda_generic(
        context, project, workspace, env, aws_lambda_client, date_param=past_date
    )


@when("I invoke the lambda with the valid date", target_fixture="context")
def step_invoke_valid_date(
    context: Context, project, workspace, env, aws_lambda_client
):
    context = invoke_lambda_generic(
        context,
        project,
        workspace,
        env,
        aws_lambda_client,
        date_param=context.extraction_date,
    )
    context.lambda_invocation_time = int(datetime.now(timezone.utc).timestamp())
    assert context.lambda_response.get("statusCode") == 200
    return context


@then(
    parsers.parse(
        'the Lambda extracts, transforms, and publishes the transformed message to SQS for "{ods_type}" ODS codes'
    )
)
def verify_lambda_logs(context: Context, cloudwatch_logs, ods_type: str):
    ods_codes = (
        [context.ods_codes[0]] if ods_type.lower() == "single" else context.ods_codes
    )
    validate_lambda_logs_for_ods_codes(context, cloudwatch_logs, ods_codes)


@then(
    parsers.parse(
        'the organisation data should be updated in DynamoDB for "{ods_type}" ODS codes'
    )
)
def verify_dynamodb_records(
    context: Context, model_repo: AttributeLevelRepository, ods_type: str
):
    ods_codes = (
        [context.ods_codes[0]] if ods_type.lower() == "single" else context.ods_codes
    )
    verify_organisation_in_repo(model_repo, ods_codes, context.organisation_details)


@then("the lambda should return status code 400")
def assert_lambda_status_code(context: Context):
    actual_status = context.lambda_response.get("statusCode")
    logger.info(
        f"[STEP] Validating Lambda status code. Expected: 400, Actual: {actual_status}"
    )
    assert actual_status == 400, f"[FAIL] Expected 400, got {actual_status}"


@then(parsers.parse('the error message should be "{expected_message}"'))
def assert_lambda_error_message(context: Context, expected_message):
    actual_message = context.lambda_response.get("body", "")
    logger.info(
        f"[STEP] Validating Lambda error message. Expected to contain: '{expected_message}', Actual: '{actual_message}'"
    )
    assert expected_message in actual_message, (
        f"[FAIL] Expected error message '{expected_message}', got '{actual_message}'"
    )
