from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any

from . import responses

router = APIRouter()

# Define a model for the POST request body (if needed)
class OrganizationUpdate(BaseModel):
    resourceType: str
    id: str
    active: bool
    name: str
    # Add other fields as needed based on your Organization schema

@router.get("/_status")
async def health_check():
    return {"status": "healthy"}

@router.get("/Organization")
async def search_organizations(
    identifier: str = Query(..., description="ODS code in the format 'odsOrganizationCode|{CODE}'")
):
    if not identifier.startswith("odsOrganisationCode|"):
        return JSONResponse(
            status_code=422,
            content=responses.INVALID_IDENTIFIER_SYSTEM_RESPONSE
        )

    try:
        system, value = identifier.split("|")
        ods_code = value.strip()
    except ValueError:
        return JSONResponse(
            status_code=422,
            content=responses.INVALID_IDENTIFIER_VALUE_RESPONSE
        )

    if len(ods_code) < 5 or len(ods_code) > 12 or not ods_code.isalnum():
        return JSONResponse(
            status_code=400,
            content=responses.INVALID_IDENTIFIER_VALUE_RESPONSE
        )

    if ods_code == "ABC123":
        return responses.GET_SUCCESS_RESPONSE

    if ods_code == "DEF456":
        return JSONResponse(
            status_code=404,
            content=responses.GET_NOT_FOUND_RESPONSE
        )

    if ods_code == "GHI789":
        return JSONResponse(
            status_code=500,
            content=responses.INTERNAL_SERVER_ERROR_RESPONSE
        )

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": []
    }

@router.put("/Organization/{organization_id}")
async def update_organization(
    organization_id: str,
    organization_data: Dict[str, Any]  # Or use OrganizationUpdate model if you want validation
):

    if organization_id == "87c5f637-cca3-4ddd-97a9-a3f6e6746bbe":
        return JSONResponse(
            status_code=200,
            content=responses.PUT_SUCCESS_RESPONSE
        )

    elif organization_id == "not-found-id":
        return JSONResponse(
            status_code=404,
            content=responses.PUT_NOT_FOUND_RESPONSE
        )
