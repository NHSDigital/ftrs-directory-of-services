from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from mangum import Mangum
from pydantic import ValidationError

from organisations.app.router import organisation

crud_organisation_logger = Logger.get(service="crud_organisation_logger")


app = FastAPI(title="Organisations API")
app.include_router(organisation.router)

handler = Mangum(app, lifespan="off")

STATUS_CODE_MAP = {
    "not-found": 404,
    "invalid": 422,
    "exception": 500,
    "forbidden": 403,
    "processing": 202,
    "duplicate": 409,
    "structure": 400,
    "security": 401,
    "not-supported": 405,
    "business-rule": 422,
    "informational": 200,
}


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


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_023,
        error_message=str(exc),
        validation_errors=str(exc.errors()),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
