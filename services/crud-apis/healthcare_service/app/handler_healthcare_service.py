from aws_lambda_powertools.utilities.typing import LambdaContext
from fastapi import FastAPI
from ftrs_common.api_middleware.correlation_id_middleware import CorrelationIdMiddleware
from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
from ftrs_common.logger import Logger
from ftrs_common.utils.request_id import fetch_or_set_request_id
from mangum import Mangum

from healthcare_service.app.router import healthcare

crud_healthcare_logger = Logger.get(service="crud_healthcare_logger")

app = FastAPI(title="Healthcare Services API", root_path="/healthcare-service")
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestIdMiddleware)
app.include_router(healthcare.router)


def handler(event: dict, context: LambdaContext) -> dict:
    fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=event.get("headers", {}).get("X-Request-ID"),
    )

    mangum_handler = Mangum(app, lifespan="off")
    return mangum_handler(event, context)
