from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from mangum import Mangum

from organisations.app.router import organisation

app = FastAPI(title="Organisations API", root_path="/Organization")
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
