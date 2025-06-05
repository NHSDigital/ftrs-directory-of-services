from fastapi import FastAPI
from mangum import Mangum

from healthcare_service.app.router import healthcare

app = FastAPI(title="Healthcare Services API", root_path="/healthcare-service")
app.include_router(healthcare.router)

handler = Mangum(app, lifespan="off")
