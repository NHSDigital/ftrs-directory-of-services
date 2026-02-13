import uvicorn

from fastapi import FastAPI
from ..router.routes import router as api_router
from starlette.responses import Response
from starlette.status import HTTP_200_OK

app = FastAPI()
app.include_router(api_router)


@app.get("/_status")
def status():
    return Response(status_code=HTTP_200_OK)

# Listening on 0.0.0.0 is intentional as the process will be running in a container. 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
