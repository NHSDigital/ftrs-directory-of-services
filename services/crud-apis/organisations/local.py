import uvicorn


def run() -> None:
    uvicorn.run("organisations.app:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    run()
