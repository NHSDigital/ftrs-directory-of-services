from typing import Annotated

from dos_ingest.service.location_service import LocationService
from dos_ingest.service.organisation_service import OrganisationService
from fastapi import Depends
from ftrs_common.logger import Logger
from ftrs_common.utils.config import Settings
from ftrs_common.utils.db_service import get_service_repository
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.repository.dynamodb.attribute_level import AttributeLevelRepository


async def settings_dependency() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(settings_dependency)]


async def logger_dependency() -> Logger:
    return Logger.get(service="crud_location_logger")


LoggerDep = Annotated[Logger, Depends(logger_dependency)]


async def org_repo_dependency(
    settings: SettingsDep,
) -> AttributeLevelRepository[Organisation]:
    """Dependency function to provide an instance of OrganisationRepository."""
    return get_service_repository(
        Organisation,
        "organisation",
        endpoint_url=settings.endpoint_url,
    )


OrgRepoDep = Annotated[
    AttributeLevelRepository[Organisation], Depends(org_repo_dependency)
]


async def org_service_dependency(
    org_repo: OrgRepoDep,
    logger: LoggerDep,
) -> OrganisationService:
    """Dependency function to provide an instance of OrganisationService."""
    return OrganisationService(org_repository=org_repo, logger=logger)


OrgServiceDep = Annotated[OrganisationService, Depends(org_service_dependency)]


async def loc_repo_dependency(
    settings: SettingsDep,
) -> AttributeLevelRepository[Location]:
    """Dependency function to provide an instance of the location repository."""
    return get_service_repository(
        Location,
        "location",
        endpoint_url=settings.endpoint_url,
    )


LocRepoDep = Annotated[AttributeLevelRepository[Location], Depends(loc_repo_dependency)]


async def loc_service_dependency(
    loc_repo: LocRepoDep,
    logger: LoggerDep,
) -> LocationService:
    """Dependency function to provide an instance of LocationService."""
    return LocationService(location_repository=loc_repo, logger=logger)


LocServiceDep = Annotated[LocationService, Depends(loc_service_dependency)]


async def hs_repo_dependency(
    settings: SettingsDep,
) -> AttributeLevelRepository[Location]:
    """Dependency function to provide an instance of the healthcare-service repository."""
    return get_service_repository(
        HealthcareService,
        "healthcare-service",
        endpoint_url=settings.endpoint_url,
    )


HSRepoDep = Annotated[
    AttributeLevelRepository[HealthcareService], Depends(hs_repo_dependency)
]
