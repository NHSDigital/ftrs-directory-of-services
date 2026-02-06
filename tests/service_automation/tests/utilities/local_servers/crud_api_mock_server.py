"""CRUD API Mock Server for local ETL ODS testing.

This module provides a FastAPI server that mocks the FTRS CRUD APIs.
It handles Organization PUT requests and returns appropriate FHIR responses.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from loguru import logger

# Store created organizations in memory for testing
ORGANIZATIONS_STORE: dict[str, dict] = {}


def create_crud_api_app_code() -> str:
    """Generate the FastAPI app code for the CRUD API mock server."""
    return '''
"""CRUD API Mock FastAPI Application - Auto-generated."""
import json
import uuid
from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI(title="CRUD API Mock Server")

# In-memory store for organizations - pre-seeded with test data
organizations: dict[str, dict] = {
    "a12345-uuid-1234-5678-abcdef012345": {
        "identifier_ODS_ODSCode": "A12345",
        "name": "Test Organization A12345",
        "active": True,
    },
    "b67890-uuid-1234-5678-abcdef012345": {
        "identifier_ODS_ODSCode": "B67890",
        "name": "Test Organization B67890",
        "active": True,
    },
}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/Organization")
async def get_organization(
    request: Request,
    identifier: Optional[str] = None,
):
    """Get organization by identifier (ODS code lookup)."""
    if not identifier:
        return JSONResponse(
            status_code=400,
            content={
                "resourceType": "OperationOutcome",
                "issue": [{"severity": "error", "code": "required", "diagnostics": "identifier parameter required"}]
            }
        )

    # Parse the identifier (format: odsOrganisationCode|CODE)
    ods_code = None
    if "|" in identifier:
        parts = identifier.split("|")
        if len(parts) >= 2:
            ods_code = parts[1]
    else:
        ods_code = identifier

    # Look up organization by ODS code
    for org_id, org_data in organizations.items():
        if org_data.get("identifier_ODS_ODSCode") == ods_code:
            return {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 1,
                "entry": [
                    {
                        "fullUrl": f"https://localhost/FHIR/R4/Organization/{org_id}",
                        "resource": {
                            "resourceType": "Organization",
                            "id": org_id,
                            "identifier": [
                                {
                                    "use": "official",
                                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                                    "value": ods_code
                                }
                            ],
                            "active": org_data.get("active", True),
                            "name": org_data.get("name", "Test Organization")
                        },
                        "search": {"mode": "match"}
                    }
                ]
            }

    # Organization not found - return empty bundle
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": []
    }

@app.put("/Organization/{org_id}")
async def put_organization(
    org_id: str,
    request: Request,
):
    """Create or update an organization."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "resourceType": "OperationOutcome",
                "issue": [{"severity": "error", "code": "invalid", "diagnostics": "Invalid JSON body"}]
            }
        )

    # Store the organization
    body["id"] = org_id
    organizations[org_id] = body

    # Return success response
    return JSONResponse(
        status_code=200,
        content={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "information",
                    "code": "informational",
                    "diagnostics": f"Organization {org_id} created/updated successfully"
                }
            ]
        }
    )

@app.get("/Organization/{org_id}")
async def get_organization_by_id(org_id: str):
    """Get organization by ID."""
    if org_id in organizations:
        org = organizations[org_id]
        return {
            "resourceType": "Organization",
            "id": org_id,
            "identifier": [
                {
                    "use": "official",
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": org.get("identifier_ODS_ODSCode", "UNKNOWN")
                }
            ],
            "active": org.get("active", True),
            "name": org.get("name", "Test Organization")
        }

    return JSONResponse(
        status_code=404,
        content={
            "resourceType": "OperationOutcome",
            "issue": [{"severity": "error", "code": "not-found", "diagnostics": f"Organization {org_id} not found"}]
        }
    )

@app.post("/oauth2/token")
async def oauth2_token(request: Request):
    """OAuth2 token endpoint - returns a mock access token."""
    return {
        "access_token": "mock-local-access-token-for-testing",
        "token_type": "Bearer",
        "expires_in": 3600
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(path: str, request: Request):
    """Catch-all endpoint for debugging."""
    return JSONResponse(
        status_code=404,
        content={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "not-found",
                    "diagnostics": f"Endpoint not found: {request.method} /{path}"
                }
            ]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
'''


def run_crud_api_mock_server(
    port: int = 8081,
    host: str = "127.0.0.1",
) -> dict[str, Any]:
    """Start the CRUD API mock server.

    Args:
        port: Port to run the server on
        host: Host to bind to

    Returns:
        Dict with server info (process, url)
    """
    # Create the app file
    app_file = Path(__file__).parent / "crud_api_mock_app.py"
    app_code = create_crud_api_app_code()

    with open(app_file, "w") as f:
        f.write(app_code)

    logger.info(f"Starting CRUD API mock server on {host}:{port}")

    # Start the server as a subprocess
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "crud_api_mock_app:app",
            "--host",
            host,
            "--port",
            str(port),
        ],
        cwd=str(app_file.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    url = f"http://{host}:{port}"
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=1)
            if response.status_code == 200:
                logger.info(f"CRUD API mock server ready at {url}")
                return {
                    "process": process,
                    "url": url,
                    "port": port,
                    "host": host,
                }
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(0.2)

    # Server didn't start
    process.terminate()
    raise RuntimeError(
        f"CRUD API mock server failed to start after {max_retries} retries"
    )


def stop_server(server_info: dict[str, Any]) -> None:
    """Stop the CRUD API mock server.

    Args:
        server_info: Dict with server process info
    """
    process = server_info.get("process")
    if process:
        logger.info("Stopping CRUD API mock server")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        logger.info("CRUD API mock server stopped")
