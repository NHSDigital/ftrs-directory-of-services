from http import HTTPStatus
from typing import Annotated
from uuid import UUID, uuid4

from dos_ingest.dependencies import HSRepoDep, LoggerDep
from dos_ingest.service.validators import (
    HealthcareServiceCreatePayloadValidator,
)
from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Body
from fastapi.responses import Response
from ftrs_data_layer.domain import HealthcareService
from ftrs_data_layer.domain.base import audit_default_value
from ftrs_data_layer.logbase import CrudApisLogBase
from starlette.responses import JSONResponse

# Constants
ITEMS_PER_PAGE = 10

router = APIRouter()


@router.get("/{service_id}", summary="Get a healthcare service by ID.")
async def get_healthcare_service_id(
    service_id: Annotated[
        UUID,
        Path(
            ...,
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The UUID of the healthcare service",
        ),
    ],
    logger: LoggerDep,
    repository: HSRepoDep,
) -> HealthcareService:
    logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_006,
        service_id=service_id,
    )
    service = repository.get(service_id)
    if not service:
        # If the service is not found, return a 404 response
        logger.log(CrudApisLogBase.HEALTHCARESERVICE_E002, service_id=service_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Healthcare Service not found",
        )

    logger.log(CrudApisLogBase.HEALTHCARESERVICE_008, service=service)
    return service


@router.get("/", summary="Get all healthcare services.")
async def get_all_healthcare_services(
    logger: LoggerDep,
    repository: HSRepoDep,
) -> list[HealthcareService]:
    logger.log(CrudApisLogBase.HEALTHCARESERVICE_007)
    services = list(repository.iter_records(ITEMS_PER_PAGE))
    if not services:
        logger.log(CrudApisLogBase.HEALTHCARESERVICE_E003)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="No healthcare services found",
        )

    logger.log(CrudApisLogBase.HEALTHCARESERVICE_012, length=len(services))
    return services


@router.put(
    "/{service_id}",
    summary="Update a Healthcare Service.",
)
async def update_organisation(
    service_id: Annotated[
        UUID,
        Path(
            ...,
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The internal id of the healthcare service",
        ),
    ],
    payload: Annotated[HealthcareService, Body()],
    logger: LoggerDep,
    repository: HSRepoDep,
) -> JSONResponse:
    logger.log(CrudApisLogBase.HEALTHCARESERVICE_003, service_id=service_id)

    existing_service = repository.get(service_id)
    if not existing_service:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Healthcare Service not found",
        )

    repository.update(service_id, payload)

    logger.log(CrudApisLogBase.HEALTHCARESERVICE_004, service_id=service_id)

    return JSONResponse(
        status_code=200,
        content=payload.model_dump(mode="json"),
    )


@router.delete("/{service_id}", summary="Delete a healthcare service by ID.")
async def delete_healthcare_service(
    service_id: Annotated[
        UUID,
        Path(
            ...,
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The UUID of the healthcare service to delete",
        ),
    ],
    logger: LoggerDep,
    repository: HSRepoDep,
) -> Response:
    logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_009,
        service_id=service_id,
    )
    healthcare_service = repository.get(service_id)
    if not healthcare_service:
        logger.log(CrudApisLogBase.HEALTHCARESERVICE_E002, service_id=service_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Healthcare Service not found",
        )

    repository.delete(service_id)
    logger.log(CrudApisLogBase.HEALTHCARESERVICE_010, service_id=service_id)

    return Response(status_code=HTTPStatus.NO_CONTENT, content=None)


@router.post("/", summary="Create a healthcare service.")
async def post_healthcare_service(
    healthcare_service_data: Annotated[
        HealthcareServiceCreatePayloadValidator,
        Body(
            examples=[
                {
                    "name": "Test Healthcare Service",
                    "type": "General Practice",
                    "identifier_ODS_ODSCode": "12345",
                }
            ],
        ),
    ],
    logger: LoggerDep,
    repository: HSRepoDep,
) -> JSONResponse:
    """
    Create a new healthcare service.
    """
    healthcare_service_data.id = uuid4()  # Assign a new UUID for the healthcare service
    healthcare_service = HealthcareService(
        **healthcare_service_data.model_dump(),
        createdBy=audit_default_value.model_copy(),
        lastUpdatedBy=audit_default_value.model_copy(),
    )

    logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_001,
        name=healthcare_service.name,
        type=healthcare_service.type,
    )
    repository.create(healthcare_service)
    logger.log(CrudApisLogBase.HEALTHCARESERVICE_002, id=healthcare_service.id)

    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=healthcare_service.model_dump(mode="json"),
        headers={"Location": f"/HealthcareService/{healthcare_service.id}"},
    )
