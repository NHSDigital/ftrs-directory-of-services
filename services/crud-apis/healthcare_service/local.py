import uvicorn


def run() -> None:
    uvicorn.run(
        "healthcare_service.app.handler_healthcare_service:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
    )
