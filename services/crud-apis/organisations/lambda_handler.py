from mangum import Mangum

from organisations.app import app

handler = Mangum(app, lifespan="off")
