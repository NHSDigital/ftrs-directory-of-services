import logging
from http import HTTPStatus
from uuid import uuid4

from fastapi import HTTPException
from ftrs_common.logger import Logger
from ftrs_data_layer.domain import Location
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

ITEMS_PER_PAGE = 10


class LocationService:
    def __init__(
        self,
        location_repository: AttributeLevelRepository[Location],
        logger: logging.Logger | None = None,
    ) -> None:
        self.location_repository = location_repository
        self.logger = logger or Logger.get(service="crud_location_logger")

    def get_location_by_id(self, location_id: str) -> Location:
        location = self.location_repository.get(location_id)
        if not location:
            # If the location is not found, return a 404 response
            self.logger.log(
                CrudApisLogBase.LOCATION_E001,
                location_id=location_id,
            )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Location not found",
            )
        else:
            self.logger.log(CrudApisLogBase.LOCATION_003, location_id=location_id)
            return location

    def get_locations(self) -> list[Location]:
        locations = list(self.location_repository.iter_records(ITEMS_PER_PAGE))
        if not locations:
            self.logger.log(
                CrudApisLogBase.LOCATION_E002,
            )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="No locations found",
            )
        else:
            self.logger.log(CrudApisLogBase.LOCATION_004, count=len(locations))
            return locations

    def create_location(self, location: Location) -> Location:
        """
        Create a new location in the repository.
        """

        location.id = uuid4()  # Assign a new UUID if not/is provided
        self.logger.log(
            CrudApisLogBase.LOCATION_005,
            location_id=location.id,
        )
        self.location_repository.create(location)
        self.logger.log(
            CrudApisLogBase.LOCATION_002,
            location_id=location.id,
        )
        return location
