import uvicorn


def run() -> None:
    """
    Run the FastAPI application with Uvicorn server.
    """
    uvicorn.run("healthcare_service.app.handler_healthcare_service:app", host="0.0.0.0", port=7000, reload=True)

if __name__ == "__main__":
   run()
