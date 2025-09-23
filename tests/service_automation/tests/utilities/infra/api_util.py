from ftrs_common.utils.api_url_util import get_api_url
from loguru import logger
from utilities.common.resource_name import get_resource_name
from utilities.infra.api_gateway_util import ApiGatewayToService
from playwright.sync_api import APIRequestContext
import pytest
import time
import json
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
    request_context: APIRequestContext,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict, str]] = None,
    json_data: Optional[Dict] = None,
    max_attempts: int = 2,
    timeout: int = 5000,  # milliseconds
) -> Dict:
    """
    Make an HTTP request using Playwright's sync API with retries.

    Args:
        request_context: Playwright APIRequestContext object.
        method: HTTP method (GET, POST, etc.)
        url: Request URL.
        headers: Optional headers.
        params: Optional query parameters.
        data: Optional raw data or string.
        json_data: Optional JSON data.
        max_attempts: Retry count.
        timeout: Timeout in milliseconds.

    Returns:
        Parsed JSON response as dict.

    Raises:
        pytest.fail if all retries fail.
    """
    method = method.upper()

    if json_data:
        data = json.dumps(json_data)
        headers = headers or {}
        headers["Content-Type"] = "application/json"

    for attempt in range(max_attempts):
        try:
            response = request_context.fetch(
                url,
                method=method,
                headers=headers,
                params=params,
                data=data,
                timeout=timeout,
            )

            if not response.ok:
                raise Exception(f"Status code: {response.status}, body: {response.text()}")

            return response.json()

        except Exception as e:
            if attempt == max_attempts - 1:
                pytest.fail(f"API call failed after {max_attempts} attempts: {e}")
            else:
                print(f"[Retry {attempt + 1}] Request failed: {e}. Retrying...")
                time.sleep(2)
