import re
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.models.constants import MEDIA_TYPE, ODS_ORG_CODE_IDENTIFIER_SYSTEM
from src.router.responses import (
    ERROR_INTERNAL_SERVER,
    ERROR_INVALID_IDENTIFIER_SYSTEM,
    ERROR_INVALID_IDENTIFIER_VALUE,
    ERROR_MISSING_IDENTIFIER_SEPARATOR,
    ERROR_NOT_FOUND,
    PUT_NOT_FOUND_RESPONSE,
    PUT_SUCCESS_RESPONSE,
    SUCCESS_BUNDLE_ABC123,
)

router = APIRouter()


@router.get("/_status")
async def health_check() -> dict[str, str]:
    """Health check endpoint for container monitoring."""
    return {"status": "healthy"}


@router.get("/Organization")
async def get_organization(
    identifier: str = Query(
        ...,
        alias="identifier",
        description=f"ODS code in the format '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{{CODE}}' (FHIR search parameter)",
    ),
) -> JSONResponse:
    """Search for organisations by ODS code identifier.

    Returns a FHIR Bundle containing matching Organization resources.
    """
    # Check for missing separator
    if "|" not in identifier:
        return JSONResponse(
            status_code=400,
            content=ERROR_MISSING_IDENTIFIER_SEPARATOR,
            media_type=MEDIA_TYPE,
        )

    # Parse system and code
    parts = identifier.split("|", 1)
    system = parts[0]
    code = parts[1] if len(parts) > 1 else ""

    # Validate system
    if system != ODS_ORG_CODE_IDENTIFIER_SYSTEM:
        return JSONResponse(
            status_code=400,
            content=ERROR_INVALID_IDENTIFIER_SYSTEM,
            media_type=MEDIA_TYPE,
        )

    # Validate ODS code format (1-12 alphanumeric characters)
    if not re.fullmatch(r"[A-Za-z0-9]{1,12}", code or ""):
        return JSONResponse(
            status_code=400,
            content=ERROR_INVALID_IDENTIFIER_VALUE,
            media_type=MEDIA_TYPE,
        )

    # Canned response for ABC123 - success
    if code.upper() == "ABC123":
        return JSONResponse(
            status_code=200,
            content=SUCCESS_BUNDLE_ABC123,
            media_type=MEDIA_TYPE,
        )

    # Canned response for DEF456 - not found
    if code.upper() == "DEF456":
        return JSONResponse(
            status_code=404,
            content=ERROR_NOT_FOUND,
            media_type=MEDIA_TYPE,
        )

    # Canned response for GHI789 - internal server error
    if code.upper() == "GHI789":
        return JSONResponse(
            status_code=500,
            content=ERROR_INTERNAL_SERVER,
            media_type=MEDIA_TYPE,
        )

    # Default: return empty bundle for unknown codes
    return JSONResponse(
        status_code=200,
        content={
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [],
        },
        media_type=MEDIA_TYPE,
    )


@router.put("/Organization/{organization_id}")
async def update_organization(
    organization_id: str,
    organization_data: dict[str, Any],
) -> JSONResponse:
    """Update/overwrite an organization resource by ID.

    Returns an OperationOutcome indicating success or failure.
    """
    # Canned response for success (specific ID)
    if organization_id == "87c5f637-cca3-4ddd-97a9-a3f6e6746bbe":
        return JSONResponse(
            status_code=200,
            content=PUT_SUCCESS_RESPONSE,
            media_type=MEDIA_TYPE,
        )

    # Canned response for not found
    if organization_id == "not-found-id":
        return JSONResponse(
            status_code=404,
            content=PUT_NOT_FOUND_RESPONSE,
            media_type=MEDIA_TYPE,
        )

    # Default: return success for any other ID (stateless sandbox)
    return JSONResponse(
        status_code=200,
        content=PUT_SUCCESS_RESPONSE,
        media_type=MEDIA_TYPE,
    )
