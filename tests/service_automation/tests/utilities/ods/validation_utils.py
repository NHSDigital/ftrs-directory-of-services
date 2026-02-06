import time

from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from step_definitions.common_steps import data_steps

from utilities.common.context import Context

# Data verification constants
DATA_VERIFICATION_RETRY_COUNT = 5
DATA_VERIFICATION_RETRY_DELAY_SECONDS = 5


def assert_org_details_match(item: DBModel, expected_org: dict) -> None:
    """Assert organization details match expected values."""
    assert item is not None, "No data found in repository"
    assert getattr(item, "identifier_ODS_ODSCode", None) == expected_org["ods_code"]

    assert getattr(item, "name", None) is not None
    assert getattr(item, "type", None) is not None

    assert isinstance(getattr(item, "active", None), bool)
    assert getattr(item, "active", None) == expected_org["active"]

    actual_telecom = getattr(item, "telecom", None)
    expected_phone = expected_org["phone"]

    if expected_phone:
        assert actual_telecom is not None
        assert len(actual_telecom) > 0
        phone_values = [t.value for t in actual_telecom if hasattr(t, "value")]
        assert expected_phone in phone_values

    actual_updated_by = getattr(item, "lastUpdatedBy", None)
    assert actual_updated_by is not None
    assert hasattr(actual_updated_by, "value")

    # Verify role codes if present
    primary_role = getattr(item, "primary_role_code", None)
    non_primary_roles = getattr(item, "non_primary_role_codes", [])

    if primary_role:
        primary_role_value = (
            primary_role.value
            if isinstance(primary_role, OrganisationTypeCode)
            else primary_role
        )
        assert primary_role_value is not None
        assert primary_role_value.startswith("RO")

    if non_primary_roles:
        non_primary_values = [
            role.value if isinstance(role, OrganisationTypeCode) else role
            for role in non_primary_roles
        ]

        for role_value in non_primary_values:
            assert role_value is not None
            assert role_value.startswith("RO")

        # Validate RO177 requires RO76
        if primary_role:
            primary_role_value = (
                primary_role.value
                if isinstance(primary_role, OrganisationTypeCode)
                else primary_role
            )
            if primary_role_value == "RO177":
                assert "RO76" in non_primary_values


def verify_organisation_in_repo(
    model_repo: AttributeLevelRepository, ods_codes: list, organisation_details: list
):
    """Verify organizations exist in repository with retry logic."""
    if not ods_codes:
        raise ValueError("No ODS codes provided for verification")
    if isinstance(ods_codes, str):
        ods_codes = [ods_codes]

    for attempt in range(DATA_VERIFICATION_RETRY_COUNT):
        try:
            for ods_code in ods_codes:
                item = data_steps.get_from_repo(model_repo, ods_code)
                if not item:
                    raise AssertionError(
                        f"No record found in repository for {ods_code}"
                    )
                expected_org = next(
                    org for org in organisation_details if org["ods_code"] == ods_code
                )
                assert_org_details_match(item, expected_org)
            return
        except AssertionError:
            if attempt < DATA_VERIFICATION_RETRY_COUNT - 1:
                time.sleep(DATA_VERIFICATION_RETRY_DELAY_SECONDS)
            else:
                raise


def verify_error_message(context, expected_error: str):
    """Verify error message in response."""
    response = context.lambda_response
    error_body = response.get("body")
    if error_body:
        assert expected_error in error_body, (
            f"Expected error '{expected_error}' not found in response body"
        )


def verify_lambda_status_code(context, status_code: int) -> None:
    """Verify lambda returned expected status code."""
    actual_status = context.lambda_response.get("statusCode")
    assert actual_status == status_code, (
        f"Expected status code {status_code}, got {actual_status}"
    )


def assert_lambda_error_message(context: Context, expected_message: str) -> None:
    """Verify lambda response contains expected error message."""
    actual_message = context.lambda_response.get("body", "")
    assert expected_message in actual_message, (
        f"[FAIL] Expected error message '{expected_message}', got '{actual_message}'"
    )


def verify_consumer_success(context: Context) -> None:
    """Verify that the consumer processed messages successfully."""
    assert hasattr(context, "extraction_date"), (
        "Expected context to have extraction_date"
    )


def verify_dynamodb_records(context: Context, model_repo, ods_type: str) -> None:
    """Verify organization data is properly stored in DynamoDB."""
    ods_codes = (
        [context.ods_codes[0]] if ods_type.lower() == "single" else context.ods_codes
    )
    verify_organisation_in_repo(model_repo, ods_codes, context.organisation_details)
