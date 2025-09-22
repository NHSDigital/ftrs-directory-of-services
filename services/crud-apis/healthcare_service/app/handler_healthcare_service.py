from fastapi import FastAPI
from mangum import Mangum

from healthcare_service.app.router import healthcare
from powertools_correlation_id import PowertoolsCorrelationIdMiddleware

app = FastAPI(title="Healthcare Services API", root_path="/healthcare-service")
app.add_middleware(PowertoolsCorrelationIdMiddleware)
app.include_router(healthcare.router)

handler = Mangum(app, lifespan="off")
