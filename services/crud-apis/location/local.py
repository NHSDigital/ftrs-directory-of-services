import uvicorn


def run() -> None:
    uvicorn.run(
        "location.app.handler_location:app",
        host="0.0.0.0",
        port=6000,
        reload=True,
    )
