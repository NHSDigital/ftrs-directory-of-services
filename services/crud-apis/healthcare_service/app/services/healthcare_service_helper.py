from ftrs_common.logger import Logger
from ftrs_data_layer.domain import DBModel, HealthcareService
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

crud_healthcareservice_logger = Logger.get(service="crud_healthcareservice_logger")


def create_healthcare_service(
    healthcare_service: HealthcareService, repository: AttributeLevelRepository[DBModel]
) -> HealthcareService:
    crud_healthcareservice_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_001,
        name=healthcare_service.name,
        type=healthcare_service.type,
    )
    repository.create(healthcare_service)
    crud_healthcareservice_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_002, id=healthcare_service.id
    )
    return healthcare_service
