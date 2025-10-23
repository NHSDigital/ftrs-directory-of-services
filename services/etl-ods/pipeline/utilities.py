import json
import os
from functools import cache

import requests
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    CORRELATION_ID_HEADER,
    fetch_or_set_correlation_id,
    get_correlation_id,
)
from ftrs_common.utils.jwt_auth import JWTAuthenticator
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_utils_logger = Logger.get(service="ods_utils")


def get_jwt_authenticator() -> JWTAuthenticator:
    environment = os.environ.get("ENVIRONMENT", "local")
    resource_prefix = get_resource_prefix()

    return JWTAuthenticator(
        environment=environment,
        region=os.environ["AWS_REGION"],
        secret_name=f"/{resource_prefix}/apim-jwt-credentials",
    )


@cache
def get_base_apim_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ["LOCAL_APIM_API_URL"]

    return os.environ.get("APIM_URL")


def get_resource_prefix() -> str:
    project = os.environ.get("PROJECT_NAME")
    environment = os.environ.get("ENVIRONMENT")
    return f"{project}/{environment}"


def build_headers(options: dict) -> dict:
    headers = {}
    json_data = options.get("json_data")
    json_string = options.get("json_string")
    fhir = options.get("fhir")
    jwt_required = options.get("jwt_required", False)
    correlation_id = fetch_or_set_correlation_id(get_correlation_id())
    headers[CORRELATION_ID_HEADER] = correlation_id

    # Prepare JSON body if present
    if json_data is not None:
        headers["Content-Type"] = "application/json"

    if jwt_required:
        jwt_auth = get_jwt_authenticator()
        auth_headers = jwt_auth.get_auth_headers()
        headers.update(auth_headers)

    # Set FHIR headers if needed
    if fhir:
        headers["Accept"] = "application/fhir+json"
        if json_string is not None:
            headers["Content-Type"] = "application/fhir+json"
    return headers


def handle_fhir_response(data: dict, method: str = None) -> None:
    if data.get("resourceType") == "OperationOutcome" and "issue" in data:
        severities = {
            issue.get("severity") for issue in data["issue"] if isinstance(issue, dict)
        }
        # For PUT: allow informational OperationOutcome, raise for any other severity
        if method and method.upper() == "PUT":
            if not severities.issubset({"information"}):
                raise OperationOutcomeException(data)
            return
        # For all other methods: raise for any OperationOutcome
        raise OperationOutcomeException(data)
    return


def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    fhir: bool = False,
    jwt_required: bool = False,
    **kwargs: dict,
) -> requests.Response:
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    headers = build_headers(
        {
            "json_data": json_data,
            "json_string": json_string,
            "fhir": fhir,
            "url": url,
            "method": method,
            "jwt_required": jwt_required,
        }
    )
    ods_utils_logger.append_keys(correlation_id=headers.get("X-Correlation-ID"))

    try:
        TIMEOUT_SECONDS = 20
        response = requests.request(
            url=url,
            method=method,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
        response.raise_for_status()

        response_correlation_id = response.headers.get("X-Correlation-ID")
        if response_correlation_id:
            ods_utils_logger.append_keys(
                response_correlation_id=response_correlation_id
            )

        if fhir:
            handle_fhir_response(response.json(), method)
            return response
        else:
            return response
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
