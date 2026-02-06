"""ODS Terminology API Mock Server for local testing.

This module provides a FastAPI server that mocks the NHS ODS Terminology API.
It returns canned FHIR Bundle responses based on the date parameter,
allowing different test scenarios to be triggered.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from loguru import logger

# Path to mock responses directory
MOCK_RESPONSES_DIR = Path(__file__).parent / "ods_mock_responses"

# Map of dates to scenarios (inverse of SCENARIO_DATE_MAP)
DATE_TO_SCENARIO = {
    "2025-12-08": "happy_path",
    "2025-12-09": "empty_payload",
    "2025-12-10": "invalid_data_types",
    "2025-12-11": "missing_required_fields",
    "2025-12-12": "extra_unexpected_field",
    "2025-12-14": "request_too_old",
    "2025-12-15": "unauthorized",
    "2025-12-16": "server_error",
    "2025-12-17": "unknown_resource_type",
    "2025-12-18": "missing_optional_fields",
    "2025-12-19": "invalid_odscode_format",
}


def get_mock_response(scenario: str) -> dict[str, Any]:
    """Get the mock response for a given scenario.

    Args:
        scenario: The scenario name

    Returns:
        Dict containing the response data and status code
    """
    response_file = MOCK_RESPONSES_DIR / f"{scenario}.json"

    if response_file.exists():
        with open(response_file) as f:
            data = json.load(f)
            return {
                "body": data.get("body", data),
                "status_code": data.get("status_code", 200),
            }

    # Default responses for scenarios without files
    default_responses = {
        "empty_payload": {
            "body": {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 0,
                "entry": [],
            },
            "status_code": 200,
        },
        "request_too_old": {
            "body": {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 0,
                "entry": [],
            },
            "status_code": 200,
        },
        "unauthorized": {
            "body": {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "security",
                        "diagnostics": "Unauthorized",
                    }
                ],
            },
            "status_code": 401,
        },
        "server_error": {
            "body": {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "exception",
                        "diagnostics": "Internal server error",
                    }
                ],
            },
            "status_code": 500,
        },
    }

    if scenario in default_responses:
        return default_responses[scenario]

    # Default: return empty bundle
    return {
        "body": {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "entry": [],
        },
        "status_code": 200,
    }


def _create_ods_mock_app_script() -> str:
    """Create the FastAPI app script for the ODS mock server.

    Returns:
        Path to the created script
    """
    script_dir = Path(__file__).parent
    app_script = script_dir / "ods_mock_app.py"

    script_content = '''"""FastAPI app for ODS Terminology API Mock Server."""

import json
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="ODS Terminology API Mock Server")

MOCK_RESPONSES_DIR = Path(__file__).parent / "ods_mock_responses"

DATE_TO_SCENARIO = {
    "2025-12-08": "happy_path",
    "2025-12-09": "empty_payload",
    "2025-12-10": "invalid_data_types",
    "2025-12-11": "missing_required_fields",
    "2025-12-12": "extra_unexpected_field",
    "2025-12-14": "request_too_old",
    "2025-12-15": "unauthorized",
    "2025-12-16": "server_error",
    "2025-12-17": "unknown_resource_type",
    "2025-12-18": "missing_optional_fields",
    "2025-12-19": "invalid_odscode_format",
}


def get_mock_response(scenario: str) -> dict[str, Any]:
    """Get the mock response for a given scenario."""
    response_file = MOCK_RESPONSES_DIR / f"{scenario}.json"

    if response_file.exists():
        with open(response_file) as f:
            data = json.load(f)
            return {
                "body": data.get("body", data),
                "status_code": data.get("status_code", 200),
            }

    default_responses = {
        "empty_payload": {
            "body": {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []},
            "status_code": 200,
        },
        "request_too_old": {
            "body": {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []},
            "status_code": 200,
        },
        "unauthorized": {
            "body": {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "security", "diagnostics": "Unauthorized"}]},
            "status_code": 401,
        },
        "server_error": {
            "body": {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": "exception", "diagnostics": "Internal server error"}]},
            "status_code": 500,
        },
    }

    if scenario in default_responses:
        return default_responses[scenario]

    return {"body": {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []}, "status_code": 200}


@app.get("/ORD/2-0-0/organisations")
@app.get("/fhir/Organization")
async def get_organizations(
    _lastUpdated: Optional[str] = Query(None),
    _count: Optional[int] = Query(1000),
    roleCode: Optional[List[str]] = Query(None),
):
    """Mock ODS Terminology API endpoint for fetching organizations."""
    scenario = DATE_TO_SCENARIO.get(_lastUpdated, "empty_payload")
    response_data = get_mock_response(scenario)

    status_code = response_data.get("status_code", 200)
    body = response_data.get("body", {})

    if status_code >= 400:
        return JSONResponse(content=body, status_code=status_code)

    return JSONResponse(content=body, status_code=200)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
'''

    with open(app_script, "w") as f:
        f.write(script_content)

    return str(app_script)


def run_ods_mock_server(
    port: int = 8003,
    host: str = "127.0.0.1",
) -> subprocess.Popen:
    """Start the ODS mock server locally.

    Args:
        port: Port to run the server on
        host: Host to bind to

    Returns:
        subprocess.Popen: The server process
    """
    # Create the app script
    _create_ods_mock_app_script()

    script_dir = Path(__file__).parent

    env = os.environ.copy()

    # Use the service_automation venv python
    venv_python = (
        Path(__file__).parent.parent.parent.parent.parent / ".venv" / "bin" / "python"
    )
    if venv_python.exists():
        python_path = str(venv_python)
    else:
        python_path = sys.executable

    logger.info(f"Starting ODS mock server with Python: {python_path}")

    process = subprocess.Popen(
        [
            python_path,
            "-m",
            "uvicorn",
            "ods_mock_app:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=str(script_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    _wait_for_server(host, port, timeout=30)

    logger.info(f"ODS mock server started at http://{host}:{port}")

    return process


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

    raise TimeoutError(f"ODS mock server did not start within {timeout} seconds")


def stop_server(process: subprocess.Popen) -> None:
    """Stop the server process."""
    if process:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        logger.info("ODS mock server stopped")
