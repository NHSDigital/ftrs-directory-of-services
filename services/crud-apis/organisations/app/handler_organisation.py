from fastapi import FastAPI
from mangum import Mangum

from organisations.app.router import organisation

app = FastAPI(title="Organisations API", root_path="/Organization")
app.include_router(organisation.router)

handler = Mangum(app, lifespan="off")
