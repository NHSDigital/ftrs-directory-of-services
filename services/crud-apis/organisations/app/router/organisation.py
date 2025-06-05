import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Body, Path
from fastapi.responses import JSONResponse
from ftrs_data_layer.models import Organisation

from organisations.app.services.organisation_helpers import (
    apply_updates,
    get_outdated_fields,
)
from organisations.app.services.validators import UpdatePayloadValidator
from utils.db_service import get_service_repository

router = APIRouter()
org_repository = get_service_repository(Organisation, "organisation")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@router.get("/ods_code/{ods_code}", summary="Get an organisation by ODS code.")
def get_org_by_ods_code(
    ods_code: str,
) -> JSONResponse:
    logging.info(f"Received request to get organisation with ODS code: {ods_code}")
    records = org_repository.get_by_ods_code(ods_code)

    if not records:
        logging.info(f"Organisation with ODS code {ods_code} not found.")
        raise HTTPException(status_code=404, detail="Organisation not found")

    logging.info(f"Organisation: {records}")
    return JSONResponse(status_code=200, content={"id": records[0]})


@router.get("/{organisation_id}", summary="Read a single organisation by id")
def get_organisation_by_id(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
) -> Organisation:
    logging.info(f"Received request to read organisation with ID: {organisation_id}")

    organisation = org_repository.get(organisation_id)

    if not organisation:
        logging.error(f"Organisation with ID {organisation_id} not found.")
        raise HTTPException(status_code=404, detail="Organisation not found")

    return organisation


@router.get("/", summary="Read all organisations")
def get_all_organisations(limit: int = 10) -> list[Organisation]:
    logging.info("Received request to read all organisations")
    organisations = list(org_repository.iter_records(max_results=limit))
    if not organisations:
        logging.error("Unable to retrieve any organisations.")
        raise HTTPException(
            status_code=404, detail="Unable to retrieve any organisations"
        )

    return organisations


@router.put("/{organisation_id}", summary="Update an organisation.")
def update_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
    payload: UpdatePayloadValidator = Body(...),
) -> dict:
    logging.info(f"Received request to update organisation with ID: {organisation_id}")
    organisation = org_repository.get(organisation_id)

    if not organisation:
        logging.error(f"Organisation with ID {organisation_id} not found.")
        raise HTTPException(status_code=404, detail="Organisation not found")

    outdated_fields = get_outdated_fields(organisation, payload)
    logging.info(
        f"Computed outdated fields: {outdated_fields} for organisation {organisation_id}"
    )

    if not outdated_fields:
        logging.info(f"No changes detected for organisation {organisation_id}.")
        return JSONResponse(status_code=200, content={"message": "No changes detected"})

    apply_updates(organisation, outdated_fields)
    org_repository.update(id, organisation)
    logging.info(f"Successfully updated organisation {organisation_id}")

    return JSONResponse(
        status_code=200, content={"message": "Data processed successfully"}
    )
