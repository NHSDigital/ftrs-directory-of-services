import uvicorn


def run() -> None:
    uvicorn.run(
        "organisations.app.handler_organisation:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
