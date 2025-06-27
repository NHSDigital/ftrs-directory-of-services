import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.params import Body, Path
from fastapi.responses import JSONResponse, Response
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import Organisation

from organisations.app.models.operation_outcomes import operation_outcome
from organisations.app.services.organisation_helpers import (
    process_organisation_update,
    create_organisation,
)
from organisations.app.services.validators import (
    CreatePayloadValidator,
    UpdatePayloadValidator,
)
from utils.db_service import get_service_repository

ERROR_MESSAGE_404 = "Organisation not found"

router = APIRouter()
org_repository = get_service_repository(Organisation, "organisation")

crud_organisation_logger = Logger.get(service="crud_organisation_logger")

@router.get("/ods_code/{ods_code}", summary="Get an organisation by ODS code.")
def get_org_by_ods_code(
    ods_code: str,
) -> JSONResponse:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_001,
        ods_code=ods_code,
    )
    records = org_repository.get_by_ods_code(ods_code)

    if not records:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_002,
            ods_code=ods_code,
        )
        return operation_outcome(
            "Organisation not found", code="not-found",  severity="error", status_code=404
        )
    org = records[0]
    return JSONResponse(
        status_code=200,
        content=org.to_fhir(),
        media_type="application/fhir+json",
    )


@router.get("/{organisation_id}", summary="Read a single organisation by id")
def get_organisation_by_id(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
) -> Organisation:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_003,
        organisation_id=organisation_id,
    )
    organisation = org_repository.get(organisation_id)

    if not organisation:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_009,
            organisation_id=organisation_id,
        )
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_404)

    return organisation


@router.get("/", summary="Read all organisations")
def get_all_organisations(limit: int = 10) -> list[Organisation]:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_004,
    )
    organisations = list(org_repository.iter_records(max_results=limit))
    if not organisations:
        logging.error("Unable to retrieve any organisations.")
        raise HTTPException(
            status_code=404, detail="Unable to retrieve any organisations"
        )

    return organisations


@router.put(
    "/{organisation_id}",
    summary="Update an organisation.",
    response_model=JSONResponse,
    response_description="OperationOutcome",
)
def update_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
    fhir_org: dict = Body(..., media_type="application/fhir+json")
) -> dict:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_005,
        organisation_id=organisation_id,
    )
    try:
        process_organisation_update(
            organisation_id=organisation_id,
            fhir_org=fhir_org,
            org_repository=org_repository,
            logger=crud_organisation_logger,
        )
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Organisation updated successfully"},
        )
    except OperationOutcomeException as e:
        return JSONResponse(
            status_code=e.outcome.status_code,
            content=e.outcome,
            media_type="application/fhir+json",
        )
    except Exception as e:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_006,
            organisation_id=organisation_id,
            error=str(e),
        )
        outcome = OperationOutcomeHandler.from_exception(
            exc=e,
        )
        return JSONResponse(
            status_code=500,
            content=outcome,
            media_type="application/fhir+json",
        )

@router.post("/", summary="Create a new organisation")
def post_organisation(
    organisation_data: CreatePayloadValidator = Body(
        ...,
        examples=[
            {
                "summary": "Create a new organisation",
                "value": {
                    "identifier_ODS_ODSCode": "ABC123",
                    "active": True,
                    "name": "Test Organisation",
                    "telecom": "12345",
                    "type": "Test Type",
                    "endpoints": [],
                },
            }
        ],
    ),
) -> JSONResponse:
    organisation = Organisation(**organisation_data.model_dump())
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_011,
        ods_code=organisation.identifier_ODS_ODSCode,
    )
    organisation = create_organisation(organisation, org_repository)
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_015,
        ods_code=organisation.identifier_ODS_ODSCode,
        organisation_id=organisation.id,
    )
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={
            "message": "Organisation created successfully",
            "organisation": organisation.model_dump(mode="json"),
        },
    )


@router.delete("/{organisation_id}", summary="Delete an organisation")
def delete_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
) -> Response:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_017,
        organisation_id=organisation_id,
    )
    organisation = org_repository.get(organisation_id)

    if not organisation:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_010,
            organisation_id=organisation_id,
        )
        raise HTTPException(status_code=404, detail="Organisation not found")

    org_repository.delete(organisation_id)
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_018,
        organisation_id=organisation_id,
    )

    return Response(status_code=204, content=None)
