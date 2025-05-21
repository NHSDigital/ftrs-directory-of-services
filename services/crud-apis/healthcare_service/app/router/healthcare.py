import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from ftrs_data_layer.models import HealthcareService
from utils.db_service import get_service_repository

# Constants
ITEMS_PER_PAGE = 10

router = APIRouter()


@router.get("/{service_id}", summary="Get a healthcare service by ID.")
async def get_healthcare_service_id(
    service_id: Optional[str] = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The UUID of the healthcare service",
    ),
) -> JSONResponse:
    logging.info(f"Getting healthCare service with ID: {service_id}")
    return get_healthcare_service_by_id(service_id)


@router.get("/", summary="Get all healthcare services.")
async def get_all_healthcare_services() -> JSONResponse:
    logging.info("Getting all healthcare services")
    # Call the repository to get all healthcare services
    return get_service_repository(HealthcareService, "healthcare-service").find(
        ITEMS_PER_PAGE
    )


def get_healthcare_service_by_id(service_id: str) -> JSONResponse:
    try:
        UUID(service_id)  # Validate UUID format
        service = get_service_repository(HealthcareService, "healthcare-service").get(
            service_id
        )
        if service:
            return service
        else:
            # If the service is not found, return a 404 response
            logging.error(f"Healthcare Service with ID {service_id} not found")
            return JSONResponse(
                status_code=404, content={"message": "Healthcare Service not found"}
            )
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid service_id format. Must be a valid UUID"
        )
