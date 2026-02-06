"""Local server runner for CRUD APIs (FastAPI with Mangum).

The CRUD APIs service is a FastAPI app wrapped with Mangum for Lambda.
We can run it directly with uvicorn for local testing.
"""

import os
import subprocess
import sys
import time
from typing import Optional

import requests
from loguru import logger


def run_crud_apis_server(
    port: int = 8002,
    host: str = "127.0.0.1",
    endpoint_url: Optional[str] = None,
) -> subprocess.Popen:
    """Start the CRUD APIs FastAPI server locally.

    Args:
        port: Port to run the server on
        host: Host to bind to
        endpoint_url: LocalStack endpoint URL for AWS services

    Returns:
        subprocess.Popen: The server process
    """
    # Navigate from local_servers/ -> utilities/ -> tests/ -> service_automation/ -> tests/ -> repo root
    crud_apis_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "..",  # up to repo root
        "services",
        "crud-apis",
    )
    crud_apis_path = os.path.abspath(crud_apis_path)

    # Build environment for LocalStack
    env = os.environ.copy()

    # AWS / LocalStack configuration
    if endpoint_url:
        env["AWS_ENDPOINT_URL"] = endpoint_url
        env["ENDPOINT_URL"] = endpoint_url
    else:
        endpoint_url = env.get("AWS_ENDPOINT_URL", "http://localhost:4566")
        env["AWS_ENDPOINT_URL"] = endpoint_url
        env["ENDPOINT_URL"] = endpoint_url

    # Set required environment variables for CRUD APIs
    # Use direct assignment to ensure these are set correctly
    env["PROJECT_NAME"] = env.get("PROJECT_NAME", "ftrs-dos")
    env["ENVIRONMENT"] = env.get("ENVIRONMENT", "local")
    env["WORKSPACE"] = env.get("WORKSPACE", "test")
    env["AWS_DEFAULT_REGION"] = "eu-west-2"
    env["AWS_REGION"] = "eu-west-2"
    env["AWS_ACCESS_KEY_ID"] = env.get("AWS_ACCESS_KEY_ID", "test")
    env["AWS_SECRET_ACCESS_KEY"] = env.get("AWS_SECRET_ACCESS_KEY", "test")

    # Disable X-Ray tracing for local tests
    env["AWS_XRAY_SDK_ENABLED"] = "false"
    env["POWERTOOLS_TRACE_DISABLED"] = "true"

    # Try to find Python interpreter
    # First try the crud-apis venv
    python_path = os.path.join(crud_apis_path, ".venv", "bin", "python")
    if not os.path.exists(python_path):
        # Try shared venv
        shared_venv = os.path.join(
            os.path.dirname(crud_apis_path), ".venv", "bin", "python"
        )
        if os.path.exists(shared_venv):
            python_path = shared_venv
        else:
            # Fall back to system Python
            python_path = sys.executable

    print(f"[CRUD APIs Server] Starting using Python: {python_path}")
    print(f"[CRUD APIs Server] CRUD APIs path: {crud_apis_path}")
    print(f"[CRUD APIs Server] Endpoint URL: {endpoint_url}")
    print(f"[CRUD APIs Server] Environment ENDPOINT_URL: {env.get('ENDPOINT_URL')}")
    print(
        f"[CRUD APIs Server] Environment AWS_ENDPOINT_URL: {env.get('AWS_ENDPOINT_URL')}"
    )
    logger.info(f"Starting CRUD APIs server using Python: {python_path}")
    logger.info(f"CRUD APIs path: {crud_apis_path}")
    logger.info(f"Endpoint URL: {endpoint_url}")
    logger.info(f"Environment ENDPOINT_URL: {env.get('ENDPOINT_URL')}")
    logger.info(f"Environment AWS_ENDPOINT_URL: {env.get('AWS_ENDPOINT_URL')}")

    process = subprocess.Popen(
        [
            python_path,
            "-m",
            "uvicorn",
            "handler_main:app",
            "--host",
            host,
            "--port",
            str(port),
            "--log-level",
            "info",
        ],
        cwd=crud_apis_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout for easier debugging
    )

    # Wait for server to be ready
    try:
        _wait_for_server(host, port, timeout=30)
        print(f"[CRUD APIs Server] Server started at http://{host}:{port}")
        logger.info(f"CRUD APIs server started at http://{host}:{port}")
    except TimeoutError:
        # Log any stderr output for debugging
        stdout_output = ""
        if process.stdout:
            try:
                stdout_output = process.stdout.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        print(f"[CRUD APIs Server] Failed to start. stdout: {stdout_output[:2000]}")
        logger.error(
            f"CRUD APIs server failed to start. stdout: {stdout_output[:2000]}"
        )
        stop_server(process)
        raise

    return process


def _wait_for_server(host: str, port: int, timeout: int = 30) -> None:
    """Wait for the server to be ready."""
    start_time = time.time()
    url = f"http://{host}:{port}/docs"  # FastAPI docs endpoint

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)

    raise TimeoutError(f"Server did not start within {timeout} seconds")


def stop_server(process: subprocess.Popen) -> None:
    """Stop the server process."""
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)
        logger.info("CRUD APIs server stopped")
