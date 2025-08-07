from ftrs_common.utils.api_url_util import get_api_url
from loguru import logger
from utilities.common.resource_name import get_resource_name
from utilities.infra.api_gateway_util import ApiGatewayToService


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
    logger.info("URL: {}", url)
    return url


def get_r53(workspace, api_name, env):
    # set the URL for the R53 record for the env
    workspace_suffix = f"-{workspace}" if workspace else ""
    r53 = f"{api_name}{workspace_suffix}.{env}.ftrs.cloud.nhs.uk"
    logger.info("R53 URL: {}", r53)
    return r53
