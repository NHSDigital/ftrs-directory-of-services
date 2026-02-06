"""Local server runner for DOS Search (Lambda Powertools APIGatewayRestResolver).

The DOS Search service uses AWS Lambda Powertools APIGatewayRestResolver.
We wrap it in a simple Flask/Starlette app for local testing.
"""

import os
import subprocess
import sys
import time
from typing import Optional

import requests


def run_dos_search_server(
    port: int = 8002,
    host: str = "127.0.0.1",
    endpoint_url: Optional[str] = None,
) -> subprocess.Popen:
    """Start the DOS Search server locally using the wrapper.

    Args:
        port: Port to run the server on
        host: Host to bind to
        endpoint_url: LocalStack endpoint URL for AWS services

    Returns:
        subprocess.Popen: The server process
    """
    # Create a temporary wrapper script
    _create_wrapper_script()

    dos_search_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "..",  # tests/service_automation
        "..",
        "..",  # repo root
        "services",
        "dos-search",
    )
    dos_search_path = os.path.abspath(dos_search_path)

    env = os.environ.copy()
    if endpoint_url:
        env["AWS_ENDPOINT_URL"] = endpoint_url
        env["ENDPOINT_URL"] = endpoint_url

    # Disable X-Ray tracing for local testing
    env["AWS_XRAY_SDK_ENABLED"] = "false"
    env["POWERTOOLS_TRACE_DISABLED"] = "true"

    # Use the dos-search venv python
    python_path = os.path.join(dos_search_path, ".venv", "bin", "python")
    if not os.path.exists(python_path):
        python_path = sys.executable

    process = subprocess.Popen(
        [
            python_path,
            "-m",
            "uvicorn",
            "local_server:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=dos_search_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    _wait_for_server(host, port, timeout=30)

    return process


def _create_wrapper_script() -> str:
    """Create a wrapper script that exposes the Lambda handler as an HTTP endpoint.

    Returns:
        Path to the created wrapper script
    """
    dos_search_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "..",
        "..",
        "..",
        "services",
        "dos-search",
    )
    dos_search_path = os.path.abspath(dos_search_path)

    wrapper_path = os.path.join(dos_search_path, "local_server.py")

    # Only create if it doesn't exist or is outdated
    wrapper_content = '''"""Local server wrapper for DOS Search Lambda function.

This wraps the AWS Lambda Powertools APIGatewayRestResolver in a FastAPI app
for local testing.
"""

import json
import os
import uuid

# Disable tracing before importing the handler
os.environ["AWS_XRAY_SDK_ENABLED"] = "false"
os.environ["POWERTOOLS_TRACE_DISABLED"] = "true"

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Import the Lambda handler
from functions.dos_search_ods_code_function import lambda_handler

app = FastAPI(title="DOS Search Local Server")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_lambda(request: Request, path: str) -> Response:
    """Proxy all requests to the Lambda handler."""
    # Build API Gateway event format
    body = await request.body()

    event = {
        "httpMethod": request.method,
        "path": f"/{path}",
        "headers": dict(request.headers),
        "queryStringParameters": dict(request.query_params) or None,
        "pathParameters": None,
        "body": body.decode("utf-8") if body else None,
        "isBase64Encoded": False,
        "requestContext": {
            "requestId": str(uuid.uuid4()),
            "stage": "local",
        },
    }

    # Mock Lambda context
    class MockContext:
        function_name = "dos-search-local"
        memory_limit_in_mb = 128
        invoked_function_arn = "test-function-arn-dos-search"
        aws_request_id = str(uuid.uuid4())

    # Call the Lambda handler
    result = lambda_handler(event, MockContext())

    # Parse the Lambda response
    status_code = result.get("statusCode", 200)
    headers = result.get("headers", {})
    response_body = result.get("body", "")

    return Response(
        content=response_body,
        status_code=status_code,
        headers=headers,
        media_type=headers.get("Content-Type", "application/json"),
    )


@app.get("/health")
async def health():
    return {"status": "healthy"}
'''

    with open(wrapper_path, "w") as f:
        f.write(wrapper_content)

    return wrapper_path


def _wait_for_server(host: str, port: int, timeout: int = 30) -> None:
    """Wait for the server to be ready."""
    start_time = time.time()
    url = f"http://{host}:{port}/health"

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
        process.wait(timeout=5)
