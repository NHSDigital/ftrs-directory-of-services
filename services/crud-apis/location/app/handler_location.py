from fastapi import FastAPI
from mangum import Mangum

from location.app.router import location

app = FastAPI(title="Location API", root_path="/location")
app.include_router(location.router)

handler = Mangum(app, lifespan="off")
