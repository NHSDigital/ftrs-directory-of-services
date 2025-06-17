from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from ftrs_data_layer.models import DBModel, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from organisations.app.services.validators import UpdatePayloadValidator

crud_organisation_logger = Logger.get(service="crud_organisation_logger")


def get_outdated_fields(
    organisation: Organisation, payload: UpdatePayloadValidator
) -> dict:
    return {
        field: value
        for field, value in payload.model_dump().items()
        if (
            (
                field == "modified_by"
                and getattr(organisation, "modifiedBy", None) != value
            )
            or (field != "modified_by" and getattr(organisation, field, None) != value)
        )
    }


def apply_updates(
    existing_organisation: Organisation, outdated_fields: dict
) -> Organisation:
    crud_organisation_logger.log(
        CrudApisLogBase.ORGANISATION_009,
        organisation_id=existing_organisation.id,
    )
    for field, value in outdated_fields.items():
        if field == "modified_by":
            setattr(existing_organisation, "modifiedBy", value)
        else:
            setattr(existing_organisation, field, value)
    existing_organisation.modifiedDateTime = datetime.now(UTC)


def create_organisation(
    organisation: Organisation, org_repository: AttributeLevelRepository[DBModel]
) -> Organisation:
    # Check if the ODS code is provided, if not, then we log it and raise an error
    if not organisation.identifier_ODS_ODSCode:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_012,
            ods_code=organisation.identifier_ODS_ODSCode,
        )
        raise HTTPException(status_code=400, detail="ODS code is required")

    # if the organisation already exists, we log it and raise an error
    existing_organisation = org_repository.get_by_ods_code(
        organisation.identifier_ODS_ODSCode
    )
    if existing_organisation:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_013,
            ods_code=organisation.identifier_ODS_ODSCode,
        )
        raise HTTPException(
            status_code=409, detail="Organisation with this ODS code already exists"
        )
    # If the organisation already has an ID, we log it and generate a new one
    if organisation.id is not None:
        crud_organisation_logger.log(
            CrudApisLogBase.ORGANISATION_014,
            organisation_id=organisation.id,
        )
        organisation.id = uuid4()
    org_repository.create(organisation)
    return organisation
