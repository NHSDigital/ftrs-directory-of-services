from fastapi import FastAPI
from ftrs_common.api_middleware.powertools_correlation_id import (
    PowertoolsCorrelationIdMiddleware,
)
from mangum import Mangum

from healthcare_service.app.router import healthcare
from location.app.router import location
from organisations.app.router import organisation

app = FastAPI(title="FTRS Services API")
app.add_middleware(PowertoolsCorrelationIdMiddleware)
app.include_router(organisation.router, tags=["Organization"])
app.include_router(healthcare.router, prefix="/healthcare-service", tags=["Healthcare"])
app.include_router(location.router, prefix="/location", tags=["Location"])

handler = Mangum(app, lifespan="off")
