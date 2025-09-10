from fastapi import FastAPI, Request
from fastapi.concurrency import iterate_in_threadpool
from fastapi.responses import JSONResponse
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from mangum import Mangum
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from organisations.app.router import organisation

crud_organisation_logger = Logger.get(service="crud_organisation_logger")

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


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)

            if response and response.status_code == STATUS_CODE_MAP["invalid"]:
                response_body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(iter(response_body))

                body_content = response_body[0].decode()
                crud_organisation_logger.log(
                    CrudApisLogBase.ORGANISATION_022,
                    error="Validation error",
                    error_message=body_content,
                )
            if response:
                return response
        except Exception as e:
            crud_organisation_logger.log(
                CrudApisLogBase.ORGANISATION_022,
                error="Middleware exception",
                error_message=str(e),
            )
            raise


app = FastAPI(title="Organisations API")
app.add_middleware(RequestLoggingMiddleware)
app.include_router(organisation.router)

handler = Mangum(app, lifespan="off")


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
