from ftrs_common.utils.api_url_util import get_api_url
from loguru import logger
from utilities.common.resource_name import get_resource_name
from utilities.infra.api_gateway_util import ApiGatewayToService
import requests
import pytest
import time
from typing import Optional, Dict, Any, Union


def get_api_gateway_url(workspace, stack, project, env):
    # get the api gateway name env var and then the api gateway id
    apigateway_name = get_resource_name(project, workspace, env, stack, "api-gateway")
    logger.info("Fetching API Gateway ID for: {}", apigateway_name)
    agts = ApiGatewayToService()
    apigatewayid = agts.get_rest_api_id(apigateway_name)
    # set the URL for the api-gateway stage identified by the workspace and api gateway id
    return (
        "https://" + str(apigatewayid) + ".execute-api.eu-west-2.amazonaws.com/default"
    )


def get_url(api_name):
    # set the URL for the R53 record for the env
    url = get_api_url(api_name)
    logger.debug("URL: {}", url)
    return url


def get_r53(workspace, api_name, env):
    # set the URL for the R53 record for the env
    workspace_suffix = f"-{workspace}" if workspace else ""
    r53 = f"{api_name}{workspace_suffix}.{env}.ftrs.cloud.nhs.uk"
    logger.debug("R53 URL: {}", r53)
    return r53

def make_api_request_with_retries(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict, str]] = None,
    json: Optional[Dict] = None,
    max_attempts: int = 2,
    timeout: int = 5,
) -> Dict:
    """
    Make an HTTP request with retries and flexible options.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: The API endpoint URL.
        headers: Optional HTTP headers.
        params: Optional URL query parameters.
        data: Optional data payload (for POST/PUT).
        json: Optional JSON payload (for POST/PUT).
        max_attempts: Number of retries before failing.
        timeout: Timeout in seconds for each request.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        pytest.fail if all attempts fail.
    """
    method = method.upper()
    for attempt in range(max_attempts):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            if attempt == max_attempts - 1:
                pytest.fail(f"API call failed after {max_attempts} attempts: {err}")
            else:
                print(f"Attempt {attempt + 1} failed for {method} {url}. Retrying...")
                time.sleep(2)