import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from src.router.routes import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

app.include_router(api_router)


@app.get("/_status")
def status() -> Response:
    return Response(status_code=HTTP_200_OK)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
