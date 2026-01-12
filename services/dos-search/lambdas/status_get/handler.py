from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from health_check.health_check_function import app as status_router

logger = Logger(service="dos-search-status")

app = APIGatewayRestResolver()
app.include_router(status_router)


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
