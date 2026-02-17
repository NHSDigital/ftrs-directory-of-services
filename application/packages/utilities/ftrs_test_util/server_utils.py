import socket
from contextlib import contextmanager
import uvicorn
import threading
from fastapi import FastAPI
from typing import Generator
import signal


def get_available_port() -> int:
    """Find an available port on the host machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # Bind to an available port assigned by the OS
        return s.getsockname()[1]  # Return the assigned port number


@contextmanager
def run_server(app: FastAPI | str) -> Generator[str, None, None]:
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=get_available_port(),
    )
    dev_server = uvicorn.Server(config)

    # Start the server in a separate thread
    thread = threading.Thread(target=dev_server.run)
    thread.start()

    # Wait for the server to start
    while not dev_server.started:
        pass

    try:
        yield f"http://{config.host}:{config.port}"
    finally:
        # Shutdown the server after tests are done
        dev_server.handle_exit(sig=signal.SIGINT, frame=None)
        thread.join(timeout=5)
