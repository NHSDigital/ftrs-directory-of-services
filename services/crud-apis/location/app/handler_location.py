from fastapi import FastAPI
from ftrs_common.api_middleware.powertools_correlation_id import (
    PowertoolsCorrelationIdMiddleware,
)
from mangum import Mangum

from location.app.router import location

app = FastAPI(title="Location API", root_path="/location")
app.add_middleware(PowertoolsCorrelationIdMiddleware)
app.include_router(location.router)

handler = Mangum(app, lifespan="off")
