from fastapi import FastAPI
from mangum import Mangum

from healthcare_service.app.router import healthcare

app = FastAPI()
app.include_router(healthcare.router)

handler = Mangum(app, lifespan="off")
