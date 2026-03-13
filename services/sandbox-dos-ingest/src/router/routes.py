import re
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.models.constants import MEDIA_TYPE, ODS_ORG_CODE_IDENTIFIER_SYSTEM
from src.router.responses import (
    ERROR_INTERNAL_SERVER,
    ERROR_MISSING_IDENTIFIER,
    ERROR_MISSING_IDENTIFIER_SEPARATOR,
    PUT_NOT_FOUND_RESPONSE,
    PUT_SUCCESS_RESPONSE,
    PUT_VALIDATION_ERROR_RESPONSE,
    SUCCESS_BUNDLE_ABC123,
    build_invalid_identifier_system_error,
    build_invalid_identifier_value_error,
    build_not_found_error,
)

router = APIRouter()


@router.get("/Organization")
async def get_organization(
    identifier: str | None = Query(
        default=None,
        alias="identifier",
        description=f"ODS code in the format '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{{CODE}}' (FHIR search parameter)",
    ),
) -> JSONResponse:
    """Search for organisations by ODS code identifier.

    Returns a FHIR Bundle containing matching Organization resources.
    """
    # Check for missing identifier
    if identifier is None:
        return JSONResponse(
            status_code=400,
            content=ERROR_MISSING_IDENTIFIER,
            media_type=MEDIA_TYPE,
        )

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
            content=build_invalid_identifier_system_error(system),
            media_type=MEDIA_TYPE,
        )

    # Validate ODS code format (1-12 alphanumeric characters)
    if not re.fullmatch(r"[A-Za-z0-9]{1,12}", code or ""):
        return JSONResponse(
            status_code=400,
            content=build_invalid_identifier_value_error(code),
            media_type=MEDIA_TYPE,
        )

    # Canned response for ABC123 - success (found organization)
    if code.upper() == "ABC123":
        return JSONResponse(
            status_code=200,
            content=SUCCESS_BUNDLE_ABC123,
            media_type=MEDIA_TYPE,
        )

    # Canned response for GHI789 - internal server error (demo)
    if code.upper() == "GHI789":
        return JSONResponse(
            status_code=500,
            content=ERROR_INTERNAL_SERVER,
            media_type=MEDIA_TYPE,
        )

    # Default: return 404 for any other ODS code (matches CRUD API behavior)
    return JSONResponse(
        status_code=404,
        content=build_not_found_error(code.upper()),
        media_type=MEDIA_TYPE,
    )


@router.put("/Organization/{organization_id}")
async def update_organization(
    organization_id: str,
    organization_data: dict[str, Any],
) -> JSONResponse:
    """Update/overwrite an organization resource by ID.

    Returns an OperationOutcome indicating success or failure.

    Sandbox trigger IDs:
    - 04393ec4-198f-42dd-9507-f4fa5e9ebf96 → 200 Success (matches GET response)
    - trigger-422-validation-error → 422 Validation Error
    - Any other ID → 404 Not Found
    """
    if organization_id == "04393ec4-198f-42dd-9507-f4fa5e9ebf96":
        return JSONResponse(
            status_code=200,
            content=PUT_SUCCESS_RESPONSE,
            media_type=MEDIA_TYPE,
        )

    if organization_id == "trigger-422-validation-error":
        return JSONResponse(
            status_code=422,
            content=PUT_VALIDATION_ERROR_RESPONSE,
            media_type=MEDIA_TYPE,
        )

    return JSONResponse(
        status_code=404,
        content=PUT_NOT_FOUND_RESPONSE,
        media_type=MEDIA_TYPE,
    )
