"""CRUD API Mock FastAPI Application - Auto-generated."""

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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
                "issue": [
                    {
                        "severity": "error",
                        "code": "required",
                        "diagnostics": "identifier parameter required",
                    }
                ],
            },
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
                                    "value": ods_code,
                                }
                            ],
                            "active": org_data.get("active", True),
                            "name": org_data.get("name", "Test Organization"),
                        },
                        "search": {"mode": "match"},
                    }
                ],
            }

    # Organization not found - return empty bundle
    return {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []}


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
                "issue": [
                    {
                        "severity": "error",
                        "code": "invalid",
                        "diagnostics": "Invalid JSON body",
                    }
                ],
            },
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
                    "diagnostics": f"Organization {org_id} created/updated successfully",
                }
            ],
        },
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
                    "value": org.get("identifier_ODS_ODSCode", "UNKNOWN"),
                }
            ],
            "active": org.get("active", True),
            "name": org.get("name", "Test Organization"),
        }

    return JSONResponse(
        status_code=404,
        content={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "not-found",
                    "diagnostics": f"Organization {org_id} not found",
                }
            ],
        },
    )


@app.post("/oauth2/token")
async def oauth2_token(request: Request):
    """OAuth2 token endpoint - returns a mock access token."""
    return {
        "access_token": "mock-local-access-token-for-testing",
        "token_type": "Bearer",
        "expires_in": 3600,
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
                    "diagnostics": f"Endpoint not found: {request.method} /{path}",
                }
            ],
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
