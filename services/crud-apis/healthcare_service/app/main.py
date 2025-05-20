from fastapi import FastAPI
from healthcare_service.app.router import healthcare

app = FastAPI()
app.include_router(healthcare.router)
