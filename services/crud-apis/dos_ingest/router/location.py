from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from dos_ingest.dependencies import LocRepoDep, LocServiceDep, LoggerDep
from fastapi import APIRouter, HTTPException, Path, Response
from fastapi.params import Body
from ftrs_data_layer.domain import Location
from ftrs_data_layer.logbase import CrudApisLogBase
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/{location_id}", summary="Get a location by ID.")
async def get_location_id(
    logger: LoggerDep,
    service: LocServiceDep,
    location_id: Annotated[
        UUID,
        Path(
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The UUID of the location",
        ),
    ],
) -> Location:
    logger.log(CrudApisLogBase.LOCATION_006, location_id=location_id)
    return service.get_location_by_id(location_id)


@router.get("/", summary="Get all locations.")
async def get_all_locations(
    logger: LoggerDep,
    service: LocServiceDep,
) -> list[Location]:
    logger.log(CrudApisLogBase.LOCATION_007)
    return service.get_locations()


@router.post("/", summary="Create a new location.")
async def post_location(
    location: Location,
    logger: LoggerDep,
    service: LocServiceDep,
) -> JSONResponse:
    """
    Create a new location in the repository.
    """
    logger.log(
        CrudApisLogBase.LOCATION_001,
        name=location.name,
        orgID=location.managingOrganisation,
    )
    service.create_location(location)
    logger.log(CrudApisLogBase.LOCATION_002, location_id=location.id)

    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=location.model_dump(mode="json"),
        headers={"Location": f"/Location/{location.id}"},
    )


@router.delete("/{location_id}", summary="Delete a location by ID.")
async def delete_location(
    location_id: Annotated[
        UUID,
        Path(
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The UUID of the location to delete",
        ),
    ],
    logger: LoggerDep,
    repository: LocRepoDep,
) -> Response:
    logger.log(
        CrudApisLogBase.LOCATION_008,
        location_id=location_id,
    )
    location = repository.get(location_id)
    if not location:
        logger.log(CrudApisLogBase.LOCATION_E001, location_id=location_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Location not found",
        )

    repository.delete(location_id)
    logger.log(CrudApisLogBase.LOCATION_009, location_id=location_id)
    return Response(status_code=HTTPStatus.NO_CONTENT, content=None)


@router.put(
    "/{location_id}",
    summary="Update a Location.",
)
async def update_location(
    location_id: Annotated[
        UUID,
        Path(
            ...,
            examples=["00000000-0000-0000-0000-11111111111"],
            description="The internal id of the location",
        ),
    ],
    payload: Annotated[Location, Body()],
    logger: LoggerDep,
    repository: LocRepoDep,
) -> JSONResponse:
    logger.log(CrudApisLogBase.LOCATION_010, location_id=location_id)

    repository.update(location_id, payload)
    logger.log(CrudApisLogBase.LOCATION_011, location_id=location_id)

    return JSONResponse(
        status_code=200,
        content=payload.model_dump(mode="json"),
        headers={"Location": f"/Location/{location_id}"},
    )
