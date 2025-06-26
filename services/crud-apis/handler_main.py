from fastapi import FastAPI
from mangum import Mangum

from organisations.app.router import organisation
from healthcare_service.app.router import healthcare

app = FastAPI(title="FTRS Services API")
app.include_router(organisation.router, prefix="/organisation", tags=["Organisation"])
app.include_router(healthcare.router, prefix="/healthcare-service", tags=["Healthcare"])

handler = Mangum(app, lifespan="off")
