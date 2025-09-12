from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_406_NOT_ACCEPTABLE, HTTP_415_UNSUPPORTED_MEDIA_TYPE

MEDIA_TYPE = "application/fhir+json"


class FHIRContentTypeMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method == "PUT":
            content_type = request.headers.get("content-type", "")
            if content_type.strip().lower() != MEDIA_TYPE:
                return Response(
                    content='{"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "unsupported-media-type", "diagnostics": "PUT requests must have Content-Type \'application/fhir+json\'"}]}',
                    status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    media_type=MEDIA_TYPE,
                )
        return await call_next(request)


class FHIRAcceptHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method == "GET":
            accept = request.headers.get("accept", "")
            if MEDIA_TYPE not in accept.lower():
                return Response(
                    content='{"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "not-acceptable", "diagnostics": "GET requests must have Accept \'application/fhir+json\'"}]}',
                    status_code=HTTP_406_NOT_ACCEPTABLE,
                    media_type=MEDIA_TYPE,
                )
        return await call_next(request)
