from fastapi import FastAPI
from ftrs_common.api_middleware.powertools_correlation_id import (
    PowertoolsCorrelationIdMiddleware,
)
from mangum import Mangum

from healthcare_service.app.router import healthcare

app = FastAPI(title="Healthcare Services API", root_path="/healthcare-service")
app.add_middleware(PowertoolsCorrelationIdMiddleware)
app.include_router(healthcare.router)

handler = Mangum(app, lifespan="off")
