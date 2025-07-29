from datetime import UTC, datetime

from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import DBModel, HealthcareService
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


def get_outdated_fields(
    healthcare_service: HealthcareService, payload: HealthcareService
) -> dict:
    return {
        field: value
        for field, value in payload.model_dump().items()
        if (
            (
                field == "modified_by"
                and getattr(healthcare_service, "modifiedBy", None) != value
            )
            or (
                field != "modified_by"
                and getattr(healthcare_service, field, None) != value
            )
        )
    }


def apply_updates(
    existing_service: HealthcareService, outdated_fields: dict
) -> HealthcareService:
    crud_healthcareservice_logger.log(
        CrudApisLogBase.HEALTHCARESERVICE_007,
        service_id=existing_service.id,
    )
    for field, value in outdated_fields.items():
        if field == "modified_by":
            setattr(existing_service, "modifiedBy", value)
        else:
            setattr(existing_service, field, value)
    existing_service.modifiedDateTime = datetime.now(UTC)
