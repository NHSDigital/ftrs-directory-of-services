import json
import os
from functools import cache

import boto3
import requests
from botocore.exceptions import ClientError
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    CORRELATION_ID_HEADER,
    fetch_or_set_correlation_id,
    get_correlation_id,
)
from ftrs_common.utils.jwt_auth import JWTAuthenticator
from ftrs_common.utils.request_id import REQUEST_ID_HEADER
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_utils_logger = Logger.get(service="ods_utils")

TIMEOUT_SECONDS = 20


def get_jwt_authenticator() -> JWTAuthenticator:
    environment = os.environ.get("ENVIRONMENT", "local")
    resource_prefix = get_resource_prefix()

    return JWTAuthenticator(
        environment=environment,
        region=os.environ["AWS_REGION"],
        secret_name=f"/{resource_prefix}/dos-ingest-jwt-credentials",
    )


@cache
def get_base_apim_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ["LOCAL_APIM_API_URL"]

    return os.environ.get("APIM_URL")


@cache
def get_base_ods_terminology_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ.get(
            "LOCAL_ODS_URL",
            "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        )

    ods_url = os.environ.get("ODS_URL")
    if ods_url is None:
        err_msg = "ODS_URL environment variable is not set"
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_012, error_message=err_msg)
        raise KeyError(err_msg)
    return ods_url


def _is_ods_terminology_request(url: str) -> bool:
    return "organisation-data-terminology-api" in url


def _is_mock_testing_mode() -> bool:
    """
    Check if we're currently in mock testing mode.
    Mock testing scenarios can only be enabled in dev and test environments
    for security reasons to prevent accidental use in production.
    """
    mock_testing_enabled = (
        os.environ.get("MOCK_TESTING_SCENARIOS", "").lower() == "true"
    )

    if not mock_testing_enabled:
        return False

    # Validate that mock testing is only enabled in authorized environments
    current_env = os.environ.get("ENVIRONMENT", "").lower()
    allowed_environments = ["dev", "test"]

    if current_env not in allowed_environments:
        error_msg = f"Mock testing scenarios cannot be enabled in environment '{current_env}'. Only allowed in: {', '.join(allowed_environments)}"
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_011, env=current_env)
        raise ValueError(error_msg)

    return True


def _get_local_api_key() -> str:
    ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_005)
    return os.environ.get(
        "LOCAL_ODS_TERMINOLOGY_API_KEY", os.environ.get("LOCAL_API_KEY", "")
    )


def _get_production_api_key() -> str:
    """Get API key for production environment from Secrets Manager."""
    try:
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_010)
        resource_prefix = get_resource_prefix()
        secret_name = f"/{resource_prefix}/ods-terminology-api-key"
        return _get_secret_from_aws(secret_name)

    except KeyError:
        # Re-raise as original exception type expected by callers
        raise
    except Exception as e:
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(e))
        raise


def _get_api_key_for_url(url: str) -> str:
    """
    Get API key for ODS Terminology API requests.

    In mock testing mode (when MOCK_TESTING_SCENARIOS env var is set to 'true'),
    retrieves API key for mock API Gateway from Secrets Manager.
    Otherwise, fetches production API key from Secrets Manager or local environment.
    """
    if not _is_ods_terminology_request(url):
        return ""

    if _is_mock_testing_mode():
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_008)
        return _get_mock_api_key_from_secrets()

    env = os.environ.get("ENVIRONMENT")
    if env == "local":
        return _get_local_api_key()
    return _get_production_api_key()


def _get_mock_api_key_from_secrets() -> str:
    """
    Retrieve mock API key from AWS Secrets Manager for testing scenarios.
    """
    try:
        project = os.environ.get("PROJECT_NAME")
        environment = os.environ.get("ENVIRONMENT")
        workspace = os.environ.get("WORKSPACE", "")

        # Follow the same pattern as Terraform locals: project-environment
        project_prefix = f"{project}-{environment}"
        workspace_suffix = f"-{workspace}" if workspace else ""
        secret_name = f"/{project_prefix}/mock-api/api-key{workspace_suffix}"

        return _get_secret_from_aws(secret_name)

    except KeyError as e:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_006,
            secret_name=secret_name,
            error_message=f"Mock API key secret not found: {e}",
        )
        err_msg = f"Mock API key secret not found: {e}"
        raise KeyError(err_msg)
    except Exception as e:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_007,
            error_message=f"Failed to retrieve mock API key: {e}",
        )
        raise


def get_resource_prefix() -> str:
    project = os.environ.get("PROJECT_NAME")
    environment = os.environ.get("ENVIRONMENT")
    return f"{project}/{environment}"


def _get_secret_from_aws(secret_name: str) -> str:
    """
    Retrieve a secret from AWS Secrets Manager.
    """
    try:
        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]

        try:
            secret_dict = json.loads(secret)
            return secret_dict.get("api_key", secret)
        except json.JSONDecodeError:
            # If not JSON, treat as plain string
            return secret

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            ods_utils_logger.log(
                OdsETLPipelineLogBase.ETL_UTILS_006,
                secret_name=secret_name,
                error_message=str(e),
            )
            err_msg = f"Secret not found: {secret_name}"
            raise KeyError(err_msg)
        raise
    except json.JSONDecodeError as json_err:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(json_err)
        )
        raise


def _add_api_key_to_headers(headers: dict, api_key: str) -> None:
    """Add API key to headers using the appropriate header name for the current mode."""
    if not api_key:
        return

    # Mock API Gateways use AWS standard x-api-key header instead of custom apikey
    if _is_mock_testing_mode():
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_009)
        headers["x-api-key"] = api_key
    else:
        headers["apikey"] = api_key


def build_headers(options: dict) -> dict:
    """
    Builds headers for the outgoing HTTP request.
    All requests in ODS ETL use FHIR format by default and require API keys.
    The appropriate API key is automatically selected based on the URL.
    """
    headers = {}
    json_data = options.get("json_data")
    json_string = options.get("json_string")
    jwt_required = options.get("jwt_required", False)
    url = options.get("url", "")
    correlation_id = fetch_or_set_correlation_id(get_correlation_id())

    headers = {
        CORRELATION_ID_HEADER: correlation_id,
        "Accept": "application/fhir+json",
    }

    api_key = _get_api_key_for_url(url)
    _add_api_key_to_headers(headers, api_key)

    if jwt_required:
        jwt_auth = get_jwt_authenticator()
        auth_headers = jwt_auth.get_auth_headers()
        headers.update(auth_headers)

    # Set Content-Type based on whether we have JSON data
    if json_data is not None or json_string is not None:
        headers["Content-Type"] = "application/fhir+json"

    return headers


def handle_operation_outcomes(data: dict, method: str | None = None) -> dict:
    if data.get("resourceType") != "OperationOutcome":
        return data

    severities = {
        issue.get("severity") for issue in data["issue"] if isinstance(issue, dict)
    }

    # Special case: PUT requests allow informational OperationOutcome
    if method and method.upper() == "PUT" and severities.issubset({"information"}):
        return data

    raise OperationOutcomeException(data)


def _update_logger_with_response_headers(response: requests.Response) -> None:
    """Helper function to update logger with response headers."""
    response_correlation_id = response.headers.get(CORRELATION_ID_HEADER)
    response_request_id = response.headers.get(REQUEST_ID_HEADER)

    if response_correlation_id:
        ods_utils_logger.append_keys(response_correlation_id=response_correlation_id)
    if response_request_id:
        ods_utils_logger.append_keys(response_request_id=response_request_id)


def make_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    jwt_required: bool = False,
    **kwargs: dict,
) -> dict:
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    headers = build_headers(
        {
            "json_data": json_data,
            "json_string": json_string,
            "url": url,
            "method": method,
            "jwt_required": jwt_required,
        }
    )
    ods_utils_logger.append_keys(
        correlation_id=headers.get(CORRELATION_ID_HEADER),
        request_id=headers.get(REQUEST_ID_HEADER),
    )

    try:
        response = requests.request(
            url=url,
            method=method,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
        response.raise_for_status()
        _update_logger_with_response_headers(response)

    except requests.exceptions.HTTPError as http_err:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_003,
            http_err=http_err,
            status_code=getattr(http_err.response, "status_code", None),
        )
        raise
    except requests.exceptions.RequestException as e:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_004,
            method=method,
            url=url,
            error_message=str(e),
        )
        raise
    else:
        _update_logger_with_response_headers(response)

        try:
            response_data = response.json()
        except json.JSONDecodeError as json_err:
            ods_utils_logger.log(
                OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(json_err)
            )
            raise
        else:
            result = handle_operation_outcomes(response_data, method)
            result["status_code"] = response.status_code
            return result
