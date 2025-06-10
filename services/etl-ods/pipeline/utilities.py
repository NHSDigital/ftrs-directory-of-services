import json
import logging
import os
from functools import cache
from urllib.parse import urlparse

import boto3
import requests
from aws_lambda_powertools.utilities.parameters import get_parameter
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger()


@cache
def get_base_crud_api_url() -> str:
    env = os.environ.get("ENVIRONMENT", "local")
    workspace = os.environ.get("WORKSPACE", None)

    if env == "local":
        logging.info(
            "Running in local environment, using LOCAL_CRUD_API_URL environment variable"
        )
        return os.environ["LOCAL_CRUD_API_URL"]

    base_parameter_path = f"/ftrs-dos-{env}-crud-apis"
    if workspace:
        base_parameter_path += f"-{workspace}"

    parameter_path = f"{base_parameter_path}/endpoint"
    logging.info(f"Fetching base CRUD API URL from parameter store: {parameter_path}")
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


def make_request(
    url: str,
    method: str = "GET",
    params: dict = None,
    timeout: int = 20,
    sign: bool = False,
    **kwargs: dict,
) -> requests.Response:
    headers = {}

    json_data = kwargs.get("json")
    json_string = None
    if json_data is not None:
        headers["Content-Type"] = "application/json"
        json_string = json.dumps(json_data)

    if sign is True:
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        headers = get_signed_request_headers(
            method=method,
            url=url,
            host=host,
            data=json_string,
            region="eu-west-2",
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

    except requests.exceptions.HTTPError as http_err:
        logger.warning(
            f"HTTP error occurred: {http_err} - Status Code: {response.status_code}"
        )
        raise

    except requests.exceptions.RequestException as e:
        logger.warning(f"Request to {method} {url} failed: {e}")
        raise

    return response
