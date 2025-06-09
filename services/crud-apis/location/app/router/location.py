import logging
from http import HTTPStatus
from typing import NoReturn
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path
from ftrs_data_layer.models import Location

from utils.db_service import get_service_repository

# Constants
ITEMS_PER_PAGE = 10

router = APIRouter()
repository = get_service_repository(Location, "location")


@router.get("/{location_id}", summary="Get a location by ID.")
async def get_location_id(
    location_id: UUID = Path(
        ...,
        examples=["00000000-0000-0000-0000-11111111111"],
        description="The UUID of the location",
    ),
) -> Location:
    logging.info(f"Getting location with ID: {location_id}")
    return get_location_by_id(location_id)


@router.get("/", summary="Get all locations.")
async def get_all_locations() -> list[Location]:
    logging.info("Getting all locations")
    return get_locations()


def get_location_by_id(location_id: str) -> Location:
    try:
        location = repository.get(location_id)
        if not location:
            # If the location is not found, return a 404 response
            logging.error(f"Location with ID {location_id} not found")
            return raise_http_exception(HTTPStatus.NOT_FOUND, "Location not found")

        logging.info(f"Location found: {location}")
        return location  # noqa: TRY300
    except Exception as e:
        return raise_http_exception_if_not_found(e)


def get_locations() -> list[Location]:
    try:
        locations = list(repository.iter_records(ITEMS_PER_PAGE))
        if not locations:
            logging.error("No locations found")
            return raise_http_exception(HTTPStatus.NOT_FOUND, "No locations found")
        logging.info(f"Found {len(locations)} locations")
        return locations  # noqa: TRY300

    except Exception as e:
        return raise_http_exception_if_not_found(e)


def raise_http_exception_if_not_found(exception: Exception) -> NoReturn:
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
        logging.exception("Error fetching locations:")
        raise_http_exception(
            HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to fetch locations"
        )


def raise_http_exception(status_code: int, detail: str) -> NoReturn:
    logging.error(detail)
    raise HTTPException(status_code=status_code, detail=detail)
