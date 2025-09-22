from fastapi import FastAPI
from mangum import Mangum

from location.app.router import location
from powertools_correlation_id import PowertoolsCorrelationIdMiddleware

app = FastAPI(title="Location API", root_path="/location")
app.add_middleware(PowertoolsCorrelationIdMiddleware)
app.include_router(location.router)

handler = Mangum(app, lifespan="off")
