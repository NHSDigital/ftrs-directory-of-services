import json
import os
from functools import cache

import boto3
import requests
from botocore.exceptions import ClientError
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

ods_utils_logger = Logger.get(service="ods_utils")


@cache
def get_base_apim_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ["LOCAL_APIM_API_URL"]

    return os.environ.get("APIM_URL")


def _get_api_key() -> str:
    env = os.environ.get("ENVIRONMENT")

    if env == "local":
        ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_005)
        return os.environ["LOCAL_API_KEY"]
    try:
        resource_prefix = get_resource_prefix()
        secret_name = f"/{resource_prefix}/apim-api-key"
        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]
        try:
            secret_dict = json.loads(secret)
            return secret_dict.get("api_key", secret)
        except json.JSONDecodeError:
            ods_utils_logger.log(OdsETLPipelineLogBase.ETL_UTILS_007)
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
    Expects options dict with keys: json_data, json_string, fhir, url, method, api_key_required
    """
    headers = {}
    json_data = options.get("json_data")
    json_string = options.get("json_string")
    fhir = options.get("fhir")
    api_key_required = options.get("api_key_required", False)
    # Prepare JSON body if present
    if json_data is not None:
        headers["Content-Type"] = "application/json"
    if api_key_required:
        headers["apikey"] = _get_api_key()
    # Set FHIR headers if needed
    if fhir:
        headers["Accept"] = "application/fhir+json"
        if json_string is not None:
            headers["Content-Type"] = "application/fhir+json"
    return headers


def handle_fhir_response(data: dict) -> dict:
    if data.get("resourceType") == "OperationOutcome" and "issue" in data:
        raise OperationOutcomeException(data)
    return data


def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    fhir: bool = False,
    api_key_required: bool = True,
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
            "api_key_required": api_key_required,
        }
    )

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

        if fhir:
            data = response.json()
            return handle_fhir_response(data)
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
