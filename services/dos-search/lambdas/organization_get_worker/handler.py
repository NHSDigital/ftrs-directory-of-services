from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from functions.dos_search_ods_code_function import app as organization_app

# Worker lambda for GET /Organization.
#
# For the spike, this reuses the existing handler/router logic directly.
# In future, you can split steps further (e.g., query OpenSearch in one worker
# and map to FHIR in another) while keeping the API-facing router lambda stable.

logger = Logger(service="dos-search-organization-worker")
tracer = Tracer()

app = APIGatewayRestResolver()
app.include_router(organization_app)


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
