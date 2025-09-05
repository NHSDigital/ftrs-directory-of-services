from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse, Response
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.logbase import CrudApisLogBase

from organisations.app.models.organisation import OrganizationQueryParams
from organisations.app.services.organisation_service import OrganisationService
from organisations.app.services.validators import (
    CreatePayloadValidator,
    UpdatePayloadValidator,
)

ERROR_MESSAGE_404 = "Organisation not found"
FHIR_MEDIA_TYPE = "application/fhir+json"

router = APIRouter()
org_repository = get_service_repository(Organisation, "organisation")
crud_organisation_logger = Logger.get(service="crud_organisation_logger")
organisation_service = OrganisationService(
    org_repository=org_repository, logger=crud_organisation_logger
)
organisation_mapper = OrganizationMapper()


def _get_organization_query_params(
    identifier: str = Query(
        None,
        description="Organization identifier in format 'odsOrganisationCode|{code}'",
    ),
) -> OrganizationQueryParams | None:
    if identifier is None:
        return None
    return OrganizationQueryParams(identifier=identifier)


@router.get(
    "/Organization",
    summary="Get organisation uuid by ods_code or read all organisations",
    response_class=JSONResponse,
)
async def get_handle_organisation_requests(
    request: Request,
    organization_query_params: OrganizationQueryParams = Depends(
        _get_organization_query_params
    ),
) -> JSONResponse:
    """
    Returns a FHIR Bundle of Organisation(s) by ODS code or all if no identifier is provided.
    """
    try:
        organisation_service.check_organisation_params(request.query_params)
        if organization_query_params and organization_query_params.identifier:
            ods_code = organization_query_params.ods_code
            result = organisation_service.get_by_ods_code(ods_code)
        else:
            result = organisation_service.get_all_organisations()
        bundle = organisation_mapper.to_fhir_bundle(result)
        return JSONResponse(
            content=bundle.model_dump(mode="json"), media_type=FHIR_MEDIA_TYPE
        )
    except OperationOutcomeException:
        raise
    except Exception as e:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_021,
            error_message=str(e),
        )
        raise_fhir_exception(
            diagnostics="Unhandled exception occurred", code="exception"
        )


def raise_fhir_exception(diagnostics: str, code: str, severity: str = "error") -> None:
    outcome = OperationOutcomeHandler.build(
        diagnostics=diagnostics,
        code=code,
        severity=severity,
    )
    raise OperationOutcomeException(outcome)


@router.get(
    "/Organization/{organisation_id}", summary="Read a single organisation by id"
)
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


@router.put(
    "/Organization/{organisation_id}",
    summary="Update an organisation.",
    response_description="OperationOutcome",
)
def update_organisation(
    organisation_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the organisation",
    ),
    update_payload_validator: UpdatePayloadValidator = Body(
        ..., media_type=FHIR_MEDIA_TYPE
    ),
) -> JSONResponse:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_005,
        organisation_id=organisation_id,
    )
    try:
        processed = organisation_service.process_organisation_update(
            organisation_id=organisation_id,
            fhir_org=update_payload_validator.model_dump(),
        )
        if not processed:
            crud_organisation_logger.log(
                CrudApisLogBase.ORGANISATION_007,
                organisation_id=organisation_id,
            )
            outcome = OperationOutcomeHandler.build(
                diagnostics="No changes made to the organisation",
                code="information",
                severity="information",
            )
            return JSONResponse(
                status_code=200,
                content=outcome,
                media_type=FHIR_MEDIA_TYPE,
            )
        outcome = OperationOutcomeHandler.build(
            diagnostics="Organisation updated successfully",
            code="success",
            severity="information",
        )
        return JSONResponse(
            status_code=200,
            content=outcome,
            media_type=FHIR_MEDIA_TYPE,
        )
    except Exception as e:
        if not isinstance(e, OperationOutcomeException):
            crud_organisation_logger.log(
                CrudApisLogBase.ORGANISATION_019,
                organisation_id=organisation_id,
                error_message=str(e),
            )
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Unexpected error: {str(e)}",
                code="exception",
                severity="error",
            )
            raise OperationOutcomeException(outcome) from e
        raise


@router.post("/Organization", summary="Create a new organisation")
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


@router.delete("/Organization/{organisation_id}", summary="Delete an organisation")
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
