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
from ftrs_common.utils.request_id import REQUEST_ID_HEADER, generate_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_utils_logger = Logger.get(service="ods_utils")

TIMEOUT_SECONDS = 20


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
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_006, error_message=err_msg)
        raise KeyError(err_msg)
    return ods_url


def _get_api_key_for_url(url: str) -> str:
    env = os.environ.get("ENVIRONMENT")
    is_ods_terminology_request = "organisation-data-terminology-api" in url

    if env == "local":
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_005)
        if is_ods_terminology_request:
            return os.environ.get(
                "LOCAL_ODS_TERMINOLOGY_API_KEY", os.environ.get("LOCAL_API_KEY", "")
            )
        return os.environ.get("LOCAL_API_KEY", "")

    try:
        resource_prefix = get_resource_prefix()
        if is_ods_terminology_request:
            secret_name = f"/{resource_prefix}/ods-terminology-api-key"
        else:
            secret_name = f"/{resource_prefix}/apim-api-key"

        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]

        secret_dict = json.loads(secret)
        return secret_dict.get("api_key", secret)

    except json.JSONDecodeError as json_err:
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(json_err)
        )
        raise
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            ods_utils_logger.log(
                OdsETLPipelineLogBase.ETL_UTILS_006,
                secret_name=secret_name,
                error_message=str(e),
            )
        raise


def get_resource_prefix() -> str:
    project = os.environ.get("PROJECT_NAME")
    environment = os.environ.get("ENVIRONMENT")
    return f"{project}/{environment}"


def build_headers(options: dict) -> dict:
    """
    Builds headers for the outgoing HTTP request.
    All requests in ODS ETL use FHIR format by default and require API keys.
    The appropriate API key is automatically selected based on the URL.
    Expects options dict with keys: json_data, json_string, url, method
    """
    headers = {}
    json_data = options.get("json_data")
    json_string = options.get("json_string")
    url = options.get("url", "")
    correlation_id = fetch_or_set_correlation_id(get_correlation_id())

    headers = {
        CORRELATION_ID_HEADER: correlation_id,
        "Accept": "application/fhir+json",
        "apikey": _get_api_key_for_url(url),
    }

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


def make_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
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

        response_correlation_id = response.headers.get(CORRELATION_ID_HEADER)
        response_request_id = response.headers.get(REQUEST_ID_HEADER)
        if response_correlation_id:
            ods_utils_logger.append_keys(
                response_correlation_id=response_correlation_id
            )
        if response_request_id:
            ods_utils_logger.append_keys(response_request_id=response_request_id)

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
        response_correlation_id = response.headers.get("X-Correlation-ID")
        if response_correlation_id:
            ods_utils_logger.append_keys(
                response_correlation_id=response_correlation_id
            )

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
