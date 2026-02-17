from dos_ingest.logging import logger
from dos_ingest.router import healthcare, location, organisation
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ftrs_common.api_middleware.correlation_id_middleware import CorrelationIdMiddleware
from ftrs_common.api_middleware.fhir_type_middleware import (
    FHIRAcceptHeaderMiddleware,
    FHIRContentTypeMiddleware,
)
from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
from ftrs_common.api_middleware.response_logging_middleware import (
    ResponseLoggingMiddleware,
)
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.fhir.operation_outcome_status_mapper import STATUS_CODE_MAP

app = FastAPI(title="DoS Ingest API")

app.add_middleware(FHIRContentTypeMiddleware)
app.add_middleware(FHIRAcceptHeaderMiddleware)
app.add_middleware(ResponseLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(organisation.router, prefix="/Organization")
app.include_router(location.router, prefix="/Location")
app.include_router(healthcare.router, prefix="/HealthcareService")


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


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "exception",
                    "diagnostics": "An unexpected error occurred",
                }
            ],
        },
        media_type=organisation.FHIR_MEDIA_TYPE,
    )
