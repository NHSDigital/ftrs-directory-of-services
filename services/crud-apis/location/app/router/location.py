from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Path
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import Location
from starlette.responses import JSONResponse

from location.app.service.location_service import LocationService
from utils.db_service import get_service_repository

# Constants

router = APIRouter()
location_repository = get_service_repository(Location, "location")
location_service_logger = Logger.get(service="crud_location_logger")
location_service = LocationService(
    location_repository=location_repository, logger=location_service_logger
)


@router.get("/{location_id}", summary="Get a location by ID.")
async def get_location_id(
    location_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The UUID of the location",
    ),
) -> Location:
    location_service_logger.log(CrudApisLogBase.LOCATION_006, location_id=location_id)
    return location_service.get_location_by_id(location_id)


@router.get("/", summary="Get all locations.")
async def get_all_locations() -> list[Location]:
    location_service_logger.log(CrudApisLogBase.LOCATION_007)
    return location_service.get_locations()


@router.post("/", summary="Create a new location.")
async def post_location(location: Location) -> JSONResponse:
    """
    Create a new location in the repository.
    """
    location_service_logger.log(
        CrudApisLogBase.LOCATION_001,
        name=location.name,
        orgID=location.managingOrganisation,
    )
    location_service.create_location(location)
    location_service_logger.log(CrudApisLogBase.LOCATION_002, location_id=location.id)
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={
            "message": "Location created successfully",
            "location": location.model_dump(mode="json"),
        },
    )
