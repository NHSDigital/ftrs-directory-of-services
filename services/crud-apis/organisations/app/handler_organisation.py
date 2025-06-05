from fastapi import FastAPI
from mangum import Mangum

import organisations.app.router.organisation as organisation

app = FastAPI()
app.include_router(organisation.router)

handler = Mangum(app, lifespan="off")
