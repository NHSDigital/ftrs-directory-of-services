import uvicorn
from fastapi import FastAPI
from ftrs_common.api_middleware.security_headers_middleware import (
    SecurityHeadersMiddleware,
)
from mangum import Mangum

from healthcare_service.app.router import healthcare
from location.app.router import location
from organisations.app.router import organisation

app = FastAPI(title="FTRS Services API")
app.add_middleware(SecurityHeadersMiddleware)
app.include_router(organisation.router, tags=["Organization"])
app.include_router(healthcare.router, prefix="/healthcare-service", tags=["Healthcare"])
app.include_router(location.router, prefix="/location", tags=["Location"])

handler = Mangum(app, lifespan="off")


def run() -> None:
    uvicorn.run(
        "handler_main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
    )
