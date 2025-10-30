from aws_lambda_powertools.utilities.typing import LambdaContext
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ftrs_common.api_middleware.correlation_id_middleware import CorrelationIdMiddleware
from ftrs_common.api_middleware.fhir_type_middleware import (
    FHIRAcceptHeaderMiddleware,
    FHIRContentTypeMiddleware,
)

# from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
from ftrs_common.api_middleware.response_logging_middleware import (
    ResponseLoggingMiddleware,
)
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.fhir.operation_outcome_status_mapper import STATUS_CODE_MAP
from ftrs_common.logger import Logger
from ftrs_common.utils.request_id import fetch_or_set_request_id
from mangum import Mangum

from organisations.app.router import organisation

crud_organisation_logger = Logger.get(service="crud_organisation_logger")
app = FastAPI(title="Organisations API")
app.add_middleware(FHIRContentTypeMiddleware)
app.add_middleware(FHIRAcceptHeaderMiddleware)
app.add_middleware(ResponseLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
# app.add_middleware(RequestIdMiddleware)

app.include_router(organisation.router)


def handler(event: dict, context: LambdaContext) -> dict:
    fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=event.get("headers", {}).get("X-Request-ID"),
    )

    mangum_handler = Mangum(app, lifespan="off")
    return mangum_handler(event, context)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    raise OperationOutcomeException(
        OperationOutcomeHandler.build(
            diagnostics=str(exc), code="invalid", severity="error"
        )
    )


@app.exception_handler(OperationOutcomeException)
async def operation_outcome_exception_handler(
    request: Request, exc: OperationOutcomeException
) -> JSONResponse:
    status_code = STATUS_CODE_MAP.get(exc.outcome["issue"][0]["code"], 500)
    return JSONResponse(
        status_code=status_code,
        content=exc.outcome,
        media_type=organisation.FHIR_MEDIA_TYPE,
    )
