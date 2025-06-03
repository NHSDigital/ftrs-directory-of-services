from fastapi import FastAPI
from mangum import Mangum

from locations.app.router import locations

app = FastAPI()
app.include_router(locations.router)

handler = Mangum(app, lifespan="off")
