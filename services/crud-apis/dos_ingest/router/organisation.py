from http import HTTPStatus
from typing import Annotated
from uuid import UUID, uuid4

from dos_ingest.dependencies import LoggerDep, OrgRepoDep, OrgServiceDep
from dos_ingest.service.org_validators import (
    CreatePayloadValidator,
    UpdatePayloadValidator,
)
from fastapi import (
    APIRouter,
    Body,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
)
from fastapi.responses import JSONResponse, Response
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.logbase import CrudApisLogBase

ERROR_MESSAGE_404 = "Organisation not found"
FHIR_MEDIA_TYPE = "application/fhir+json"
ORGANISATION_ID_DESCRIPTION = "The internal id of the organisation"

router = APIRouter()


@router.get(
    "/",
    summary="Get organisation uuid by ods_code or read all organisations",
    response_class=JSONResponse,
)
async def get_handle_organisation_requests(
    request: Request,
    logger: LoggerDep,
    service: OrgServiceDep,
    identifier: Annotated[
        str | None,
        Query(
            description="Organization identifier in format 'odsOrganisationCode|{code}'"
        ),
    ] = None,
) -> JSONResponse:
    """
    Returns a FHIR Bundle of Organisation(s) by ODS code or all if no identifier is provided.
    """
    try:
        service.check_organisation_params(request.query_params)
        if identifier:
            # ods_code = service.extract_ods_code(identifier)
            # TODO: Reintroduce check for valid ODS code format once we have a clear definition of valid formats
            ods_code = identifier.split("|", maxsplit=1)[
                -1
            ]  # Extract ODS code from identifier
            result = service.get_by_ods_code(ods_code)
        else:
            result = service.get_all_organisations()

        organisation_mapper = OrganizationMapper()
        bundle = organisation_mapper.to_fhir_bundle(result)
        return JSONResponse(
            content=bundle.model_dump(mode="json"),
            media_type=FHIR_MEDIA_TYPE,
        )

    except OperationOutcomeException:
        raise

    except Exception as e:
        logger.log(CrudApisLogBase.ORGANISATION_021, error_message=str(e))
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


@router.get("/{organisation_id}", summary="Read a single organisation by id")
def get_organisation_by_id(
    logger: LoggerDep,
    repository: OrgRepoDep,
    organisation_id: Annotated[
        UUID,
        Path(
            examples=["00000000-0000-0000-0000-11111111111"],
            description=ORGANISATION_ID_DESCRIPTION,
        ),
    ],
) -> Organisation:
    logger.log(CrudApisLogBase.ORGANISATION_003, organisation_id=organisation_id)
    organisation = repository.get(organisation_id)

    if not organisation:
        logger.log(
            CrudApisLogBase.ORGANISATION_009,
            organisation_id=organisation_id,
        )
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_404)

    return organisation


@router.put(
    "/{organisation_id}",
    summary="Update an organisation.",
    response_description="OperationOutcome",
)
def update_organisation(
    logger: LoggerDep,
    service: OrgServiceDep,
    organisation_id: Annotated[
        UUID,
        Path(
            examples=["00000000-0000-0000-0000-11111111111"],
            description=ORGANISATION_ID_DESCRIPTION,
        ),
    ],
    update_payload_validator: Annotated[
        UpdatePayloadValidator, Body(media_type=FHIR_MEDIA_TYPE)
    ],
    nhse_product_id: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    logger.log(CrudApisLogBase.ORGANISATION_005, organisation_id=organisation_id)
    try:
        fhir_org = update_payload_validator.model_dump()
        processed = service.process_organisation_update(
            organisation_id=organisation_id,
            fhir_org=fhir_org,
            nhse_product_id=nhse_product_id,
        )
        if not processed:
            logger.log(
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
            logger.log(
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


@router.post("/", summary="Create a new organisation")
def post_organisation(
    logger: LoggerDep,
    service: OrgServiceDep,
    organisation_data: Annotated[
        CreatePayloadValidator,
        Body(
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
    ],
    nhse_product_id: Annotated[str, Header()],
) -> JSONResponse:

    organisation = Organisation(
        **organisation_data.model_dump(exclude="id"),
        id=uuid4(),
        createdBy=AuditEvent(
            type=AuditEventType.app,
            value=nhse_product_id,
            display="CRUD API",
        ),
        lastUpdatedBy=AuditEvent(
            type=AuditEventType.app,
            value=nhse_product_id,
            display="CRUD API",
        ),
    )

    logger.log(
        CrudApisLogBase.ORGANISATION_011,
        ods_code=organisation.identifier_ODS_ODSCode,
    )
    organisation = service.create_organisation(organisation)
    logger.log(
        CrudApisLogBase.ORGANISATION_015,
        ods_code=organisation.identifier_ODS_ODSCode,
        organisation_id=organisation.id,
    )

    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=organisation.model_dump(mode="json"),
        headers={"Location": f"/Organization/{organisation.id}"},
    )


@router.delete("/{organisation_id}", summary="Delete an organisation")
def delete_organisation(
    logger: LoggerDep,
    org_repository: OrgRepoDep,
    organisation_id: Annotated[
        UUID,
        Path(
            ...,
            examples=["00000000-0000-0000-0000-11111111111"],
            description=ORGANISATION_ID_DESCRIPTION,
        ),
    ],
) -> Response:
    logger.log(
        CrudApisLogBase.ORGANISATION_017,
        organisation_id=organisation_id,
    )
    organisation = org_repository.get(organisation_id)

    if not organisation:
        logger.log(
            CrudApisLogBase.ORGANISATION_010,
            organisation_id=organisation_id,
        )
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_404)

    org_repository.delete(organisation_id)
    logger.log(
        CrudApisLogBase.ORGANISATION_018,
        organisation_id=organisation_id,
    )

    return Response(status_code=204, content=None)
