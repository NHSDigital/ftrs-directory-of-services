import json
import os
from functools import cache
from urllib.parse import urlparse

import boto3
import requests
from aws_lambda_powertools.utilities.parameters import get_parameter
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.exceptions import ClientError
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
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


# will need to change to fit different branches
@cache
def get_base_fhir_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")

    if env == "local":
        return os.environ["LOCAL_FHIR_API_URL"]

    return f"https://internal-{env}.api.service.nhs.uk/dos-ingestion/FHIR/R4"


def get_api_key() -> str:
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


def build_headers(options: dict) -> dict:
    """
    Builds headers for the outgoing HTTP request.
    Expects options dict with keys: json_data, json_string, fhir, sign, url, method
    """
    headers = {}
    json_data = options.get("json_data")
    json_string = options.get("json_string")
    fhir = options.get("fhir")
    sign = options.get("sign")
    url = options.get("url")
    method = options.get("method")
    api_key = options.get("api_key")
    # Prepare JSON body if present
    if json_data is not None:
        headers["Content-Type"] = "application/json"
    if api_key is not None:
        headers["apikey"] = api_key
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
    if data.get("resourceType") == "OperationOutcome" and "issue" in data:
        raise OperationOutcomeException(data)
    return data


def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    timeout: int = 20,
    sign: bool = False,
    fhir: bool = False,
    api_key: str = None,
    **kwargs: dict,
) -> requests.Response:
    json_data = kwargs.get("json")
    json_string = json.dumps(json_data) if json_data is not None else None

    ods_utils_logger.log(
        OdsETLPipelineLogBase.ETL_UTILS_TEMP,
        ods_code="WIPPPP",
        data=json_data,
        uuid=url,
    )

    headers = build_headers(
        {
            "json_data": json_data,
            "json_string": json_string,
            "fhir": fhir,
            "sign": sign,
            "url": url,
            "method": method,
            "api_key": api_key,
        }
    )

    ods_utils_logger.log(
        OdsETLPipelineLogBase.ETL_UTILS_TEMP,
        ods_code="WIPPPP2",
        data=headers,
        uuid=url,
    )

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
