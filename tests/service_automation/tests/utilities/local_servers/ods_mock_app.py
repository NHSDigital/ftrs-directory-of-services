"""FastAPI app for ODS Terminology API Mock Server."""

import json
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, Query
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

    return {
        "body": {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "entry": [],
        },
        "status_code": 200,
    }


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
