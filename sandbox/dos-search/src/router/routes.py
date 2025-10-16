from typing import Optional
import re

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .responses import (
    SUCCESS_BUNDLE_ABC123,
    ERROR_INVALID_IDENTIFIER_VALUE,
    ERROR_INVALID_IDENTIFIER_SYSTEM,
    ERROR_MISSING_REVINCLUDE,
)

router = APIRouter()


@router.get("/Organization")
async def get_organization(
    identifier: Optional[str] = Query(
        None,
        alias="identifier",
        description="ODS code in the format 'odsOrganisationCode|{CODE}' (FHIR search parameter)",
    ),
    revinclude: Optional[str] = Query(
        None,
        alias="_revinclude",
        description="Reverse include - must be 'Endpoint:organization' for sandbox",
    ),
):
    # Supported permutations per spec/examples:
    # 1) identifier=odsOrganisationCode|ABC123&_revinclude=Endpoint:organization -> 200
    # 2) identifier=foo|ABC123&_revinclude=Endpoint:organization -> 400 invalid-identifier-system
    # 3) identifier=odsOrganisationCode|ABC&_revinclude=Endpoint:organization -> 400 invalid-identifier-value
    # 4) identifier=odsOrganisationCode|ABC123 (missing _revinclude) -> 400 missing-revinclude

    media = "application/fhir+json"

    # identifier must be provided
    if not identifier:
        return JSONResponse(status_code=400, content=ERROR_INVALID_IDENTIFIER_VALUE, media_type=media)

    # Require _revinclude exact value
    if revinclude != "Endpoint:organization":
        return JSONResponse(status_code=400, content=ERROR_MISSING_REVINCLUDE, media_type=media)

    # Expect format system|value
    if "|" not in identifier:
        return JSONResponse(status_code=400, content=ERROR_INVALID_IDENTIFIER_VALUE, media_type=media)

    system, code = identifier.split("|", 1)

    # Strictly accept only 'odsOrganisationCode' per spec
    if system != "odsOrganisationCode":
        return JSONResponse(status_code=400, content=ERROR_INVALID_IDENTIFIER_SYSTEM, media_type=media)

    # Validate code length/pattern 5-12 alphanumeric
    if not re.fullmatch(r"[A-Za-z0-9]{5,12}", code or ""):
        return JSONResponse(status_code=400, content=ERROR_INVALID_IDENTIFIER_VALUE, media_type=media)

    # Success response example for ABC123 - return static bundle but set the self link explicitly
    if code == "ABC123":
        from copy import deepcopy
        bundle = deepcopy(SUCCESS_BUNDLE_ABC123)
        bundle["link"][0]["url"] = (
            "https://api.service.nhs.uk/FHIR/R4/Organization?"
            "identifier={system}|{code}&_revinclude=Endpoint:organization"
        ).format(system=system, code=code)
        return JSONResponse(status_code=200, content=bundle, media_type=media)

    # Any other ODS code not modelled -> treat as invalid value for sandbox
    return JSONResponse(status_code=400, content=ERROR_INVALID_IDENTIFIER_VALUE, media_type=media)
