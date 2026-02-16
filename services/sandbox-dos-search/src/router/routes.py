import re
from copy import deepcopy
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.models.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from src.router.responses import (
    ERROR_INVALID_IDENTIFIER_SYSTEM,
    ERROR_INVALID_IDENTIFIER_VALUE,
    ERROR_MISSING_REVINCLUDE,
    SUCCESS_BUNDLE_ABC123,
)

router = APIRouter()


@router.get("/Organization")
async def get_organization(
    identifier: Optional[str] = Query(
        None,
        alias="identifier",
        description=f"ODS code in the format '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{{CODE}}' (FHIR search parameter)",
    ),
    revinclude: Optional[str] = Query(
        None,
        alias="_revinclude",
        description=f"Reverse include - must be '{REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}' for sandbox",
    ),
) -> JSONResponse:
    media = "application/fhir+json"

    error_content = None

    if not identifier:
        error_content = ERROR_INVALID_IDENTIFIER_VALUE
    elif revinclude != REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION:
        error_content = ERROR_MISSING_REVINCLUDE
    elif "|" not in identifier:
        error_content = ERROR_INVALID_IDENTIFIER_VALUE
    else:
        system, code = identifier.split("|", 1)
        if system != ODS_ORG_CODE_IDENTIFIER_SYSTEM:
            error_content = ERROR_INVALID_IDENTIFIER_SYSTEM
        elif not re.fullmatch(r"[A-Za-z0-9]{5,12}", code or ""):
            error_content = ERROR_INVALID_IDENTIFIER_VALUE
        elif code.upper() == "ABC123":
            bundle = deepcopy(SUCCESS_BUNDLE_ABC123)
            bundle["link"][0]["url"] = (
                "https://api.service.nhs.uk/FHIR/R4/Organization?"
                f"identifier={{system}}|{{code}}&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}"
            ).format(system=system, code=code)
            return JSONResponse(status_code=200, content=bundle, media_type=media)

    # Any path that reaches here represents an error content populated above
    return JSONResponse(
        status_code=400,
        content=error_content or ERROR_INVALID_IDENTIFIER_VALUE,
        media_type=media,
    )
