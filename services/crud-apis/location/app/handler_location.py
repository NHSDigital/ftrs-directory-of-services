from fastapi import FastAPI
from ftrs_common.api_middleware.correlation_id import CorrelationIdMiddleware
from ftrs_common.logger import Logger
from mangum import Mangum

from location.app.router import location

location_service_logger = Logger.get(service="crud_location_logger")

app = FastAPI(title="Location API", root_path="/location")
app.add_middleware(CorrelationIdMiddleware)
app.include_router(location.router)

handler = Mangum(app, lifespan="off")
