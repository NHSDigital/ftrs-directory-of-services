from fastapi import FastAPI
from ftrs_common.api_middleware.correlation_id import CorrelationIdMiddleware
from ftrs_common.logger import Logger
from mangum import Mangum

from healthcare_service.app.router import healthcare

crud_healthcare_logger = Logger.get(service="crud_healthcare_logger")

app = FastAPI(title="Healthcare Services API", root_path="/healthcare-service")
app.add_middleware(CorrelationIdMiddleware)
app.include_router(healthcare.router)

handler = Mangum(app, lifespan="off")
