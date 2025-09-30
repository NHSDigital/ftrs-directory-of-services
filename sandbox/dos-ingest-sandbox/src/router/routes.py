from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from . import responses

router = APIRouter()

@router.get("/_status")
async def health_check():
    return {"status": "healthy"}

@router.get("/Organization")
async def search_organizations(
    identifier: str = Query(..., description="ODS code in the format 'odsOrganizationCode|{CODE}'")
):
    if not identifier.startswith("odsOrganisationCode|"):
        return JSONResponse(
            status_code=400,
            content=responses.INVALID_IDENTIFIER_SYSTEM_RESPONSE
        )

    try:
        system, value = identifier.split("|")
        ods_code = value.strip()
    except ValueError:
        return JSONResponse(
            status_code=400,
            content=responses.INVALID_IDENTIFIER_VALUE_RESPONSE
        )

    if len(ods_code) < 5 or len(ods_code) > 12 or not ods_code.isalnum():
        return JSONResponse(
            status_code=400,
            content=responses.INVALID_IDENTIFIER_VALUE_RESPONSE
        )

    if ods_code == "ABC123":
        return responses.SUCCESS_RESPONSE

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": []
    }
