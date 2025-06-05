from utilities.infra.api_gateway_util import ApiGatewayToService
from loguru import logger


def get_url(workspace, stack, project, env):
    # get the api gateway name env var and then the api gateway id
    logger.info("Fetching API Gateway ID for: {}", stack)
    if workspace == "default":
        apigateway_name = project + "-" + env + "-" + stack + "-" + "api-gateway"
    else:
        apigateway_name = project + "-" + env + "-" + stack + "-" + "api-gateway-" + workspace
    logger.info("Fetching API Gateway ID for: {}", apigateway_name)
    agts = ApiGatewayToService()
    apigatewayid = agts.get_rest_api_id(apigateway_name)

    # set the URL for the api-gateway stage identified by the workspace and api gateway id
    return (
        "https://" + str(apigatewayid) + ".execute-api.eu-west-2.amazonaws.com/default"
    )
