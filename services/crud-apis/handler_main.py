from fastapi import FastAPI
from mangum import Mangum

from healthcare_service.app.router import healthcare
from location.app.router import location
from organisations.app.router import organisation

app = FastAPI(title="FTRS Services API")
app.include_router(organisation.router, prefix="/organisation", tags=["Organisation"])
app.include_router(healthcare.router, prefix="/healthcare-service", tags=["Healthcare"])
app.include_router(location.router, prefix="/location", tags=["Location"])

handler = Mangum(app, lifespan="off")
