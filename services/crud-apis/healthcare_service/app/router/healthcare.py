import logging
from http import HTTPStatus
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Body
from fastapi.responses import Response
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import HealthcareService
from starlette.responses import JSONResponse

from healthcare_service.app.services.healthcare_service_helper import (
    apply_updates,
    create_healthcare_service,
    get_outdated_fields,
)
from healthcare_service.app.services.validators import (
    HealthcareServiceCreatePayloadValidator,
)

# Constants
ITEMS_PER_PAGE = 10
ERROR_MESSAGE_404 = "Healthcare Service not found"

router = APIRouter()
repository = get_service_repository(HealthcareService, "healthcare-service")
crud_healthcare_logger = Logger.get(service="crud_healthcare_logger")


@router.get("/{service_id}", summary="Get a healthcare service by ID.")
async def get_healthcare_service_id(
    service_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The UUID of the healthcare service",
    ),
) -> HealthcareService:
    logging.info(f"Getting healthCare service with ID: {service_id}")
    return get_healthcare_service_by_id(service_id)


@router.get("/", summary="Get all healthcare services.")
async def get_all_healthcare_services() -> list[HealthcareService]:
    logging.info("Getting all healthcare services")
    return get_healthcare_services()


def get_healthcare_service_by_id(service_id: str) -> HealthcareService:
    try:
        service = repository.get(service_id)
        if not service:
            # If the service is not found, return a 404 response
            logging.error(f"Healthcare Service with ID {service_id} not found")
            return raise_http_exception(
                HTTPStatus.NOT_FOUND, "Healthcare Service not found"
            )
        else:
            logging.info(f"Healthcare Service found: {service}")
            return service
    except Exception as e:
        return raise_http_exception_if_not_found(e)


# Update Healthcare Service
@router.put(
    "/{service_id}",
    summary="Update a Healthcare Service.",
)
def update_organisation(
    service_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The internal id of the healthcare service",
    ),
    payload: HealthcareService = Body(...),
) -> JSONResponse:
    crud_healthcare_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_003,
        service_id=service_id,
    )
    service = repository.get(service_id)

    if not service:
        logging.error(f"Healthcare service with ID {service_id} not found.")
        raise HTTPException(status_code=404, detail=ERROR_MESSAGE_404)

    outdated_fields = get_outdated_fields(service, payload)
    crud_healthcare_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_004,
        outdated_fields=outdated_fields,
        service_id=service_id,
    )

    if not outdated_fields:
        crud_healthcare_logger.log(
            CrudApisLogBase.HEALTHCARESERVICE_005,
            service_id=service_id,
        )
        return JSONResponse(status_code=200, content={"message": "No changes detected"})

    apply_updates(service, outdated_fields)
    repository.update(id, service)
    crud_healthcare_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_006,
        service_id=service_id,
    )

    return JSONResponse(
        status_code=200, content={"message": "Data processed successfully"}
    )


@router.delete("/{service_id}", summary="Delete a healthcare service by ID.")
async def delete_healthcare_service(
    service_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The UUID of the healthcare service to delete",
    ),
) -> Response:
    logging.info(f"Deleting healthcare service with ID: {service_id}")
    healthcareService = repository.get(service_id)
    if not healthcareService:
        logging.error(f"Healthcare Service with ID {service_id} not found")
        return raise_http_exception(
            HTTPStatus.NOT_FOUND, "No healthcare services found"
        )

    repository.delete(service_id)
    logging.info(f"Healthcare Service with ID {service_id} deleted successfully")
    return Response(status_code=HTTPStatus.NO_CONTENT, content=None)


@router.post("/", summary="Create a healthcare service.")
async def post_healthcare_service(
    healthcare_service_data: HealthcareServiceCreatePayloadValidator = Body(
        ...,
        examples=[
            {
                "name": "Test Healthcare Service",
                "type": "General Practice",
                "identifier_ODS_ODSCode": "12345",
            }
        ],
    ),
) -> JSONResponse:
    """
    Create a new healthcare service.
    """
    healthcare_service_data.id = uuid4()  # Assign a new UUID for the healthcare service
    healthcare_service = HealthcareService(**healthcare_service_data.model_dump())

    created_healthcare_service = create_healthcare_service(
        healthcare_service, repository
    )
    logging.info(
        f"Healthcare Service created successfully: {created_healthcare_service}"
    )
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={
            "message": "Healthcare Service created successfully",
            "healthcare_service": created_healthcare_service.model_dump(mode="json"),
        },
    )


def get_healthcare_services() -> list[HealthcareService]:
    try:
        services = list(repository.iter_records(ITEMS_PER_PAGE))
        if not services:
            logging.error("No healthcare services found")
            return raise_http_exception(
                HTTPStatus.NOT_FOUND, "No healthcare services found"
            )
        else:
            logging.info(f"Found {len(services)} healthcare services")
            return services

    except Exception as e:
        return raise_http_exception_if_not_found(e)


def raise_http_exception_if_not_found(exception: Exception) -> None:
    """
    Raise an HTTPException if the exception is a 404 Not Found error.
    Otherwise, log the error and raise a generic 500 Internal Server Error.
    """
    if (
        isinstance(exception, HTTPException)
        and exception.status_code == HTTPStatus.NOT_FOUND
    ):
        # If the exception is already an HTTPException, re-raise it
        raise exception
    else:
        logging.exception("Error fetching healthcare services:")
        raise_http_exception(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to fetch healthcare services"
        )


def raise_http_exception(status_code: int, detail: str) -> None:
    logging.error(detail)
    raise HTTPException(status_code=status_code, detail=detail)
