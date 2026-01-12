from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.organization_handler import handle_get_organization

logger = Logger(service="dos-search-organization-router")
tracer = Tracer()

app = APIGatewayRestResolver()


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    return handle_get_organization(app)


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
