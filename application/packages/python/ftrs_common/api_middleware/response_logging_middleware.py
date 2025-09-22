from ftrs_common.fhir.operation_outcome_status_mapper import STATUS_CODE_MAP
from ftrs_common.logbase import MiddlewareLogBase
from ftrs_common.logger import Logger
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

middleware_logger = Logger.get(service="common_middleware_logger")


class ResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP responses in the FTRS application.
    Logs error responses with their body content and status code,
    and logs successful responses with their status code.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        if response and response.status_code >= STATUS_CODE_MAP["structure"]:
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))

            body_content = (
                response_body[0].decode()
                if response_body and len(response_body) > 0
                else ""
            )
            middleware_logger.log(
                MiddlewareLogBase.MIDDLEWARE_001,
                status_code=response.status_code,
                error_message=body_content,
            )
            return response
        elif response and response.status_code < STATUS_CODE_MAP["structure"]:
            middleware_logger.log(
                MiddlewareLogBase.MIDDLEWARE_002,
                status_code=response.status_code,
            )
            return response

        return response
