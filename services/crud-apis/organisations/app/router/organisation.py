import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Path
from fastapi.responses import JSONResponse, Response
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import Organisation

from organisations.app.services.organisation_service import OrganisationService
from organisations.app.services.validators import (
    CreatePayloadValidator,
)
from utils.db_service import get_service_repository

ERROR_MESSAGE_404 = "Organisation not found"
FHIR_MEDIA_TYPE = "application/fhir+json"

router = APIRouter()
org_repository = get_service_repository(Organisation, "organisation")
crud_organisation_logger = Logger.get(service="crud_organisation_logger")
organisation_service = OrganisationService(
    org_repository=org_repository, logger=crud_organisation_logger
)


@router.get("/ods_code/{ods_code}", summary="Get an organisation by ODS code.")
def get_org_by_ods_code(
    ods_code: str,
) -> JSONResponse:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_001,
        ods_code=ods_code,
    )
    try:
        records = org_repository.get_by_ods_code(ods_code)
        if not records:
            crud_organisation_logger.log(
                CrudApisLogBase.ORGANISATION_002,
                ods_code=ods_code,
            )
            return JSONResponse(
                status_code=404,
                content=OperationOutcomeHandler.build(
                    diagnostics=ERROR_MESSAGE_404,
                    code="not-found",
                    severity="error",
                ),
                media_type=FHIR_MEDIA_TYPE,
            )
        return JSONResponse(
            status_code=200,
            content={"id": records[0]},
            media_type=FHIR_MEDIA_TYPE,
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=OperationOutcomeHandler.build(
                diagnostics=f"Unexpected error: {str(e)}",
                code="exception",
                severity="error",
            ),
            media_type=FHIR_MEDIA_TYPE,
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
    response_description="OperationOutcome",
)
def update_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
    fhir_org: dict = Body(..., media_type=FHIR_MEDIA_TYPE),
) -> JSONResponse:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_005,
        organisation_id=organisation_id,
    )
    try:
        processed = organisation_service.process_organisation_update(
            organisation_id=organisation_id,
            fhir_org=fhir_org,
        )
        if not processed:
            crud_organisation_logger.log(
                CrudApisLogBase.ORGANISATION_007,
                organisation_id=organisation_id,
            )
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No changes made to the organisation",
                },
                media_type=FHIR_MEDIA_TYPE,
            )
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Organisation updated successfully"},
            media_type=FHIR_MEDIA_TYPE,
        )
    except OperationOutcomeException as e:
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=e.outcome,
            media_type=FHIR_MEDIA_TYPE,
        )
    except Exception as e:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_019,
            organisation_id=organisation_id,
            error_message=str(e),
        )
        return JSONResponse(
            status_code=500,
            content=OperationOutcomeHandler.build(
                diagnostics=f"Unexpected error: {str(e)}",
                code="exception",
                severity="error",
            ),
            media_type=FHIR_MEDIA_TYPE,
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
    organisation = organisation_service.create_organisation(organisation)
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
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_404)

    org_repository.delete(organisation_id)
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_018,
        organisation_id=organisation_id,
    )

    return Response(status_code=204, content=None)
