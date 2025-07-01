import json
import os
from functools import cache
from urllib.parse import urlparse

import boto3
import requests
from aws_lambda_powertools.utilities.parameters import get_parameter
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_utils_logger = Logger.get(service="ods_utils")


@cache
def get_base_crud_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")
    workspace = os.environ.get("WORKSPACE", None)

    if env == "local":
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_001)
        return os.environ["LOCAL_CRUD_API_URL"]

    base_parameter_path = f"/ftrs-dos-{env}-crud-apis"
    if workspace:
        base_parameter_path += f"-{workspace}"

    parameter_path = f"{base_parameter_path}/endpoint"
    ods_utils_logger.log(
        OdsETLPipelineLogBase.ETL_UTILS_002, parameter_path=parameter_path
    )
    return get_parameter(name=parameter_path)


def get_signed_request_headers(
    method: str,
    url: str,
    data: str | None = None,
    host: str = None,
    region: str = "eu-west-2",
) -> dict:
    session = boto3.Session()
    request = AWSRequest(method=method, url=url, data=data, headers={"Host": host})
    SigV4Auth(session.get_credentials(), "execute-api", region).add_auth(request)
    return dict(request.headers)


def build_headers(
    json_data: dict,
    json_string: str,
    fhir: bool,
    sign: bool,
    url: str,
    method: str,
) -> dict:
    """
    Builds headers for the outgoing HTTP request.
    """
    headers = {}
    # Prepare JSON body if present
    if json_data is not None:
        headers["Content-Type"] = "application/json"
    # Set FHIR headers if needed
    if fhir:
        headers["Accept"] = "application/fhir+json"
        if json_string is not None:
            headers["Content-Type"] = "application/fhir+json"
    # Handle AWS SigV4 signing if required
    if sign:
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        signed_headers = get_signed_request_headers(
            method=method,
            url=url,
            host=host,
            data=json_string,
            region="eu-west-2",
        )
        headers.update(signed_headers)
    return headers


def handle_fhir_response(data: dict) -> dict:
    """
    Checks for FHIR OperationOutcome and raises an exception if found.
    """
    if data.get("resourceType") == "OperationOutcome":
        issue = data.get("issue", [{}])[0]
        diagnostics = issue.get("diagnostics", "Unknown error")
        code = issue.get("code", "unknown")
        ods_utils_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_004,
            code=code,
            diagnostics=diagnostics,
        )
        raise Exception(f"FHIR OperationOutcome: {code} - {diagnostics}")
    return data


def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    timeout: int = 20,
    sign: bool = False,
    fhir: bool = False,
    **kwargs: dict,
) -> requests.Response:
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    headers = build_headers(json_data, json_string, fhir, sign, url, method)

    try:
        response = requests.request(
            url=url,
            method=method,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )
        response.raise_for_status()

        if fhir:
            data = response.json()
            return handle_fhir_response(data)
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
