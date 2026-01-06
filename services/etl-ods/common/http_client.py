import json

import requests
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    CORRELATION_ID_HEADER,
    fetch_or_set_correlation_id,
    get_correlation_id,
)
from ftrs_common.utils.request_id import REQUEST_ID_HEADER
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

TIMEOUT_SECONDS = 20
FHIR_JSON_CONTENT_TYPE = "application/fhir+json"
RESOURCE_TYPE_OPERATION_OUTCOME = "OperationOutcome"

http_client_logger = Logger.get(service="ods_http_client")


def handle_operation_outcomes(data: dict, method: str | None = None) -> dict:
    if data.get("resourceType") != RESOURCE_TYPE_OPERATION_OUTCOME:
        return data

    severities = {
        issue.get("severity") for issue in data["issue"] if isinstance(issue, dict)
    }

    # Special case: PUT requests allow informational OperationOutcome
    if method and method.upper() == "PUT" and severities.issubset({"information"}):
        return data

    raise OperationOutcomeException(data)


def build_headers(
    json_data: dict | None = None,
    json_string: str | None = None,
    api_key: str | None = None,
    auth_headers: dict | None = None,
) -> dict:
    correlation_id = fetch_or_set_correlation_id(get_correlation_id())

    headers = {
        CORRELATION_ID_HEADER: correlation_id,
        "Accept": FHIR_JSON_CONTENT_TYPE,
    }

    if api_key:
        headers["apikey"] = api_key

    if auth_headers:
        headers.update(auth_headers)

    if json_data is not None or json_string is not None:
        headers["Content-Type"] = FHIR_JSON_CONTENT_TYPE

    return headers


def make_request(
    url: str,
    method: str = "GET",
    params: dict | None = None,
    headers: dict | None = None,
    **kwargs: dict,
) -> dict:
    http_client_logger.append_keys(
        correlation_id=headers.get(CORRELATION_ID_HEADER) if headers else None,
        request_id=headers.get(REQUEST_ID_HEADER) if headers else None,
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
            http_client_logger.append_keys(
                response_correlation_id=response_correlation_id
            )
        if response_request_id:
            http_client_logger.append_keys(response_request_id=response_request_id)

    except requests.exceptions.HTTPError as http_err:
        http_client_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_003,
            http_err=http_err,
            status_code=getattr(http_err.response, "status_code", None),
        )
        raise
    except requests.exceptions.RequestException as e:
        http_client_logger.log(
            OdsETLPipelineLogBase.ETL_UTILS_004,
            method=method,
            url=url,
            error_message=str(e),
        )
        raise
    else:
        try:
            response_data = response.json()
        except json.JSONDecodeError as json_err:
            http_client_logger.log(
                OdsETLPipelineLogBase.ETL_UTILS_007, error_message=str(json_err)
            )
            raise
        else:
            result = handle_operation_outcomes(response_data, method)
            result["status_code"] = response.status_code
            return result
