from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from fastapi import FastAPI
from ftrs_common.api_middleware.correlation_id_middleware import CorrelationIdMiddleware
from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
from ftrs_common.feature_flags import FeatureFlag, FeatureFlagsClient
from ftrs_common.logger import Logger
from ftrs_common.utils.request_id import fetch_or_set_request_id
from ftrs_data_layer.logbase import CrudApisLogBase
from mangum import Mangum

from location.app.router import location

location_service_logger = Logger.get(service="crud_location_logger")

app = FastAPI(title="Location API", root_path="/location")
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestIdMiddleware)
app.include_router(location.router)
# Initialize outside handler - reused across invocations
FEATURE_FLAGS_CLIENT: FeatureFlagsClient = FeatureFlagsClient()


def handler(event: dict, context: LambdaContext) -> dict:
    if FEATURE_FLAGS_CLIENT.is_enabled(
        FeatureFlag.DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED
    ):
        location_service_logger.log(
            CrudApisLogBase.CRUD_API_001,
        )
    else:
        location_service_logger.log(
            CrudApisLogBase.CRUD_API_002,
        )
        return {
            "statusCode": HTTPStatus.SERVICE_UNAVAILABLE,
            "body": "Service Unavailable: Data Migration Search Triage Code feature is disabled.",
        }
    fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=event.get("headers", {}).get("X-Request-ID"),
    )

    mangum_handler = Mangum(app, lifespan="off")
    return mangum_handler(event, context)
